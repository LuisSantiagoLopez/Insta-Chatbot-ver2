from .chatgpt_langchain import chatgptlc
import openai
import json
from .token_usage import token_usage


def generate_image_dalle(image_prompt):
    response = openai.Image.create(prompt=image_prompt, n=4, size="1024x1024")
    image_urls = response["data"]

    return image_urls


def choose_best_image(image_urls):
    print("Please choose the best image:")
    for i, image_url in enumerate(image_urls):
        print(f"{i+1}. {image_url}")
    chosen_image_number = int(input("Enter the number of your chosen image: "))
    chosen_image_url = (
        image_urls[chosen_image_number - 1]["url"] if chosen_image_number != 0 else 0
    )
    return chosen_image_url


def create_image(conn, c, user_id, user_input, idea, styles):
    image_url = ""
    idea = json.loads(idea)
    print(idea["Illustration"])
    prompt = f"DALLE is OpenAI's text prompt to image AI generation model. Your task is to create a DALLE prompt from the client's idea of an illustration inside triple backticks. \
The text prompt should be one simple sentence describing the image with ', digital art' at the end. \
Take these considerations when writing the prompt: \
- styles such as 3d renders and manga work best \
- the description should be symbolic. \
- Incorporate the user's style: '{styles}'. \
Avoid these mistakes when writing a prompt: \
- DALLE can not generate humans, faces, human figures, people, or hands. \
- DALLE can not generate text on an image. No logos, no text, no numbers, no banners, no signs. \
- DALLE can not create complex images. \
- DALLE prompts should be extremely simple signle sentences with 10 or fewer words. \
- ONLY take into account the idea inside the triple backticks. \
- The DALLE prompt should contain NO explanations, do not use 'symbolizing', 'representing', 'like' or any other justification. \
Your output should be a JSON dictionary with the key 'prompt' \
Client's idea: ```{idea['Illustration']}```."

    image_prompt = chatgptlc(conn, c, user_id, user_input, prompt, 0.7, "gpt-4")
    print(image_prompt)
    image_prompt = json.loads(image_prompt)
    image_url = choose_best_image(generate_image_dalle(image_prompt["prompt"]))

    token_usage["total_images"] += 4
    token_usage["total_cost"] += 0.08

    if image_url == 0:
        while image_url == 0:
            image_feedback = input("What was wrong with the images? ")
            prompt = f"Your task is to improve a text to image diffusion prompt created for the client. I will give you the current prompt and the client's feedback and you should implement the changes. Their current prompt is inside the apostrophes: '{image_prompt}' and their feedback is inside the triple backticks ```{image_feedback}```. The prompt should be simple and straightforward. If the feedback asked to add something from the image, add it to the end of the prompt; for instance: 'rest of the prompt... yellow highlights, 3d render'. Your output should be a JSON dictionary with the key 'prompt'"

            image_prompt = json.loads(
                chatgptlc(conn, c, user_id, user_input, prompt, 0.2, "gpt-4")
            )
            print(image_prompt)

            image_url = choose_best_image(generate_image_dalle(image_prompt["prompt"]))
            token_usage["total_images"] += 4
            token_usage["total_cost"] += 0.08

        return {"image_url": image_url, "image_prompt": image_prompt}

    print(idea["Instagram Idea"])
    return {"image_url": image_url, "image_prompt": image_prompt}
