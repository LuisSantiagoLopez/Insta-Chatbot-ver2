from instagrapi import Client
from change_url_imgur import save_image
from instagrapi.types import Usertag, Location

cl = Client()

def upload_instagram(conn, c, user_id, user_input, image_url, caption, instagram_username, instagram_password):
    cl.login(instagram_username, instagram_password)
    image_file = save_image(image_url)
    print(image_file)
    media = cl.photo_upload(
        image_file,
        caption
    )
    