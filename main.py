#imports
from dotenv import load_dotenv
import pygame
import logging

#langchain imports
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

#modules imports
from logs import setup_logger


logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

load_dotenv()
logger = setup_logger() 

pygame.init()
pygame.mixer.init()

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

#Todo o main será refeito