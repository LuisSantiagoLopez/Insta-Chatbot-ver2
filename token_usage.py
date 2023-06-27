token_usage = {
    "total_tokens": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_images": 0,
    "total_searches": 0,
    "total_cost": 0,
}

def token_usage_f(conn, c, user_id):
    global token_usage
    # Create a table with a column for each field in token_usage
    c.execute('''CREATE TABLE IF NOT EXISTS tokens
                 (user_id TEXT PRIMARY KEY, total_tokens INTEGER, prompt_tokens INTEGER, completion_tokens INTEGER, total_images INTEGER, total_searches INTEGER, total_cost REAL)''')

    # Retrieve the token usage for the user
    c.execute("SELECT total_tokens, prompt_tokens, completion_tokens, total_images, total_searches, total_cost FROM tokens WHERE user_id=?", (user_id,))

    db_result = c.fetchone()

    if db_result is not None:
        # Update the token_usage dictionary with the values from the database
        token_usage = {
            "total_tokens": db_result[0],
            "prompt_tokens": db_result[1],
            "completion_tokens": db_result[2],
            "total_images": db_result[3],
            "total_searches": db_result[4],
            "total_cost": db_result[5]
        }
        
    return token_usage