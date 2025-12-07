import base64
import os
import tempfile
import runpod
from faster_whisper import WhisperModel

# Carica il modello una sola volta all'avvio del worker
# Usa "openai/whisper-large-v3-turbo" da Hugging Face. :contentReference[oaicite:5]{index=5}
MODEL_NAME = os.getenv("MODEL_NAME", "openai/whisper-large-v3-turbo")

# Scegli compute_type per bilanciare velocità/memoria
# float16 di solito è ok su GPU moderne
COMPUTE_TYPE = os.getenv("COMPUTE_TYPE", "float16")

model = WhisperModel(
    MODEL_NAME,
    device="cuda",
    compute_type=COMPUTE_TYPE
)

def _download_to_file(url: str, suffix: str = ".audio"):
    # download semplice senza dipendenze extra
    import urllib.request
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    urllib.request.urlretrieve(url, path)
    return path

def handler(event):
    """
    Input atteso:
    {
      "input": {
        "audio_url": "https://...",
        // oppure
        "audio_base64": "<...>",
        "language": "it",
        "task": "transcribe",   // o "translate"
        "beam_size": 5,
        "vad_filter": true
      }
    }
    """
    inp = event.get("input", {}) or {}

    language = inp.get("language")  # es. "it"
    task = inp.get("task", "transcribe")
    beam_size = int(inp.get("beam_size", 5))
    vad_filter = bool(inp.get("vad_filter", True))

    audio_path = None

    try:
        if "audio_url" in inp and inp["audio_url"]:
            audio_path = _download_to_file(inp["audio_url"])
        elif "audio_base64" in inp and inp["audio_base64"]:
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
            vad_filter=vad_filter
        )

        seg_list = []
        text_parts = []
        for s in segments:
            seg_list.append({
                "start": s.start,
                "end": s.end,
                "text": s.text
            })
            text_parts.append(s.text)

        return {
            "text": "".join(text_parts).strip(),
            "language": getattr(info, "language", language),
            "duration": getattr(info, "duration", None),
            "segments": seg_list,
            "model": MODEL_NAME
        }

    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

runpod.serverless.start({"handler": handler})
