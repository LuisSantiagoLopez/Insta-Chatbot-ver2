from chatgpt import chatgpt
import openai
import json

def generate_image(image_prompt):
    response = openai.Image.create(
      prompt=image_prompt["prompt"],
      n=4,
      size="512x512"
    )
    
    image_urls = response["data"]
  
    print("Please choose the best image:")
    for i, image_url in enumerate(image_urls):
        print(f"{i+1}. {image_url}")
    chosen_image_number = int(input("Enter the number of your chosen image: "))
    if chosen_image_number == 0:
        return print("re-generate images")
    chosen_image_url = image_urls[chosen_image_number-1]["url"]

    return chosen_image_url

def create_image(conn, c, user_id, user_input, idea):
    idea = json.loads(idea)
    print(idea['Illustration'])
    prompt = f"DALLE is OpenAI's text prompt to image AI generation model. \
    Your task is to apply the structure of a DALLE prompt to the \
    client's idea of an illustration inside triple backticks. \
    The text prompt should contain: \
    - A description of the image.' \
    - Keywords describing the style, the quality, and other artist's or website's styles. \
    Use these examples of other successful prompts to structure yours: <Example 1: Vintage 90's anime style. cluttered starship interior; \
    captain giving orders; by Hajime Sorayama, Greg Tocchini, Virgil Finlay, sci-fi, colors, neon lights. Example 2: pen and ink, birds eye view, \
    illustrated by hergé, Background space and earth. man alone forever. Sadness. \
    Example 3: Abstract dark fantasy romance book cover of cinderella's glass slipper in front of a fantasy castle. \
    highly detailed, fantasy artwork, digital painting, greg rutkowski, 8k, concept art, artstation, hyper detailed, \
    rule of thirds, no text. Example 4: vintage personal handheld computer assistance devices, 1990s, c4d render, vaporwave, \
    product photography. Example 5: 50s cartoon style photo of a huge savage skelton emopunk robot in far off galaxy, \
    style of Hannah Barbara, studio ghibli, akira toriyama, james gilleard, warner brothers, trending pixiv fanbox, \
    acrylic palette knife, 8k, vibrant colors, devinart, trending on artstation, low details, smooth. Example 6: \
    pixel art san francisco fisherman's wharf. 3d pixel art 4k wallpaper. incredible pixel art details. flowers. \
    pixel art. lots of people in foreground. pixel art by Pixel Jeff> \
    Avoid these mistakes when writing a prompt: \
    - DALLE can not generate human faces or hands appropriately \
    - DALLE can not generate text on an image \
    - DALLE struggles at depicting hands or groups of subjects. \
    Your output should be a JSON dictionary with the key 'prompt' \
    Client's idea: ```{idea['Illustration']}```."
  
    image_prompt = chatgpt(conn, c, user_id, user_input, prompt, 0.7, "gpt-4")
    print(image_prompt)
    image_prompt = json.loads(image_prompt)
  
    image_url = generate_image(image_prompt)
    
    if image_url == "re-generate images":
        return print("re-generate images")
  
    return {"image_url": image_url, "image_prompt": image_prompt}