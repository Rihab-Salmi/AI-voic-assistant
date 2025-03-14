import vosk
import sys
import queue
import sounddevice as sd
import json
import requests
import os
from gtts import gTTS
import pygame
import time

API_KEY_GEMINI = ""
API_KEY_ELEVENLABS = ""

# Load Vosk model
model = vosk.Model("model")
q = queue.Queue()

# Audio callback function
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Speech recognition function
def recognize_speech():
    q.queue.clear()  
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")
            time.sleep(0.1)  

# Function to generate AI response using Gemini API
def generate_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY_GEMINI}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # Corrected response extraction
        if "candidates" in response_data and response_data["candidates"]:
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "I'm sorry, I didn't understand."
    except Exception as e:
        print("Error generating response:", e)
        return "Error generating response."

# AI conversation handling function
def handle_conversation():
    while True:
        print("Listening...")
        transcript_result = recognize_speech()
        if transcript_result:
            print("User:", transcript_result)

            # Generate AI response using Gemini API
            ai_response = generate_gemini_response(transcript_result)

            # Convert AI response to speech using gTTS
            try:
                print("\nAI:", ai_response)
                tts = gTTS(text=ai_response, lang='en')
                tts.save("response.mp3")
                
                # Initialize Pygame mixer to play the audio response
                pygame.mixer.init()
                pygame.mixer.music.load("response.mp3")
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                print("AI response played.")
            
            except Exception as e:
                print(f"Error during speech playback: {e}")
        else:
            print("No speech recognized.")

# Start the conversation loop
handle_conversation()
