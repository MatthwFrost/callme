import asyncio
import websockets
import json
import base64
import shutil
import subprocess
import ssl
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play

from chunker import text_chunker
load_dotenv()

async def stream(audio_stream):
    """Stream audio data using mpv player."""

    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print("Started streaming audio")
    async for chunk in audio_stream:
        if chunk:
            await write_to_mpv_async(mpv_process, chunk)

    if mpv_process.stdin:
        mpv_process.stdin.close()

async def write_to_mpv_async(process, chunk):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, process.stdin.write, chunk)
    await loop.run_in_executor(None, process.stdin.flush)

async def text_to_speech_input_streaming(text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    voice_id = 'cXTSK3LJBx7irlK2jy7q'
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2&optimize_streaming_latency=4"
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_default_certs()


    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            # start = time.time()
            await websocket.send(json.dumps({
                "text": " ",
                "voice_settings": {"stability": 0.5, "similarity_boost": 1},
                "xi_api_key": ELEVENLABS_API_KEY,
            }))

            async def listen_sock():
                """Listen to the websocket for audio data and stream it."""
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        if data.get("audio"):
                            yield base64.b64decode(data["audio"])
                        elif data.get('isFinal'):
                            break
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed")
                        break

            listen_task = asyncio.create_task(stream(listen_sock()))
            # end = time.time()
            # print(f"Fetched: {end - start}")

            async for text in text_chunker(text_iterator):
                await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

            await websocket.send(json.dumps({"text": ""}))

            await listen_task
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed with error: {e}. Attempting to reconnect...")
        await asyncio.sleep(1)  # Simple backoff strategy
