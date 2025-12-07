# RunPod Serverless Worker - Whisper large-v3-turbo

This repository contains a **custom RunPod Serverless worker** for audio transcription using
**Whisper large-v3-turbo** via **faster-whisper**.

It supports:
- `audio_url` input
- `audio_base64` input
- optional language hint (e.g. `"it"`)
- `transcribe` or `translate`
- segment-level output

---

## Repo structure

```
.
├── handler.py
├── requirements.txt
├── Dockerfile
├── test_request.json
├── .runpod
│   └── tests.json
├── scripts
│   ├── encode_audio_base64.py
│   └── local_smoke_test.py
├── .gitignore
└── LICENSE
```

---

## Input schema

Send to your RunPod endpoint:

```json
{
  "input": {
    "audio_url": "https://example.com/audio.mp3",
    "language": "it",
    "task": "transcribe",
    "beam_size": 5,
    "vad_filter": true
  }
}
```

Or:

```json
{
  "input": {
    "audio_base64": "<BASE64_AUDIO_BYTES>",
    "language": "it"
  }
}
```

### Output

```json
{
  "text": "...",
  "language": "it",
  "duration": 12.34,
  "segments": [
    {"start": 0.0, "end": 2.1, "text": "..." }
  ],
  "model": "openai/whisper-large-v3-turbo"
}
```

---

## Build & push

1. Build locally:

```bash
docker build -t <YOUR_DOCKERHUB_USER>/runpod-whisper-large-v3-turbo:latest .
```

2. Push:

```bash
docker push <YOUR_DOCKERHUB_USER>/runpod-whisper-large-v3-turbo:latest
```

---

## Create RunPod Serverless Endpoint

In the RunPod dashboard:

1. **Serverless → New Endpoint**
2. Choose **Custom Worker**
3. Point to your Docker image
4. Prefer **Queue** type (recommended for transcription jobs)
5. Select a suitable GPU

Environment variables you can set:

- `MODEL_NAME` (default: `openai/whisper-large-v3-turbo`)
- `COMPUTE_TYPE` (default: `float16`)

---

## Tests

The `.runpod/tests.json` file provides a basic test definition you can run in RunPod's
validation flow.

The sample test uses `audio_url`. Replace it with a stable, publicly accessible short audio file
(or switch to `audio_base64`) for deterministic CI-style checks.

---

## License

MIT
