import json

def create_caption(conn, c, user_id, user_input, idea):
    idea = json.loads(idea)
    return {"caption":idea['Caption']}