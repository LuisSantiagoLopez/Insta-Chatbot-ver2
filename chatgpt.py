import openai
import time

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
          
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are an Instagram content creator for this client's Instagram: '{variables['program_description']}' with this target audience: '{variables['target_segment']}'. Help them execute a variety of tasks related to their Instagram content marketing."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response['choices'][0]['message']['content']

    except openai.error.RateLimitError as e:
        # Retry the request after a delay
        print(f"RateLimitError: {e}")
        print("Retrying after 5 seconds...")
        time.sleep(5)
        return chatgpt(conn, c, user_id, user_input, prompt, temperature, model)

    except openai.error.ServiceUnavailableError as e:
        # Retry the request after a delay
        print(f"ServiceUnavailableError: {e}")
        print("Retrying after 5 seconds...")
        time.sleep(5)
        return chatgpt(conn, c, user_id, user_input, prompt, temperature, model)
  