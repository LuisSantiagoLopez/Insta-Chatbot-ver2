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
    
def download_video(video_url):
    # Send a GET request to the video URL
    response = requests.get(video_url, stream=True)

    # Check that the request was successful
    if response.status_code == 200:
        # The path where you want to save the downloaded video
        video_file = "video.mp4"
        
        # Write the contents of the response to a file
        with open(video_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return video_file
    else:
        print(f"Failed to download video: {response.status_code}")
        return None