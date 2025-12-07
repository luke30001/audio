#!/usr/bin/env python3
"""
Utility to base64-encode a local audio file for RunPod input.

Usage:
  python3 encode_audio_base64.py path/to/audio.mp3

It prints a JSON payload you can paste into your request.
"""
import base64
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 encode_audio_base64.py <audio_path>", file=sys.stderr)
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}", file=sys.stderr)
        sys.exit(1)

    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")

    payload = {
        "input": {
            "audio_base64": b64,
            "language": "it",
            "task": "transcribe",
            "beam_size": 5,
            "vad_filter": True
        }
    }
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
