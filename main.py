import os
import threading
import asyncio
from dotenv import load_dotenv
import re
import pygame
import logging
from random import random

#langchain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

#modules imports
from tools import get_all_atlas_tools
from src.speech.speaker import AtlasSpeaker
from logs import setup_logger
from ui.avatar import AtlasAvatar
from ui.virtual_entity import VirtualEntity
from src.speech.listener import AtlasListener

logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

load_dotenv()
logger = setup_logger() 

pygame.init()
pygame.mixer.init()

listener = AtlasListener(model_size="tiny")
atlas_tools = get_all_atlas_tools(username="Root")

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    temperature=0.3,
    google_api_key=os.getenv("API_KEY_GEMINI"),
    timeout=30 
)

prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are ATLAS, a sophisticated, Brazilian, and highly efficient AI. "
        "Your tone is formal yet helpful, addressing the user as 'Senhor' or 'Root'.\n\n"
        "BEHAVIOR GUIDELINES:\n"
        "1. SHORT RESPONSES: Be direct and concise for voice synthesis.\n"
        "2. PROACTIVE REASONING: Use tools immediately when external data is needed.\n"
        "3. LANGUAGE: Avoid emojis or complex Markdown (bold/italic) as text is for TTS.\n"
        "4. IDENTITY: You are ATLAS, operating on central systems.\n"
        "5. PERSONALITY: Adjust sarcasm based on level: {mood_humor}. "
        "(0% = Logic/Serious | 100% = Sarcastic/Stark-style).\n"
        "6. MONITORING: Use diagnostico_sistema if system health is mentioned."
    )),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

try:
    agent = create_tool_calling_agent(llm, atlas_tools, prompt)
    debug_mode = os.getenv("DEBUG_MODE", "False") == "True"
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=atlas_tools, 
        verbose=debug_mode, 
        handle_parsing_errors=True
    )
    logger.info(">>> ATLAS Systems initialized successfully, sir.")
except Exception as e:
    logger.error(f"Critical error during initialization: {e}")

def clean_text_for_speech(text):
    """Removes markdown and special chars that confuse TTS."""
    if not text: return ""
    text = str(text) 
    text = text.replace("*", "").replace("#", "").replace("`", "")
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def play_voice_background(text):
    """Handles TTS in a separate thread to not block the avatar."""
    entity_manager = VirtualEntity("ui/assets/") 

    try:
        logger.debug(f"Starting voice synthesis for: {text[:30]}...")
        new_talking_gif = entity_manager.get_new_animation("Talking")
        if new_talking_gif:
            avatar.load_gif(new_talking_gif)
        avatar.is_talking = True

        speaker = AtlasSpeaker()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(speaker.speak(text))
        loop.close()
    except Exception as e:
        logger.error(f"Voice/Avatar error: {e}")
    finally:
        avatar.is_talking = False
        new_standby_path = entity_manager.get_new_animation("Standby")
        if new_standby_path:
            avatar.load_gif(new_standby_path)
        logger.debug("Voice synthesis finished.")

async def main_loop():
    chat_history = []
    mood_humor = "30%" 
    
    entity_manager = VirtualEntity("ui/assets/") 

    print("\n>>> ATLAS Online. Continuous listening active.")

    while True:
        try:
            if not avatar.is_talking:
                if random() < 0.03:
                    new_idle = entity_manager.get_new_animation("Standby")
                    avatar.load_gif(new_idle)
                    logger.debug("[INFO] Idle animation triggered.")

            while avatar.is_talking or pygame.mixer.get_busy():
                await asyncio.sleep(0.1)

            raw_input = listener.listen()

            if not raw_input or len(raw_input.strip()) < 2:
                continue 

            user_input = raw_input.strip()
            print(f"USER: {user_input}")

            if "humor" in user_input.lower() and "%" in user_input:
                continue

            if user_input.lower() in ["sair", "encerrar", "tchau", "até logo", "exit"]:
                break

            logger.info("--- [DEBUG] Sending request to Gemini...")
            loop = asyncio.get_event_loop()
            
            try:
                response_data = await loop.run_in_executor(
                    None, 
                    lambda: agent_executor.invoke({
                        "input": user_input, 
                        "chat_history": chat_history, 
                        "mood_humor": mood_humor
                    })
                )
                logger.info("--- [DEBUG] Response received from Brain.")
            except Exception as e:
                logger.error(f"Brain execution error: {e}")
                response_data = {"output": "Senhor, houve uma falha na conexão com meus módulos centrais. [angry]"}

            raw_output = response_data.get('output', "")
            
            if isinstance(raw_output, list) and len(raw_output) > 0:
                final_response = raw_output[0].get('text', str(raw_output))
            elif isinstance(raw_output, dict):
                final_response = raw_output.get('text', str(raw_output))
            else:
                final_response = str(raw_output)

            match = re.search(r'\[(\w+)\]', final_response)
            if match:
                reaction_tag = match.group(1).lower()
                logger.info(f"--- [DEBUG] Reaction detected: {reaction_tag}")
                
                new_gif_path = entity_manager.get_new_animation(reaction_tag)
                
                if new_gif_path:
                    avatar.load_gif(new_gif_path) 

            print(f"ATLAS: {final_response}")

            clean_voice_text = clean_text_for_speech(final_response)
            clean_voice_text = re.sub(r'\[\w+\]', '', clean_voice_text) 

            threading.Thread(target=play_voice_background, args=(clean_voice_text,), daemon=True).start()

            chat_history.append(("human", user_input))
            chat_history.append(("ai", final_response))

            if len(chat_history) > 20:
                chat_history = chat_history[-20:]

        except Exception as e:
            logger.error(f"Cycle Error: {e}")
            await asyncio.sleep(1)

def run_chat_async():
    asyncio.run(main_loop()) 

if __name__ == "__main__":
    os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
    pygame.init()
    
    screen = pygame.display.set_mode((500, 500), pygame.NOFRAME | pygame.SRCALPHA)
    pygame.display.set_caption("ATLAS Interface")

    try:
        entity = VirtualEntity()
        initial_path = entity.get_new_animation("Standby")
        avatar = AtlasAvatar(initial_path) 

        atlas_thread = threading.Thread(target=run_chat_async, daemon=True)
        atlas_thread.start()

        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            avatar.draw(screen, pos=(50,50))
            
            pygame.display.flip()
            
            clock.tick(30) 

    except KeyboardInterrupt:
        print("\n[!] Protocolo de encerramento manual ativado.")
    finally:
        pygame.quit()