import sqlite3
import json
from decision_tree import decision_tree
from token_usage import token_usage_f
import pandas as pd
import os

user_id = input("Enter your name: ")
conn = sqlite3.connect('decision_tree.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tree
             (user_id TEXT, function TEXT, parameter TEXT, value TEXT, PRIMARY KEY(user_id, function, parameter))''')

c.execute('''CREATE TABLE IF NOT EXISTS news 
             (user_id TEXT, title TEXT, PRIMARY KEY(user_id, title))''')

def update_token_usage(conn, c, user_id, token_usage):
    # Update the tokens table with the new values of token_usage
    c.execute("""
        UPDATE tokens 
        SET total_tokens = ?, prompt_tokens = ?, completion_tokens = ?, 
            total_images = ?, total_searches = ?, total_cost = ? 
        WHERE user_id = ?""",
        (token_usage["total_tokens"], token_usage["prompt_tokens"], 
         token_usage["completion_tokens"], token_usage["total_images"], 
         token_usage["total_searches"], token_usage["total_cost"], user_id))
    conn.commit()

def compile_token_costs(conn, c, user_id, user_input, func, **parameter_values):
    # Initialize the table
    table = {"User": [], "Function": [], "Cost": [], "Total Cost": []}

    # Initialize the previous total cost
    prev_total_cost = token_usage_f(conn, c, user_id)["total_cost"]

    # Perform the function
    result = func(conn, c, user_id, user_input, **parameter_values)

    # Get the updated token usage
    token_usage = token_usage_f(conn, c, user_id)

    update_token_usage(conn, c, user_id, token_usage)

    # Calculate the cost of the function
    function_cost = token_usage["total_cost"] - prev_total_cost

    # Add the user ID to the table
    table["User"].append(user_id)

    # Add the function name to the table
    table["Function"].append(f"{func}")

    # Add the function cost to the table
    table["Cost"].append(function_cost)

    table["Total Cost"].append(token_usage["total_cost"])

    # Convert the table to a DataFrame
    df = pd.DataFrame(table)

    # If the CSV file doesn't exist, create it and write the header
    if not os.path.isfile(f"{user_id}_token_costs.csv"):
        df.to_csv(f"{user_id}_token_costs.csv", index=False)
    else:  # else it exists so append without writing the header
        df.to_csv(f"{user_id}_token_costs.csv", mode='a', header=False, index=False)

    return result

def store_dictionary_results(result):
    # If function returns a dictionary with results, update the results dictionary and the database
    if isinstance(result, dict):
        for key, value in result.items():
            value = json.dumps(value)
            results[key] = value
            c.execute("REPLACE INTO tree (user_id, function, parameter, value) VALUES (?, ?, ?, ?)", (user_id, user_input, key, value))

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
            c.execute("SELECT value FROM tree WHERE user_id=? AND parameter=?", (user_id, param))
            db_result = c.fetchone()
            
            if db_result is None:
                value = input(f"Enter {param}: ") 
                c.execute("REPLACE INTO tree (user_id, function, parameter, value) VALUES (?, ?, ?, ?)",(user_id, user_input, param, value))

            else:
              value = db_result[0]
          
            parameter_values[param] = value
            results[param] = value

        # We call the function with the collected parameters and store the result
        result = compile_token_costs(conn, c, user_id, user_input, func, **parameter_values)

        if user_input not in ["create idea", "normalize idea", "manipulate idea"]:
            store_dictionary_results(result)

        # Commit changes to the database.
        conn.commit()
      
        # Finally, we print the result of the function call.
        print(result)
      
    else:
         print("Invalid input.")

# Close the connection to the database when we're done.
conn.close()