from langchain.models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import SystemMessagePromptTemplate

variables = {}
def chatgpt(conn, c, user_id, user_input, prompt, temperature, model="gpt-3.5-turbo"):
    c.execute('CREATE TABLE IF NOT EXISTS conversations (user_id TEXT, prompt TEXT, output TEXT)')
    
    params_needed = ["target_segment", "program_description"]
    
    for param in params_needed:
        c.execute("SELECT value FROM tree WHERE user_id=? AND parameter=?", (user_id, param))
        parameter_value = c.fetchone()
        variables[param] = parameter_value

    llm = ChatOpenAI(temperature=0.5, model="gpt-4")
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=200)
    chain = ConversationChain(
        llm=llm, 
        memory = memory,
        verbose=True
    )

    system_message_template = "You are an instagram content creator for this client's instagram: '{variables['program_description']}' with this target audience: '{variables['target_segment']}'. Help them execute a variety of tasks related with their instagram content marketing."
  
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)

    formatted_system_message_prompt = system_message_prompt.format(target_segment=variables['target_segment'], program_description=variables['program_description'])

    chain.system_message = formatted_system_message_prompt
  
    # Fetch past conversation from the database
    c.execute("SELECT prompt, output FROM conversations WHERE user_id=?", (user_id,))
    conversation_history = c.fetchall()

    # Add past conversation to memory
    for conversation in conversation_history:
        memory.save_context({"input": conversation[0]}, {"output": conversation[1]})
  
    # Get the AI response
    response = chain.run(user_input)
    
    # Save the prompt and output to the database
    c.execute('INSERT INTO conversations (user_id, prompt, output) VALUES (?, ?, ?)', (user_id, user_input, response))
    conn.commit()
  
    return response