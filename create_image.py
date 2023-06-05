from main import chatgpt
import replicate

def generate_image(image_prompt):
    input_parameters = {
        "prompt": image_prompt,
        "image_dimensions": "768x768",
        "negative_prompt": "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, words, low quality, bad quality, low resolution",
        "num_outputs": 1,
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "scheduler": "DPMSolverMultistep",
    }

    output = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input=input_parameters
    )

    image_url = output[0]
    return image_url

def create_image(idea):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "user", "content": f"You are a Stable Diffusion prompt engineer. Your job is to create a prompt for a Stable Diffusion image model to generate an image about a topic. \
            Your tasks are: \
            1. Analyze the structural patterns in the example prompts I will provide you. \
            2. Based on the patterns you find, create a prompt for the image model to generate an image for this idea: {idea}. Creatively represent the topic and the style detailed on the idea. \
            3. The output should be a single prompt.\
            The example prompts are surrounded by <>: <Vintage 90's anime style. cluttered starship interior; captain giving orders; by Hajime Sorayama, Greg Tocchini, Virgil Finlay, sci-fi, colors, neon lights> <pen and ink, birds eye view, illustrated by hergé, Background space and earth. man alone forever. Sadness.> <Abstract dark fantasy romance book cover of cinderella's glass slipper in front of a fantasy castle. highly detailed, fantasy artwork, digital painting, greg rutkowski, 8k, concept art, artstation, hyper detailed, rule of thirds, no text> <vintage personal handheld computer assistance devices, 1990s, c4d render, vaporwave, product photography> <50s cartoon style photo of a huge savage skelton emopunk robot in far off galaxy, style of Hannah Barbara, studio ghibli, akira toriyama, james gilleard, warner brothers, trending pixiv fanbox, acrylic palette knife, 8k, vibrant colors, devinart, trending on artstation, low details, smooth> <pixel art san francisco fisherman's wharf. 3d pixel art 4k wallpaper. incredible pixel art details. flowers. pixel art. lots of people in foreground. pixel art by Pixel Jeff> \
            As a note, don't just copy the example prompts. Be creative and come up with your own prompts that creatively represent the idea. \
            Avoid creating a prompt for an image that requires many objects or things, or one that asks for realistic faces, or one that has letters or numbers. The Stable Diffusion model still has difficulty generating these."}
            ]
    )
  
    image_prompt = response['choices'][0]['message']['content']
  
    return {"image_url": generate_image(image_prompt), "image_prompt": image_prompt}