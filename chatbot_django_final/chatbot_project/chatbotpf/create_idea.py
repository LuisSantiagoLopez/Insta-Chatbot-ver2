from .chatgpt_langchain import chatgptlc
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from .config import SERP_API_KEY
from .config import SERPWOW_API_KEY
from .token_usage import token_usage
from chatbot_insta.models import Newstitles
import json
import requests


def trends(request):
    prompt = "Execute the following tasks to find 5 relevant keywords for the client: \
    - Find 5 related one word keywords that are directly related to the client's target audience. \
    - Only output the five keywords separated by commas. Do not add any special character to the word."

    keywords_string = chatgptlc(request, prompt, 0.7, "gpt-4")
    print(keywords_string)

    # Convert the comma-separated string into a list of keywords
    keywords = []
    for keyword in keywords_string.split(","):
        keyword = keyword.strip()  # Remove leading and trailing whitespace
        if " " in keyword:
            keyword = '"' + keyword + '"'  # Wrap two-word keyword in double quotes
        keywords.append(keyword)

    trends_search = GoogleSearch(
        {
            "q": keywords,
            "engine": "google_trends",
            "date": "now 1-d",
            "api_key": SERP_API_KEY,
        }
    )

    token_usage["total_searches"] += 1
    token_usage["total_cost"] += 0.01

    trends_results = trends_search.get_dict()
    print(trends_results)

    latest_entry = max(
        trends_results["interest_over_time"]["timeline_data"],
        key=lambda x: int(x["timestamp"]),
    )

    values = latest_entry["values"]
    values = [d for d in values if d["value"] != "<1"]

    sorted_keywords = sorted(values, key=lambda x: int(x["value"]), reverse=True)[:3]
    print(sorted_keywords)

    for keyword_results in sorted_keywords:
        token_usage["total_searches"] += 1
        token_usage["total_cost"] += 0.01

        keyword = keyword_results["query"]
        news_search = GoogleSearch(
            {"q": keyword, "tbm": "nws", "api_key": SERP_API_KEY}
        )
        news_results = news_search.get_dict()["news_results"]

        relevant_news = {}
        for news in news_results:
            db_result = Newstitles.objects.filter(
                user=request.user, newstitle=news["title"]
            ).first()
            if db_result is None:
                prompt = f"1. Your task is to determine whether this news title: '{news['title']}' is relevant to our client's audience and description. Output a 'yes.' or 'no.' answer, even if you are not certain if the answer is correct."
                is_news_relevant = chatgptlc(request, prompt, 0)
                print(is_news_relevant)

                if is_news_relevant.lower() == "yes.":
                    news_title_db = Newstitles(
                        user=request.user, newstitle=news["title"]
                    )
                    news_title_db.save()
                    relevant_news[news["title"]] = news["link"]
                    print(news["title"])

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
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        news_text = ""
        word_count = 0
        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text().strip()
            words = paragraph_text.split()
            if word_count + len(words) <= 2500:
                news_text += paragraph_text + " "
                word_count += len(words)
            else:
                break

        news_contents[title] = news_text

        prompt = f"1. Summarize this news article into bullet points with the most important parts of its content.\
        Title: '{title}'. Contents: '{news_contents[title]}'"
        news_contents[title] = chatgptlc(request, prompt, 0.2)

    return news_contents


def create_idea(request, news_contents):
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

        idea = chatgptlc(request, prompt, 0.4, "gpt-4")
        idea_json = json.loads(idea)
        three_ideas = []
        three_ideas.append(idea_json)

    return {"three_ideas": three_ideas}


def normalize_idea(request, user_idea):
    prompt = f"Your task is to create an idea for an Instagram post based on the idea the user provided inside the triple backticks. \
            Your idea should contain the following elements: \
            - A pitch of your idea to the client \
            - A caption that expands on the concept the user asked for. Make it lengthy and entertaning, but avoid emojis. \
            - A single sentence for a simple illustrative representation of the topic that requires no text, no people and no logos. \
            User's idea: ```{user_idea}``` \
            - Do not ask for an illustration with logos or text. \
            Structure your output in JSON format with the following keys: \
            Instagram Idea: 'Here goes the title of your idea' \
            Caption: 'Here goes the caption of the post.' \
            Illustration: 'Here goes the illustrative representation of the topic'"

    idea = chatgptlc(request, prompt, 0.5, "gpt-4")
    return {"idea": idea}


def manipulate_idea(idea):
    print(idea)
    idea = input("Write out the idea you had in mind: ")
    return {"idea": idea}
