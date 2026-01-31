# Local Whisper → DeepSeek → gTTS Pipeline

This repository demonstrates a local speech assistant pipeline that:

- Captures audio and performs VAD (Voice Activity Detection).
- Runs a local whisper-style encoder–decoder transformer to transcribe speech.
- Sends the transcribed text to a paid DeepSeek API for semantic processing.
- Converts the API response into speech using `gTTS` and plays it through the speakers.

## Overview

The pipeline is designed for low-latency, local-first transcription with optional cloud processing for intelligence (DeepSeek). Key components:

- Local ASR: Whisper-style encoder-decoder transformer running locally for speech-to-text (STT).
- VAD: Filters out silence and reduces unnecessary transcription calls.
- DeepSeek API: A paid external API that receives text and returns a structured or conversational response.
- TTS: `gTTS` (Google Text-to-Speech) converts the response text to audio.
- Playback: Audio is played back through system speakers using a lightweight audio player.

## Architecture

1. Microphone → VAD: Detect voice segments.
2. Voice segment → Whisper (local): Encode → Decode → Transcribed text.
3. Transcribed text → DeepSeek API (HTTPS request with API key).
4. DeepSeek JSON/text response → gTTS → MP3/WAV.
5. Play generated audio on speakers.

This keeps sensitive raw audio on your machine; only the text (and any metadata you choose to send) leaves locally.

## Features

- Local-first transcription for privacy and responsiveness.
- Simple VAD to avoid transcribing silence.
- Extensible: swap DeepSeek for any paid/private LLM/semantic API.
- Uses standard Python libraries and minimal glue code.

## Requirements

- Python 3.9+
- Microphone and speakers configured on your system

Recommended Python packages (example):

```
pip install openai-whisper webrtcvad gTTS pydub requests sounddevice soundfile
```

Note: replace `openai-whisper` with the specific local Whisper implementation you prefer (e.g., `whisper` package or a custom fork). `pydub` requires `ffmpeg` installed on your system for audio conversions.

## Environment variables

- `DEEPSEEK_API_KEY` — your paid DeepSeek API key (required to call the external API).
- `DEEPSEEK_ENDPOINT` — optional, default as provided by your DeepSeek account.
- `VAD_AGGRESSIVENESS` — VAD sensitivity (0–3) if using `webrtcvad`.

Always keep API keys out of source control. Use environment variables or a secrets manager.

## Example usage

1. Set environment variables (PowerShell example):

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."
$env:DEEPSEEK_ENDPOINT = "https://api.deepseek.example/v1/query"
```

2. Run the assistant (example):

```powershell
python assistant.py --device default --vad 2
```

3. Speak; the system will detect voice, transcribe locally, send the transcription to DeepSeek, and play the TTS reply through speakers.

## Implementation Notes

- Whisper (encoder–decoder): The encoder converts audio features into latent embeddings; the decoder produces the output text autoregressively. Using a local model reduces latency and keeps raw audio private.
- VAD: Use `webrtcvad` to detect speech frames; buffer a short window and only send contiguous voice segments to the transcriber.
- DeepSeek calls: Use `requests` with proper timeouts and exponential backoff for robustness. Sanitize and truncate text where necessary to control cost.
- gTTS: Generates MP3 by default; convert to WAV with `pydub` if your playback library prefers WAV.

## Privacy & Security

- Raw audio stays local to your machine unless you deliberately send it elsewhere.
- Transcribed text and API queries will be sent to DeepSeek and Google TTS (gTTS) services — ensure this aligns with your privacy requirements.
- Store `DEEPSEEK_API_KEY` securely (environment variables, OS keychain, or secret manager). Do not commit keys.

## Troubleshooting

- If `pydub` raises ffmpeg errors, install ffmpeg and ensure it is on your PATH.
- If TTS audio is choppy, check sample rates and convert with `pydub.AudioSegment.set_frame_rate()`.
- For VAD tuning, increase `VAD_AGGRESSIVENESS` for noisier environments.

## Extending the pipeline

- Replace DeepSeek with other LLM APIs (OpenAI, Anthropic, etc.) by changing the API client module.
- Add caching for repeated queries to reduce cost.
- Support multiple output voices by integrating a TTS service that supports voice selection.

## License

This README and example code are provided as-is. Review third-party license terms for `whisper`, `gTTS`, `pydub`, and other dependencies before production use.

---

If you want, I can also:

- Add a `requirements.txt` with the recommended packages.
- Update `assistant.py` with example env var parsing and a minimal run loop showing VAD → whisper → DeepSeek → gTTS flow.

Let me know which you'd prefer next.
