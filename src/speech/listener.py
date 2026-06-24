import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from config.settings import settings
from config.logger import logger

class AtlasListener:
    def __init__(self):
        self.model_size = "small" 
        logger.info(f"Loading phonetic transcription template Faster-Whisper ({self.model_size})...")
        
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        self.sample_rate = 16000 
        
        self.phonetic_prompt = "ATLAS, Root, Root-Alpha, Linux, Ubuntu, Python, White Hat, hardware, CPU, RAM."

    def listen(self, duration: int = 4) -> str:
        """It captures audio from the hardware and transcribes it by applying phonetic filters."""
        try:
            logger.debug(f"Microphone activated. Capturing stream by {duration} seconds...")
            
            audio_data = sd.rec(
                int(duration * self.sample_rate), 
                samplerate=self.sample_rate, 
                channels=1, 
                dtype='float32'
            )
            sd.wait() 
            
            audio_segments = audio_data.flatten()
            
            segments, info = self.model.transcribe(
                audio_segments,
                language="pt",                 
                beam_size=5,                   
                initial_prompt=self.phonetic_prompt 
            )
            
            transcription = "".join([segment.text for segment in segments]).strip()
            
            if transcription:
                logger.info(f"[STT RAW]: {transcription}")
            return transcription

        except Exception as e:
            logger.error(f"Audio capture or transcription failure: {e}", exc_info=True)
            return ""