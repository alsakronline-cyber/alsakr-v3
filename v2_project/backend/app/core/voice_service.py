import os
import shutil
import asyncio
import edge_tts
from typing import Optional
from faster_whisper import WhisperModel
from fastapi import UploadFile

class VoiceService:
    def __init__(self, model_size: str = "tiny", device: str = "cpu"):
        self.model_size = model_size
        self.device = device
        # Initialize model immediately to cache it in docker build phase if possible, 
        # or lazy load on first request. Lazy load is safer for startup time.
        self.model = None

    def _get_model(self):
        if not self.model:
            print(f"Loading Whisper model {self.model_size} on {self.device}...")
            self.model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
        return self.model

    async def transcribe(self, file: UploadFile) -> str:
        """
        Transcribes an uploaded audio file.
        """
        # Save temp file
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            model = self._get_model()
            # Wrap blocking transcription in a thread to keep event loop free
            segments, info = await asyncio.to_thread(model.transcribe, temp_filename, beam_size=5)
            
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
        finally:
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    async def generate_audio(self, text: str, language: str = "en") -> str:
        """
        Generates audio from text using Edge TTS.
        Returns the path to the generated file.
        """
        voice = "en-US-AriaNeural"
        if any("\u0600" <= c <= "\u06FF" for c in text): # Simple Arabic detection
            voice = "ar-SA-ZariyahNeural"
            
        output_file = f"temp_speech_{os.urandom(4).hex()}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        return output_file
