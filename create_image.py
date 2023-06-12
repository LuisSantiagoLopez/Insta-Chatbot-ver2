from chatgpt import chatgpt
from config import HUGGING_FACE_API_KEY
import requests
import openai
import json

def generate_image_dalle(image_prompt):
    response = openai.Image.create(
      prompt=image_prompt,
      n=4,
      size="512x512"
    )
    image_urls = response["data"]

    return image_urls

def generate_image_hf(image_prompt):
    API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney-v4"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}

    def query(payload):
    	response = requests.post(API_URL, headers=headers, json=payload)
    	return response.content
    image_bytes = query({
    	"inputs": image_prompt,
    })
    # You can access the image with PIL.Image for example
    import io
    from PIL import Image
    image = Image.open(io.BytesIO(image_bytes))

def choose_best_image(image_urls):
    print("Please choose the best image:")
    for i, image_url in enumerate(image_urls):
        print(f"{i+1}. {image_url}")
    chosen_image_number = int(input("Enter the number of your chosen image: "))
    chosen_image_url = image_urls[chosen_image_number-1]["url"] if chosen_image_number != 0 else 0
    return chosen_image_url

def create_image(conn, c, user_id, user_input, idea):
    image_url = ""
    idea = json.loads(idea)
    print(idea['Illustration'])
    prompt = f"DALLE is OpenAI's text prompt to image AI generation model. \
    Your task is to apply the structure of a DALLE prompt to the \
    client's idea of an illustration inside triple backticks. \
    The text prompt should contain: \
    - A really simple description of the image with no reference to the client.' \
    - Keywords describing the style and the quality. \
    Use the simple structure of these example prompts to create yours: <Example 1: Vintage 90's anime style. cluttered starship interior; \
    captain giving orders; by Hajime Sorayama, Greg Tocchini, Virgil Finlay, sci-fi, colors, neon lights. Example 2: pen and ink, birds eye view, \
    illustrated by hergé, Background space and earth. man alone forever. Sadness. \
    Example 3: Abstract dark fantasy romance book cover of cinderella's glass slipper in front of a fantasy castle. \
    highly detailed, fantasy artwork, digital painting, greg rutkowski, 8k, concept art, artstation, hyper detailed, \
    rule of thirds, no text. Example 4: vintage personal handheld computer assistance devices, 1990s, c4d render, vaporwave, \
    product photography. Example 5: 50s cartoon style photo of a huge savage skelton emopunk robot in far off galaxy, \
    style of Hannah Barbara, studio ghibli, akira toriyama, james gilleard, warner brothers, trending pixiv fanbox, \
    acrylic palette knife, 8k, vibrant colors, devinart, trending on artstation, low details, smooth. Example 6: \
    pixel art san francisco fisherman's wharf. 3d pixel art 4k wallpaper. incredible pixel art details. flowers. \
    Example 7: pixel art. lots of people in foreground. pixel art by Pixel Jeff> \
    Avoid these mistakes when writing a prompt: \
    - DALLE can not generate human faces or hands appropriately \
    - DALLE can not generate text on an image. No logos, no text. \
    - DALLE can not create complex images. \
    Your output should be a JSON dictionary with the key 'prompt' \
    Client's idea: ```{idea['Illustration']}```."
  
    image_prompt = chatgpt(conn, c, user_id, user_input, prompt, 0.7, "gpt-4")
    print(image_prompt)
    image_prompt = json.loads(image_prompt)
    image_url = choose_best_image(generate_image_dalle(image_prompt['prompt']))

    #This function is designed for later functionality. The user should be capable of giving feedback if none of the images were of his liking. image_feedback should be integrated into a block of code 
  
    if image_url == 0:
        while image_url == 0:
            image_feedback = input("What was wrong with the images? ")
            prompt = f"Your task is to improve a text to image diffusion prompt created for the client. I will give you the current prompt and the client's feedback and you should implement the changes. Their current prompt is inside the apostrophes: '{image_prompt}' and their feedback is inside the triple backticks ```{image_feedback}```. The prompt should be simple and straightforward. If the feedback asked to remove something from the image, add it to the end of the prompt; for instance: 'rest of the prompt... no text, no deformities'. Output the new prompt inside a json dictionary with the key 'New Prompt:'"

            image_prompt = json.loads(chatgpt(conn, c, user_id, user_input, prompt, 0.2, "gpt-4"))
            print(image_prompt)
      
            image_url = choose_best_image(generate_image_dalle(image_prompt['New Prompt']))

        return image_url, image_prompt
    
    return {"image_url": image_url, "image_prompt": image_prompt}