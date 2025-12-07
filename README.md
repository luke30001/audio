# RunPod Serverless Worker - Whisper large-v3-turbo

This repository contains a **custom RunPod Serverless worker** for audio transcription using
**Whisper large-v3-turbo** via **faster-whisper**.

It supports:
- `audio_url` input
- `audio_base64` input
- optional language hint (e.g. `"it"`)
- `transcribe` or `translate`
- segment-level output

## Why this approach?

RunPod Serverless is a good fit for bursty workloads:
you only pay for GPU during execution and can scale with a queue-based endpoint.

`faster-whisper` offers strong performance/latency characteristics for inference.

---

## Repo structure

```
.
├── rp_handler.py
├── requirements.txt
├── Dockerfile
├── test_request.json
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

## Local smoke test (CPU-only fallback)

This worker is intended for CUDA GPUs.
For a quick local logic check (not performance), you can run:

```bash
python3 scripts/local_smoke_test.py --audio-url "https://example.com/audio.mp3"
```

This script will attempt to load the model using `faster-whisper`.
If you don't have CUDA locally, it may fall back or fail depending on your setup.

---

## Notes

- The first request may take longer due to model download (cold start).
- For best latency, ensure your audio URLs are directly downloadable without auth.
- Consider smaller models if your workloads are very short and cost-sensitive.

---

## License

MIT
