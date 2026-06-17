import os
import asyncio
import edge_tts
import pygame
from pathlib import Path
from config.settings import settings
from config.logger import logger

class AtlasSpeaker:
    def __init__(self):
        self.voice = settings.EDGE_TTS_VOICE
        self.base_path = settings.BASE_PATH
        
        self.temp_audio_path = self.base_path / ".atlas_voice_cache.mp3"
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            logger.debug("Pygame Mixer inicializado no módulo do Speaker.")

    async def speak(self, text: str):
        """
        Recebe o texto gerado pela IA, sintetiza assincronamente via Edge-TTS,
        salva no cache e realiza a reprodução em background.
        """
        if not text or len(text.strip()) == 0:
            return

        logger.debug(f"Iniciando síntese de voz Edge-TTS para o texto: '{text[:30]}...'")
        
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate="+5%")
            await communicate.save(str(self.temp_audio_path))
            
            logger.debug("Áudio sintetizado com sucesso. Iniciando reprodução...")
            
            pygame.mixer.music.load(str(self.temp_audio_path))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
            pygame.mixer.music.unload()
            
            if os.path.exists(self.temp_audio_path):
                os.remove(self.temp_audio_path)
                
            logger.debug("Reprodução de voz concluída e cache limpo.")
            
        except Exception as e:
            logger.error(f"Falha no pipeline de síntese/reprodução de voz: {e}", exc_info=True)