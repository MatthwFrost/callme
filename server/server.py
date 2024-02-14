from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Record
from google.cloud import speech
from google.cloud.speech import types
import io

app = Flask(__name__)

@app.route("/answer", methods=['POST'])
def answer_call():
    """Responds to incoming calls with a prompt to record a message."""
    resp = VoiceResponse()
    resp.say("Hello, please say something after the beep. Press any key to finish.")
    # Record the caller's voice input
    resp.record(maxLength="30", action="/process_recording", playBeep=True)
    return str(resp)

@app.route("/process_recording", methods=['POST'])
def process_recording():
    """Processes the recording and uses Speech-to-Text to transcribe it."""
    recording_url = request.values.get("RecordingUrl", "")
    transcription = transcribe_audio(recording_url)
    
    resp = VoiceResponse()
    if transcription:
        resp.say(f"Here is what you said: {transcription}")
    else:
        resp.say("Sorry, I couldn't understand that.")
    
    return str(resp)

def transcribe_audio(recording_url):
    """Transcribes the audio file from the given URL using Google Cloud Speech-to-Text."""
    client = speech.SpeechClient()
    
    # Load the audio from the URL
    audio = types.RecognitionAudio(uri=recording_url)
    config = types.RecognitionConfig(
        encoding=types.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code='en-US'
    )
    
    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)
    
    for result in response.results:
        return result.alternatives[0].transcript
    
    return None

if __name__ == "__main__":
    app.run(debug=True)

