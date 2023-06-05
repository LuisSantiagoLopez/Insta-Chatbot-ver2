from main import chatgpt
import requests
import sqlite3
import json
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from config import SERP_API_KEY

def replace_idea(conn, c, user_id, user_input, idea):
    # Insert the new 'idea' into the database, replacing any existing 'idea' for the current user and function
    c.execute("REPLACE INTO tree (user_id, function, parameter, value) VALUES (?, ?, ?, ?)", 
              (user_id, user_input, 'idea', idea))
    conn.commit()

def create_idea(conn, c, user_id, user_input, target_segment, program_description):
    c.execute('''CREATE TABLE IF NOT EXISTS news (user_id TEXT, title TEXT)''')
    # 1. Let ChatGPT find 10 keywords related to the data the user provided
    prompt = f"Considering the user's program description: '{program_description}' and their target audience: '{target_segment}' find 3 relevant keywords they could go trending with on social media. Only output a list of keywords separated by commas and nothing else."
    response = chatgpt(prompt, 0.5)
  
    keywords = response['choices'][0]['message']['content']
    print(keywords)

    # 2. Search each keyword in the Google Trends API and choose the most searched
    trends_search = GoogleSearch({"q": keywords, 
                                  "engine": "google_trends",
                                  "date": "now 1-d",
                                  "api_key": SERP_API_KEY})
  
    trends_results = trends_search.get_dict()

    # Find the entry with the latest timestamp
    latest_entry = max(trends_results["interest_over_time"]["timeline_data"], key=lambda x: int(x['timestamp']))

    # Retrieve the values from the latest entry
    values = latest_entry['values']

    # Sort keywords based on their values in descending order
    sorted_keywords = sorted(values, key=lambda x: int(x['value']), reverse=True)[:1]

    for keyword_results in sorted_keywords:
        keyword = keyword_results['query']
        # Search the keywords in the Google News API and with ChatGPT choose the most relevant news for the user by keyword
        news_search = GoogleSearch({"q": keyword, "tbm": "nws", "api_key": SERP_API_KEY})
        news_results = news_search.get_dict()['news_results']

        relevant_news = {}
        for news in news_results:
            c.execute("SELECT title FROM news WHERE user_id=? AND title=?", (user_id, news['title']))
            db_result = c.fetchone()
            
            if db_result is None:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Considering the user's program description: '{program_description}' and their target audience: '{target_segment}', Is this news relevant to them? {news['title']}. Only output a 'Yes.' or a 'No.' answer."}
                    ]
          )
            
                if response['choices'][0]['message']['content'].lower() == 'yes.':
                    relevant_news[news['title']] = news['link']
            else:
              continue
    
        # 4. Get the entire news with the Python requests library and deliver it to ChatGPT
        news_contents = {}
        for title, link in relevant_news.items():
            response = requests.get(link)
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the specific elements that contain the written portion of the article
            paragraphs = soup.find_all('p')
            # Extract the text from the first three paragraphs
            first_five_paragraphs = ""
            for i, paragraph in enumerate(paragraphs):
                if i >= 5:  # Limit to the first three paragraphs
                    break
                paragraph_text = paragraph.get_text().strip()
                first_five_paragraphs += paragraph_text + ' '
            
            news_contents[title] = first_five_paragraphs
    
        # 5. Generate a topic per news
        ideas = {}
        for title, content in news_contents.items():
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"""You are an instagram community manager that needs to come up with a relevant and creative idea for a client's post. Follow these steps to find the idea: \
    1. Considering the client's description of their instagram:'{program_description}' and their target audience: '{target_segment}'. Generate a unique idea for their instagram from this news: '{content}'. Include actual content from the news in this idea, we are doing content marketing that most be valuable for the user and is not promotional.
    2. Output a complete idea.
    Avoid coming up with ideas that are unrelated with their target audience orthe client's description. Also avoid topics that require an image that has text written on it or several images, for instace, a meme, aquote, or topics such as 'three tips to...'."""}
                ]
            )
            ideas[title] = response['choices'][0]['message']['content']

        # 6. Let the user choose the most relevant topic
        print("Please choose the best idea:")
        for i, (title, idea) in enumerate(ideas.items()):
            print(f"{i+1}. {title}: {idea}")
        chosen_idea_number = int(input("Enter the number of your chosen topic: "))
        chosen_title = list(ideas.keys())[chosen_idea_number-1]
        idea = ideas[chosen_title]

        # 7. Save the news in the database so it doesn't repeat later
        conn = sqlite3.connect('decision_tree.db')
        c = conn.cursor()
    
        c.execute("INSERT INTO news (user_id, title) VALUES (?, ?)",(user_id, chosen_title))
        conn.commit()
        replace_idea(conn, c, user_id, user_input, idea)
        
        return {'idea':idea}

def normalize_idea(conn, c, user_id, user_input, user_idea, target_segment, program_description):
  response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are an instagram community manager."},
        {"role": "user", "content": f"You are an instagram community manager that needs to complete the idea of a client. Their idea is {user_idea}, however, it may be incomplete. A proper idea needs to have a clear topic and a style. Therefore, complete their idea with additional elements that will help portray their vision. Make sure that your completion is aligned with their {program_description} and {target_segment}. Nonetheless, if the idea the user provided is complete, leave it as it is."}
  ]
)
  idea = response['choices'][0]['message']['content']
  replace_idea(conn, c, user_id, user_input, idea)
  return {"idea":idea}

def manipulate_idea(conn, c, user_id, user_input, idea):
  print(idea)
  idea = input("Write out the idea you had in mind: ")
  replace_idea(conn, c, user_id, user_input, idea)
  return {"idea":idea}