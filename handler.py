import base64
import os
import tempfile
import runpod
from faster_whisper import WhisperModel

# Allows override via RunPod endpoint env vars
MODEL_NAME = os.getenv("MODEL_NAME", "openai/whisper-large-v3-turbo")
COMPUTE_TYPE = os.getenv("COMPUTE_TYPE", "float16")

# Load once at container start
model = WhisperModel(
    MODEL_NAME,
    device="cuda",
    compute_type=COMPUTE_TYPE,
)

def _download_to_file(url: str, suffix: str = ".audio"):
    import urllib.request
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    urllib.request.urlretrieve(url, path)
    return path

def handler(event):
    """
    Expected input:
    {
      "input": {
        "audio_url": "https://...",
        // or
        "audio_base64": "<...>",
        "language": "it",
        "task": "transcribe",   // or "translate"
        "beam_size": 5,
        "vad_filter": true
      }
    }
    """
    inp = event.get("input", {}) or {}

    language = inp.get("language")  # e.g. "it"
    task = inp.get("task", "transcribe")
    beam_size = int(inp.get("beam_size", 5))
    vad_filter = bool(inp.get("vad_filter", True))

    audio_path = None

    try:
        if inp.get("audio_url"):
            audio_path = _download_to_file(inp["audio_url"])
        elif inp.get("audio_base64"):
            data = base64.b64decode(inp["audio_base64"])
            fd, audio_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            with open(audio_path, "wb") as f:
                f.write(data)
        else:
            return {"error": "Provide audio_url or audio_base64"}

        segments, info = model.transcribe(
            audio_path,
            language=language,
            task=task,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )

        seg_list = []
        text_parts = []
        for s in segments:
            seg_list.append({
                "start": float(s.start),
                "end": float(s.end),
                "text": s.text,
            })
            text_parts.append(s.text)

        return {
            "text": "".join(text_parts).strip(),
            "language": getattr(info, "language", language),
            "duration": getattr(info, "duration", None),
            "segments": seg_list,
            "model": MODEL_NAME,
        }

    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass

runpod.serverless.start({"handler": handler})
