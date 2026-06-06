import pytest
from src.speech.speaker import AtlasSpeaker
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_voice_output():
    """
    Teste de integração isolado para validar a síntese de voz assíncrona.
    """
    logger.info("=== Iniciando Teste de Emissão de Voz da ATLAS ===")
    
    speaker = AtlasSpeaker()
    
    test_phrase = (
        "Sistemas de áudio validados com sucesso, Senhor. "
        "A voz está operando de forma assíncrona na frequência padrão."
    )
    
    logger.info("Disparando reprodução de áudio...")
    await speaker.speak(test_phrase)
    
    logger.info("=== Teste de Emissão de Voz Concluído ===")