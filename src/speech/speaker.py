import edge_tts
import asyncio
import pygame
import os

class AtlasSpeaker:
    def __init__(self, voice="pt-BR-FranciscaNeural"):
        self.voice = voice
        self.output_file = "speech/output.mp3"

    async def speak(self, text):
        """Transforma texto em áudio e reproduz."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(self.output_file)
        
        pygame.mixer.init()
        pygame.mixer.music.load(self.output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(1)
        
        pygame.mixer.quit()
        os.remove(self.output_file)