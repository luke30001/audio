#!/usr/bin/env python3
"""
Local smoke test for the transcription logic.

This is NOT a full RunPod simulation, but helps you validate:
- model load call
- input parsing
- output assembly

Usage:
  python3 local_smoke_test.py --audio-url "https://example.com/audio.mp3" --language it

Notes:
- Needs ffmpeg available.
- If you don't have CUDA, faster-whisper may fail depending on your setup.
"""
import argparse
import json
import os
import tempfile
from faster_whisper import WhisperModel

def download(url: str):
    import urllib.request
    fd, path = tempfile.mkstemp(suffix=".audio")
    os.close(fd)
    urllib.request.urlretrieve(url, path)
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-url", required=True)
    ap.add_argument("--language", default=None)
    ap.add_argument("--task", default="transcribe")
    ap.add_argument("--beam-size", type=int, default=5)
    ap.add_argument("--vad-filter", action="store_true", default=True)
    ap.add_argument("--model", default="openai/whisper-large-v3-turbo")
    ap.add_argument("--compute-type", default="float16")
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    audio_path = download(args.audio_url)

    try:
        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
        )

        segments, info = model.transcribe(
            audio_path,
            language=args.language,
            task=args.task,
            beam_size=args.beam_size,
            vad_filter=args.vad_filter,
        )

        segs = []
        texts = []
        for s in segments:
            segs.append({"start": float(s.start), "end": float(s.end), "text": s.text})
            texts.append(s.text)

        out = {
            "text": "".join(texts).strip(),
            "language": getattr(info, "language", args.language),
            "duration": getattr(info, "duration", None),
            "segments": segs,
            "model": args.model,
        }

        print(json.dumps(out, indent=2, ensure_ascii=False))

    finally:
        try:
            os.remove(audio_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
