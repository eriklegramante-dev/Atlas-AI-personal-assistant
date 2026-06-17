import asyncio
import sys
from config.settings import settings
from config.logger import logger
from src.database.brain_database import AtlasBrain
from src.brain.agent_graph import AtlasBrainGraph
from src.speech.listener import AtlasListener
from src.speech.speaker import AtlasSpeaker

async def core_loop():
    logger.info("=== SISTEMA OPERACIONAL ATLAS INICIADO ===")
    
    try:
        brain_db = AtlasBrain()
        await brain_db.initialize_db()
        
        listener = AtlasListener()
        speaker = AtlasSpeaker()
        graph = AtlasBrainGraph()
        
        session_id = "main_terminal_root"
        
        logger.info("Todos os sistemas centrais inicializados e estáveis. Pronto para escuta.")
        await speaker.speak("Sistemas inicializados, Senhor. Aguardando diretrizes.")
        
    except Exception as e:
        logger.critical(f"Falha catastrófica na inicialização do sistema: {e}", exc_info=True)
        sys.exit(1)

    while True:
        try:
            print("\n" + "="*50)
            print(">>> ATLAS está ouvindo... (Fale agora)")
            print("="*50 + "\n")
            
            user_input = listener.listen(duration=4)
            
            if not user_input or len(user_input.strip()) == 0:
                await asyncio.sleep(0.5)
                continue
                
            if any(cmd in user_input.lower() for cmd in ["desligar sistema", "encerrar atlas", "dormir atlas"]):
                logger.warning("Protocolo de desligamento ordenado pelo operador.")
                await speaker.speak("Encerrando operações locais e salvando logs. Até logo, Root.")
                break

            chat_history = await brain_db.get_chat_history(session_id=session_id, limit=10)
            
            response_text = await graph.execute(
                user_input=user_input,
                history_raw=chat_history,
                humor="30%" 
            )
            
            if response_text:
                await brain_db.add_message(role="human", content=user_input, session_id=session_id)
                await brain_db.add_message(role="ai", content=response_text, session_id=session_id)
                
                await speaker.speak(response_text)
            
            await asyncio.sleep(0.5)
            
        except KeyboardInterrupt:
            logger.warning("Interrupção manual detectada (Ctrl+C). Salvando estado e saindo.")
            break
        except Exception as e:
            logger.error(f"Erro inesperado no loop de execução: {e}", exc_info=True)
            await asyncio.sleep(2)
if __name__ == "__main__":
    try:
        asyncio.run(core_loop())
    except KeyboardInterrupt:
        print("\n[ATLAS] Operação abortada pelo usuário.")