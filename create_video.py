from config import PEXELS_API_KEY
import json
import shutil
import requests
from gtts import gTTS
import os
from pydub import AudioSegment

def download_video(url, filename):
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

def get_pexels_video(keyword):
    headers = {
        'Authorization': 'Your_Pexels_API_Key', # replace with your actual Pexels API key
    }

    response = requests.get(f'https://api.pexels.com/videos/search?query={keyword}&per_page=1', headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = json.loads(response.text)

        # Check if there is at least one video
        if data['videos']:
            # Get the URL of the first video
            video_url = data['videos'][0]['video_files'][0]['link']

            return video_url

    else:
        print(f'Error: {response.status_code}')
        return None

def text_to_speech(text, filename):
    # Create speech
    tts = gTTS(text=text, lang='en')
    # Save to file
    tts.save(filename)

    # Get duration of the audio file
    audio = AudioSegment.from_file(filename)
    duration = len(audio) / 1000  # duration in seconds

    return filename, duration


def create_video(conn, c, user_id, user_input, idea, tone):
  if idea['News']:
    prompt = f"Create a prose social media video script based on the news article inside the triple backticks. \
    Consider the following elements when writing the script: \
    1. The script should have this tone: '{tone}'. \
    2. The script should be short. \
    3. The script should start with an attractive, controversial or thought provoking sentence. \
    4. The script should dive straight into the point and avoid unnecessary details. \
    5. The script should have one silly mistake (such as mispronouncing a word) or a very controversial view on the topic. \
    News Article: ```{idea['News']}```. \
    The output should only be a JSON dictionary with the key 'Script: Here goes the script'"

    script = chatgptlc(conn, c, user_id, user_input, prompt, 0.5, "gpt-4")

  prompt = f"Generate one keyword for each sentence on this script: '{script}'. Your output should be comma separated keywords. Consider the clients' description of their program."

  comma_keywords = chatgptlc(conn, c, user_id, user_input, prompt, 0, "gpt-4")
  keywords = keywords_str.split(', ')

  for i, keyword in enumerate(keywords):
    # Get video URL from Pexels using keyword
    video_url = get_pexels_video(keyword)  # Add your Pexels API call function here

    # Download video
    download_video(video_url, f"video_{i}.mp4")  # This will save the video as "video_0.mp4", "video_1.mp4", etc.
    