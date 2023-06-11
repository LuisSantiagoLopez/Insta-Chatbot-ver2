import os
import requests
from imgurpython import ImgurClient
from config import imgur_client_id, imgur_client_secret

def change_url(url):
  
    # Download the image
    url = url.strip('\"')
    response = requests.get(url)
    image_filename = "downloaded_image.png"
    
    # Save the image
    with open(image_filename, 'wb') as file:
        file.write(response.content)

    # Upload the image to Imgur
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    upload_result = client.upload_from_path(image_filename, config=None, anon=True)

    # Remove the local image file
    os.remove(image_filename)

    print(f"Imgur link: {upload_result['link']}")
  
    # Return the Imgur URL
    return upload_result['link']