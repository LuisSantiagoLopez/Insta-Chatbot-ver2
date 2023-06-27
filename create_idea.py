from chatgpt_langchain import chatgptlc
import requests
import json
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from config import SERP_API_KEY
from token_usage import token_usage

def replace_idea(conn, c, user_id, user_input, idea):
    str_idea = json.dumps(idea)
    c.execute("REPLACE INTO tree (user_id, function, parameter, value) VALUES (?, ?, ?, ?)", (user_id, user_input, "idea", str_idea))
    conn.commit()

def trends(conn, c, user_id, user_input):
    prompt = "Execute the following tasks to find 5 relevant keywords for the client: \
    - Find 5 common and popular one or two word keywords that are directly related to the client's target audience. \
    - Only output the five keywords separated by commas."

    keywords = chatgptlc(conn, c, user_id, user_input, prompt, 0.7, "gpt-4")
    print(keywords)
  
    trends_search = GoogleSearch({"q": keywords, 
                                  "engine": "google_trends",
                                  "date": "now 1-d",
                                  "api_key": SERP_API_KEY})
    
    token_usage["total_searches"] += 1
    token_usage["total_cost"] += 0.01
    
    trends_results = trends_search.get_dict()

    latest_entry = max(trends_results["interest_over_time"]["timeline_data"], key=lambda x: int(x['timestamp']))

    values = latest_entry['values']
    values = [d for d in values if d['value'] != '<1']

    sorted_keywords = sorted(values, key=lambda x: int(x['value']), reverse=True)[:3]
    print(sorted_keywords)
    
    for keyword_results in sorted_keywords:
        token_usage["total_searches"] += 1
        token_usage["total_cost"] += 0.01
      
        keyword = keyword_results['query']
        news_search = GoogleSearch({"q": keyword, "tbm": "nws", "api_key": SERP_API_KEY})
        news_results = news_search.get_dict()['news_results']

        relevant_news = {}
        for news in news_results:
            c.execute("SELECT title FROM news WHERE user_id=? AND title=?", (user_id, news['title']))
            db_result = c.fetchone()
            
            if db_result is None:
                prompt = f"1. Your task is to determine whether this news title: '{news['title']}' is relevant to our client's audience and description. Output a 'yes.' or 'no.' answer, even if you are not certain if the answer is correct."
                is_news_relevant = chatgptlc(conn, c, user_id, user_input, prompt, 0)  
                print(is_news_relevant)
                  
                if is_news_relevant.lower() == 'yes.':
                    relevant_news[news['title']] = news['link']
                    print(news['title'])
                    
                    # Check if the dictionary has 3 items
                    if len(relevant_news) == 3:
                        break
            else:
                continue
    
    news_contents = {}
    print(relevant_news)
    for title, link in relevant_news.items():
        response = requests.get(link)
        print(f"Status Code: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        news_text = ""
        word_count = 0
        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text().strip()
            words = paragraph_text.split()
            if word_count + len(words) <= 2500:
                news_text += paragraph_text + ' '
                word_count += len(words)
            else:
                break
        
        news_contents[title] = news_text
        
        prompt = f"1. Summarize this news article into bullet points with the most important parts of its content.\
        Title: '{title}'. Contents: '{news_contents[title]}'"
        news_contents[title] = chatgptlc(conn, c, user_id, user_input, prompt, 0.2)
    return news_contents

def create_idea(conn, c, user_id, user_input, target_segment, program_description):
    # Create the 'ideas' table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS ideas
                 (user_id TEXT, title TEXT PRIMARY KEY, idea_json TEXT)''')
    conn.commit()

    # Fetch existing ideas from the database
    c.execute("SELECT title, idea_json FROM ideas WHERE user_id=?", (user_id,))
    existing_ideas = c.fetchall()

    # Check if there are existing ideas
    if user_input == "choose another idea":
        print("Existing ideas found. Select an idea:")
        for i, (title, idea_json) in enumerate(existing_ideas):
            idea = json.loads(idea_json)
            print(f"{i+1}. {title}: {idea}")

        chosen_idea_number = int(input("Enter the number of your chosen idea: "))
        chosen_title, chosen_idea_json = existing_ideas[chosen_idea_number - 1]
        idea = json.loads(chosen_idea_json)

        c.execute("DELETE FROM ideas WHERE title=?", (chosen_title,))
        conn.commit()

        replace_idea(conn, c, user_id, user_input, idea)
        return {'idea': idea}

    # Execute the trends function to generate new ideas
    news_contents = trends(conn, c, user_id, user_input)

    for title, content in news_contents.items():
        prompt = f"Your task is to create an idea for an Instagram post based on the summary of this news article: '{title}' \
            which is inside the triple backticks. \
            Based on your idea, the client will decide whether to generate the post or not. \
            Therefore, your idea should contain the following elements: \
            - A pitch of your idea to the client \
            - A caption that explains the content of the news article. The users will have no other interaction with the news article, and they will not be able to find a link to the news article. Make the caption entertaining and as long as necessary with no emojis. Add relevant hashtags at the end. \
            - A single sentence for a simple illustrative representation of the topic that requires no text, no logos, no explanations, and no representations. \
            Summary of the News Article '{title}': ```{content}``` \
            - Do not ask for an illustration with logos or text. \
            Structure your output in JSON format with the following keys: \
            Instagram Idea: 'Here goes the title of your idea' \
            Caption: 'Here goes the caption of the post.' \
            Illustration: 'Here goes the illustrative representation of the topic' \
            News: 'Here goes the summary of the news article'"

        idea_json = chatgptlc(conn, c, user_id, user_input, prompt, 0.4, "gpt-4")

        c.execute("INSERT OR REPLACE INTO ideas (user_id, title, idea_json) VALUES (?, ?, ?)", (user_id, title, idea_json))
        conn.commit()

    print("Please choose the best idea:")
    for i, (title, _) in enumerate(news_contents.items()):
        print(f"{i+1}. {title}")

    chosen_idea_number = int(input("Enter the number of your chosen idea: "))
    chosen_title = list(news_contents.keys())[chosen_idea_number - 1]
    chosen_idea_json = c.execute("SELECT idea_json FROM ideas WHERE user_id=? AND title=?", (user_id, chosen_title)).fetchone()[0]
    idea = json.loads(chosen_idea_json)

    c.execute("DELETE FROM ideas WHERE title=?", (chosen_title,))
    conn.commit()

    replace_idea(conn, c, user_id, user_input, idea)
    return {'idea': idea}


def normalize_idea(conn, c, user_id, user_input, user_idea, target_segment, program_description):
    prompt = f"Your task is to create an idea for an Instagram post based on the user's idea inside triple backticks. \ Based on your idea, the client will decide whether to generate the post or not. \
            Therefore, your idea should contain the following elements: \
            - A pitch of your idea to the client \
            - A really simple representation of the topic that only requires an illustration with no text. \
            - A caption that expands on the topic at hand with relevant emojis. \
            User's Idea: ```{user_idea}``` \
            Structure your output in JSON format with the following keys: \
            Instagram Idea: 'Here goes the title of your idea' \
            Caption: 'Here goes the caption of the post' \
            Explanation: 'Here goes the body of the idea' \
            Illustration: 'Here goes the imaginative representation of the topic'"
  
    idea = chatgptlc(conn, c, user_id, user_input, prompt, 0.5, "gpt-4")
    replace_idea(conn, c, user_id, user_input, idea)
    return {"idea":idea}

def manipulate_idea(conn, c, user_id, user_input, idea):
  print(idea)
  idea = input("Write out the idea you had in mind: ")
  replace_idea(conn, c, user_id, user_input, idea)
  return {"idea":idea}