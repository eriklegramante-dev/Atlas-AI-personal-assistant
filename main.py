import asyncio
from src.database.brain_database import AtlasBrain
from src.speech.listener import AtlasListener
from config.logger import logger

async def main_execution():
    logger.info("=== Iniciando Protocolo de Teste Integrado: ATLAS ===")
    
    brain = AtlasBrain()
    await brain.initialize_db()
    
    listener = AtlasListener()
    
    print("\n>>> FALE ALGO AGORA (Gravação ativa por 4 segundos)...")
    user_speech = listener.listen(duration=4)
    
    if user_speech:
        print(f"\n[STT RESULT] O que você disse: {user_speech}")
        await brain.add_message(role="human", content=user_speech)
    else:
        logger.warning("Nenhum sinal de voz detectado ou transcrito.")

    history = await brain.get_chat_history()
    logger.info(f"Total de interações salvas no histórico seguro: {len(history)}")

if __name__ == "__main__":
    asyncio.run(main_execution())