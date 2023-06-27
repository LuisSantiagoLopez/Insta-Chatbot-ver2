from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks import get_openai_callback
from token_usage import token_usage

variables = {}
conversations = []
def chatgptlc(conn, c, user_id, user_input, prompt, temperature, model="gpt-3.5-turbo"):
    c.execute('CREATE TABLE IF NOT EXISTS conversations (user_id TEXT, prompt TEXT, output TEXT)')
    
    params_needed = ["target_segment", "program_description"]
    
    for param in params_needed:
        c.execute("SELECT value FROM tree WHERE user_id=? AND parameter=?", (user_id, param))
        parameter_value = c.fetchone()
        variables[param] = parameter_value
  
    system_message_template = f"You are a helpful instagram content creator for this client's instagram: '{variables['program_description']}' with this target audience: '{variables['target_segment']}'. Help them execute a variety of tasks related with their instagram content marketing."

    chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_message_template),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

    chat = ChatOpenAI(temperature=0.5, model=model)
    memory = ConversationBufferWindowMemory(k=5, return_messages=True)
  
    # Fetch past conversation from the database
    c.execute("SELECT prompt, output FROM conversations WHERE user_id=?", (user_id,))
    conversation_history = c.fetchall()

    # Add past conversation to memory
    for conversation in conversation_history:
        input = conversation[0]
        output = conversation[1]
        conversations.append({"input": input})
        conversations.append({"output": output})
        memory.save_context({"input": input}, {"output": output})
  
    conversation = ConversationChain(
    llm=chat,
    prompt=chat_prompt,
    memory=memory,
    verbose=True
    )

    #This second chain handles non-memory requests 
    system_template = system_message_template
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt_2 = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    secondary_chain = LLMChain(
    llm=chat,
    prompt=chat_prompt_2,
    )
  
    # Get the AI response
    with get_openai_callback() as cb:
        if prompt[0] == "1":
            response = secondary_chain.run(text=prompt)
        else:
            response = conversation.predict(input=prompt)
            c.execute('INSERT INTO conversations (user_id, prompt, output) VALUES (?, ?, ?)', (user_id, prompt, response))
      
        # Assign each statement to a variable
        total_tokens = cb.total_tokens
        prompt_tokens = cb.prompt_tokens
        completion_tokens = cb.completion_tokens
        total_cost = cb.total_cost

        # Add the values to the totals dictionary
        token_usage["total_tokens"] += total_tokens
        token_usage["prompt_tokens"] += prompt_tokens
        token_usage["completion_tokens"] += completion_tokens
        token_usage["total_cost"] += total_cost

    conn.commit()
    
    return response