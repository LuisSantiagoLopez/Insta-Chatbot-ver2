import sqlite3
import json
from decision_tree import decision_tree

user_id = input("Enter your name: ")
conn = sqlite3.connect('decision_tree.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tree
             (user_id TEXT, function TEXT, parameter TEXT, value TEXT, PRIMARY KEY(user_id, function, parameter))''')

c.execute('''CREATE TABLE IF NOT EXISTS news 
             (user_id TEXT, title TEXT, PRIMARY KEY(user_id, title))''')


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
            # Get value either from results dictionary or, if not present there, from the database
#            if param in results:
#                value = results[param]          
#            else:
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
        result = func(conn, c, user_id, user_input, **parameter_values)

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

"""
Enter target_segment: lower income workers that distrust of insurance companies
Enter program_description: beesure is an insurtech that sells affordable digital insurance
"""