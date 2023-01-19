import os
import openai
import gradio as gr

openai.api_key = ""

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "

def openai_create(prompt):
    print("Prompt: {0}".format(prompt))

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.9, # randomness to responses, 0 = no randomness
    max_tokens= 1024, # max amount of characters
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    stop=[" Human:", " AI:"]
    )

    return response.choices[0].text

