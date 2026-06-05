import io
import speech_recognition as sr
from faster_whisper import WhisperModel
import faster_whisper
import torch

class AtlasListener:
    def __init__(self, model_size="base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = WhisperModel(model_size, device=self.device, compute_type="int8")
        self.model = faster_whisper.WhisperModel(model_size, device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=16000)

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5) 
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.6
            
            print("\n[OUVINDO COMANDO...]")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return ""

        try:
            print("[PROCESSANDO...]")
            audio_data = io.BytesIO(audio.get_wav_data())
            
            segments, info = self.model.transcribe(
                audio_data, 
                beam_size=5, 
                language="pt",
                initial_prompt="O usuário está falando com a ATLAS, um assistente inteligente. Comandos comuns: sistemas, luzes, pesquisa, Root.",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                condition_on_previous_text=False, 
                repetition_penalty=1.2,           
                no_speech_threshold=0.6          
            )
            
            full_text = "".join([segment.text for segment in segments])
            return full_text.strip()
        
        except Exception as e:
            print("Erro na transcrição:", e)
            return ""
    
        