import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from config.settings import settings
from config.logger import logger

class AtlasListener:
    def __init__(self):
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.channels = settings.AUDIO_CHANNELS
        
        logger.info(f"Carregando Modelo Whisper Local [{settings.WHISPER_MODEL_SIZE.upper()}] no dispositivo [{settings.WHISPER_DEVICE.upper()}]...")
        
        try:
            self.model = WhisperModel(
                settings.WHISPER_MODEL_SIZE,
                device=settings.WHISPER_DEVICE,
                compute_type=settings.WHISPER_COMPUTE_TYPE
            )
            logger.info("Modelo Whisper carregado e pronto para transcrição.")
        except Exception as e:
            logger.error(f"Falha ao carregar o modelo Whisper: {e}", exc_info=True)
            raise e

    def _record_audio(self, duration: int = 5) -> np.ndarray:
        """
        Grava um bloco fixo de áudio do microfone padrão do Ubuntu.
        (Módulo base para validação rápida).
        """
        logger.debug(f"Iniciando gravação de {duration}s via sounddevice...")
        try:
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32"
            )
            sd.wait()  
            return audio_data.flatten()
        except Exception as e:
            logger.error(f"Erro ao capturar dados do hardware de som: {e}")
            return np.array([], dtype="float32")

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Recebe o array de áudio bruto e transcreve para texto localmente.
        """
        if audio_data.size == 0:
            return ""

        logger.debug("Enviando áudio bruto para o pipeline do Faster-Whisper...")
        try:
            segments, info = self.model.transcribe(audio_data, beam_size=5, language="pt")
            
            text = "".join([segment.text for segment in segments]).strip()
            
            if text:
                logger.info(f"Transcrição bem-sucedida [Confiança: {info.language_probability:.2f}]: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"Erro durante o processo de transcrição local: {e}")
            return ""

    def listen(self, duration: int = 4) -> str:
        """
        Método interface principal: Escuta por um período e retorna o texto.
        """
        audio = self._record_audio(duration=duration)
        return self.transcribe(audio)