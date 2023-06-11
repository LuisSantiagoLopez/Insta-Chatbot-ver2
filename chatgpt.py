import openai

variables = {}  
def chatgpt(conn, c, user_id, user_input, prompt, temperature, model="gpt-3.5-turbo"):
    
    params_needed = ["target_segment", "program_description"]
    
    for param in params_needed:
        if variables.get(param) is None:
            c.execute("SELECT value FROM tree WHERE user_id=? AND parameter=?", (user_id, param))
            parameter_value = c.fetchone()
            variables[param] = parameter_value
        else:
          continue

    response = openai.ChatCompletion.create(
    model=model,
    messages=[{"role": "system", "content": f"You are an instagram content creator for this client's instagram: '{variables['program_description']}'\
        with this target audience: '{variables['target_segment']}'. Help them execute a variety of tasks related with their instagram content marketing."}, 
    {"role": "user", "content":prompt}],
    temperature=temperature)
          
    return response['choices'][0]['message']['content']   