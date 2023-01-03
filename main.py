import whisper
import ffmpeg

model = whisper.load_model("tiny")

def transcribe(audio):

    transcription = model.transcribe(audio)

    return transcription["text"]