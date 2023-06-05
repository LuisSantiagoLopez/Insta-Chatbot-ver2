import requests

from config import AYRSHARE_API_KEY

def upload_instagram(image_url, caption):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AYRSHARE_API_KEY}"
    }

    post_data = {
        "post": caption,
        "mediaUrls": [image_url],
        "platforms": ["instagram"]
    }

    response = requests.post("https://app.ayrshare.com/api/post", json=post_data, headers=headers)

    if response.status_code == 200:
        print("Image successfully posted to Instagram!")
    else:
        print(f"Error posting image to Instagram: {response.status_code} - {response.text}")