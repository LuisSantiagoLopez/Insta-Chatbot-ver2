from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory

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
        print(input, output)
        conversations.append({"input": input})
        conversations.append({"output": output})
        memory.save_context({"input": input}, {"output": output})
    else:
        print("No conversation history")

    print("MEMORY:", memory.load_memory_variables({}))
  
    conversation = ConversationChain(
    llm=chat,
    prompt=chat_prompt,
    memory=memory,
    verbose=True
    )
  
    # Get the AI response
    response = conversation.predict(input=prompt)
    print("response", response)
    
    # Save the prompt and output to the database
    c.execute('INSERT INTO conversations (user_id, prompt, output) VALUES (?, ?, ?)', (user_id, prompt, response))
    conn.commit()
  
    return response