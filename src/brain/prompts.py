from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config.settings import settings
from config.logger import logger

def get_atlas_prompt() -> ChatPromptTemplate:
    """
    Gera o template de prompt central da ATLAS utilizando as configurações globais.
    Preparado para a arquitetura assíncrona do LangGraph.
    """
    logger.debug("Construindo ChatPromptTemplate para o agente central.")
    
    return ChatPromptTemplate.from_messages([
        ("system", settings.SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])