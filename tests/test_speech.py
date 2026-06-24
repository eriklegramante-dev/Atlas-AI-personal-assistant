import pytest
from src.speech.speaker import AtlasSpeaker
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_voice_output():
    """
    Isolated integration test to validate the asynchronous voice synthesis layer.
    """
    logger.info("=== Starting ATLAS Voice Output Emission Test ===")
    
    speaker = AtlasSpeaker()
    
    test_phrase = (
        "Audio emission subsystems successfully validated, Sir. "
        "The voice synthesizer is operating asynchronously at standard frequency parameters."
    )
    
    logger.info("Triggering asynchronous audio stream playback...")
    await speaker.speak(test_phrase)
    
    logger.info("=== ATLAS Voice Output Emission Test Completed ===")