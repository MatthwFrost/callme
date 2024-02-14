import asyncio
import shutil
import whisper
from pydub import AudioSegment
from pydub.playback import play
import time

from listen import listen
from text_generation import chat_completion

async def main():
# Load / Download model
    print(f"Downloading tiny.en model.")
    model = "base" 
    audio_model = whisper.load_model(model)
    print("Finished downloading model.")
    #play_introduction()

    while True:
        user_query = listen(audio_model)
        # start = time.time()
        print(user_query)
        if "stop" in user_query:
            break
        await chat_completion(user_query)        
        # end = time.time()
        # print(end - start)


# Main execution
if __name__ == "__main__":
    asyncio.run(main())
