from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config.settings import settings
from config.logger import logger

def get_atlas_prompt() -> ChatPromptTemplate:
    """
    Generates the ATLAS central prompt template using global settings.
    Prepared for the LangGraph asynchronous architecture.
    """
    logger.debug("Building a ChatPromptTemplate for the central agent.")
    
    return ChatPromptTemplate.from_messages([
        ("system", settings.SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])