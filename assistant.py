import sounddevice as sd
import numpy as np
import soundfile as sf
import subprocess
import requests
import os
import time
from gtts import gTTS

# =========================
# CONFIGURATION
# =========================
#
DEEPSEEK_API_KEY = ""
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

SAMPLE_RATE = 16000
RECORD_SECONDS = 5

# USB microphone (confirmed)
MIC_DEVICE_INDEX = 3  # UACDemoV1.0

# Whisper.cpp
WHISPER_BIN = "/home/pi/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "/home/pi/whisper.cpp/models/ggml-small.en.bin"

AUDIO_FILE = "input.wav"
TEXT_FILE = "result.txt"
TTS_FILE = "tts.mp3"

# =========================
# RECORD AUDIO
# =========================
def record_audio():
    print(" Speak now...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.int16,
        device=MIC_DEVICE_INDEX
    )
    sd.wait()
    sf.write(AUDIO_FILE, audio, SAMPLE_RATE)
    return np.abs(audio).mean()

# =========================
# SPEECH TO TEXT
# =========================
def speech_to_text():
    if os.path.exists(TEXT_FILE):
        os.remove(TEXT_FILE)

    subprocess.run(
        [
            WHISPER_BIN,
            "-m", WHISPER_MODEL,
            "-f", AUDIO_FILE,
            "-otxt",
            "-of", "result"
        ],
        check=True
    )

    if not os.path.exists(TEXT_FILE):
        return ""

    with open(TEXT_FILE, "r") as f:
        return f.read().strip()

# =========================
# DEEPSEEK (SUMMARIZED)
# =========================
def ask_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Respond in English only. "
                    "Keep answers short (1–2 sentences). "
                    "Be conversational, clear, and natural. "
                    "Do not give long explanations unless asked."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    r = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# =========================
# gTTS (FREE, RELIABLE)
# =========================
def speak(text):
    if not text.strip():
        return

    # Generate speech
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(TTS_FILE)

    # Force playback through ALSA
    os.system(f"mpg123 -q {TTS_FILE}")

# =========================
# MAIN LOOP
# =========================
print("\n System ready.")
print("USB mic locked to card 3.")
print("Press ENTER to record. Ctrl+C to exit.\n")

while True:
    try:
        input(" Press ENTER to start recording...")
        energy = record_audio()

        if energy < 50:
            print(" Audio too quiet. Speak louder.")
            continue

        text = speech_to_text()
        print("You said:", text)

        if not text:
            print(" No transcription.")
            continue

        reply = ask_deepseek(text)
        print("AI:", reply)
        speak(reply)

        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n Exiting safely.")
        break

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
