from main import chatgpt

def create_caption(idea, image_prompt, target_segment, program_description):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"You are an Instagram Copywriter. Your job will be to write a relevant caption for an instagram post about a topic and image. \
        Your tasks are the following: \
        1. Understand the target audience and the client's description of their instagram I will provide you. \
        2. Analyze the topic and image description I will provide you. \
        3. Based on the client's description, their target audience and specific topic and image description, write a relevant caption for their post. \
        4. The output should only be the caption for the post. \
        The topic is: `{idea}`. \
        The image prompt is: `{image_prompt}` \
        The target audience is: `{target_segment}` \
        The client's description of their instagram is: `{program_description}`"},
            {"role": "assistant", "content": ""},
        ])

    caption = response['choices'][0]['message']['content']
    return {"caption":caption}