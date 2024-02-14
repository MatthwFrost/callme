from openai import AsyncOpenAI
import asyncio

from stream import text_to_speech_input_streaming
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set OpenAI API key
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if text is None:  # Skip None values
            continue
        if buffer.endswith(splitters):
            yield buffer + " "
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + " "

async def chat_completion(query):

    """Retrieve text from OpenAI and pass it to the text-to-speech function."""
    print("Getting text")

    system_role ="You are a French teacher on a call to a student. Your role is to have casual convosation and keep the convosation exciting. You are required to keep it exciting" \
             "You are the users best friend and you are looking for a catch up. You've been friends for many years. You have just been through something upsetting and you really want to talk about it" \
             "If asked to slow donw: Split every word with a \"-\" in the sentences you speak french and reply, \"Sure, I will be speaking slow from now on\"" \
             "You should be kind and very convosational, looking to boost the users mood at ALL times." \
             "Split every word by a dash"
         # Set a new event loop for the current thread
    #system_role = "You are a Jarvis like assistant. I will require you to answer my questions in a casual tone. Keep the convosation causal. Keep answers short and only elaborate when asked."
    
    # Now you can run the coroutine in this loop
    response = await aclient.chat.completions.create(
        model='gpt-3.5-turbo', 
        messages=[{"role": "system", "content": system_role},
                  {'role': 'user', 'content': f"{query}"}],
        temperature=0.8, stream=True
    )
    
    # Close the loop when done
    print("Finished getting text")


    async def text_iterator():
        async for chunk in response:
            delta = chunk.choices[0].delta
            yield delta.content
    
    await text_to_speech_input_streaming(text_iterator())
