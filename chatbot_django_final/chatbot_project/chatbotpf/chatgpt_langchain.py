from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks import get_openai_callback
from .token_usage import token_usage
from chatbot_insta.models import Conversations
import json

variables = {}
conversations = []


def chatgptlc(request, prompt, temperature=0.5, model="gpt-3.5-turbo"):
    data = json.loads(request.body)
    target_segment = data.get("target_segment")
    program_description = data.get("program_description")

    system_message_template = f"You are a helpful instagram content creator for this client's instagram: '{program_description}' with this target audience: '{target_segment}'. Help them execute a variety of tasks related with their instagram content marketing."

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_message_template),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    chat = ChatOpenAI(temperature=temperature, model=model)
    memory = ConversationBufferWindowMemory(k=5, return_messages=True)

    # Fetch past conversation from the database
    conversation_history = Conversations.objects.filter(user=request.user).values(
        "prompt", "output"
    )

    for conversation in conversation_history:
        input_text = conversation["prompt"]
        output_text = conversation["output"]
        conversations.append({"input": input_text})
        conversations.append({"output": output_text})
        memory.save_context({"input": input_text}, {"output": output_text})

    conversation = ConversationChain(
        llm=chat, prompt=chat_prompt, memory=memory, verbose=True
    )

    # This second chain handles non-memory requests
    system_template = system_message_template
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt_2 = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    secondary_chain = LLMChain(
        llm=chat,
        prompt=chat_prompt_2,
    )

    # Get the AI response
    with get_openai_callback() as cb:
        if prompt[0] == "1":
            response = secondary_chain.run(text=prompt)
        else:
            response = conversation.predict(input=prompt)
            conversation = Conversations(
                user=request.user, prompt=prompt, output=response
            )
            conversation.save()

        # Assign each statement to a variable
        total_tokens = cb.total_tokens
        prompt_tokens = cb.prompt_tokens
        completion_tokens = cb.completion_tokens
        total_cost = cb.total_cost

        # Add the values to the totals dictionary
        token_usage["total_tokens"] += total_tokens
        token_usage["prompt_tokens"] += prompt_tokens
        token_usage["completion_tokens"] += completion_tokens
        token_usage["total_cost"] += total_cost

    return response
