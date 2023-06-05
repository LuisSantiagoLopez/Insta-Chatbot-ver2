import sqlite3
import create_caption, create_idea, create_image, upload_instagram

def chatgpt(prompt, temperature)
    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "system", "content": "You are an instagram content creator."}, 
              {"role": "user", "content":prompt}],
    temperature=temperature)
    return 

def store_dictionary_results(result):
    # If function returns a dictionary with results, update the results dictionary and the database
    if isinstance(result, dict):
        for key, value in result.items():
            results[key] = value
            c.execute("REPLACE INTO tree (user_id, function, parameter, value) VALUES (?, ?, ?, ?)", (user_id, user_input, key, value))

user_id = input("Enter your name: ")

# Connect to SQLite database. This will create the database if it doesn't exist.
conn = sqlite3.connect('decision_tree.db')
c = conn.cursor()

# Create table for storing parameters and results. This will not recreate the table if it already exists.
c.execute('''CREATE TABLE IF NOT EXISTS tree
             (user_id TEXT, function TEXT, parameter TEXT, value TEXT, PRIMARY KEY(user_id, function, parameter))''')

# Here we define a dictionary mapping user commands to the respective functions and their parameters.
decision_tree = {
    "create idea": (create_idea.create_idea, ["target_segment", "program_description"]),
    "normalize idea": (create_idea.normalize_idea, ["user_idea", "target_segment", "program_description"]),
    "manipulate idea": (create_idea.manipulate_idea, ["idea"]),
    "create image": (create_image.create_image, ["idea"]),
    "create caption": (create_caption.create_caption, ["idea", "image_prompt", "target_segment", "program_description"]),
    "upload instagram": (upload_instagram.upload_instagram, ["image_url", "caption"])
}

# Dictionary for storing results of functions
results = {}

# We start an infinite loop to continuously take user inputs.
while True:
    user_input = input("Enter your input: ")

    # We try to get the function and the parameter list from the decision tree for the user's input.
    func, params = decision_tree.get(user_input, (None, None))

    # We check if the function exists in the decision tree. If it does, we proceed.
    if func:
      
        parameter_values={}
      
        for param in params:
            # Get value either from results dictionary or, if not present there, from the database
            if param in results:
                value = results[param]
              
            else:
                c.execute("SELECT value FROM tree WHERE user_id=? AND function=? AND parameter=?", (user_id, user_input, param))
                db_result = c.fetchone()
                print("DB Result for param", param, ":", db_result) # Debug print
                value = db_result
            
                if db_result is None:
                    value = input(f"Enter {param}: ") 
                    c.execute("REPLACE INTO tree (user_id, function, parameter, value) VALUES (?, ?, ?, ?)",(user_id, user_input, param, value))
          
            parameter_values[param] = value
            results[param] = value

        # We call the function with the collected parameters and store the result.
        if user_input in ["create idea", "normalize idea", "manipulate idea", "find topic"]:
            result = func(conn, c, user_id, user_input, **parameter_values)
            store_dictionary_results(result)
        else:
            result = func(**parameter_values)
            store_dictionary_results(result)

        # Commit changes to the database.
        conn.commit()

        # Finally, we print the result of the function call.
        print(result)
      
    else:
         print("Invalid input.")

# Close the connection to the database when we're done.
conn.close()

"""
luissantiago
create idea
28-45 year olds searching to grow their business through AI.
MARS is an automatic social media marketing agency dedicated to bringing results at a lower price
create image
create caption
upload instagram
"""

"""
Cosas que le quiero añadir:
1. Tomar curso de Prompt Engineering de ChatGPT para mejorar la calidad de los outputs 
2. Dejar que el usuario agregue su página web para entender más sobre su programa (SERP-API)
3. Que la función de ideas tenga acceso a tendencias 
4. Conectarse con MidJourney a través de Discord
5. Guardar las (ideas / prompts / captions) que el usuario decidió subir en su base de datos dentro de cada función. 
6. Que el programa pueda retraer las métricas y aplicarlas en el siguiente post
"""