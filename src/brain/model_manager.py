from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings
from config.logger import logger

class AtlasModelManager:
    def __init__(self):
        logger.debug(f"Inicializando modelo local Ollama: {settings.OLLAMA_MODEL}")
        self.local_model = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.3
        )
        
        self.cloud_model = None
        if settings.GEMINI_API_KEY:
            logger.debug("Chave Gemini detectada. Inicializando modelo de contingência na nuvem.")
            self.cloud_model = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.3
            )
        else:
            logger.warning("GEMINI_API_KEY não foi configurada no .env. Sistema operando sem fallback na nuvem.")

    def get_model(self, prefer_cloud: bool = False):
        """
        Retorna o modelo ativo. Pode forçar o uso da nuvem se necessário.
        """
        if prefer_cloud and self.cloud_model:
            return self.cloud_model
        return self.local_model

    async def invoke_with_fallback(self, prompt_messages) -> str:
            """
            Tenta processar a requisição no Ollama local. Se falhar ou bater no limite,
            faz o transbordo automático para o Gemini Flash.
            Garante o tratamento do retorno para sempre devolver uma string limpa.
            """
            try:
                logger.debug("Direcionando requisição para o cérebro local (Ollama)...")
                response = await self.local_model.ainvoke(prompt_messages)
                return self._extract_content(response)
                
            except Exception as local_error:
                logger.warning(f"Ollama local indisponível ou limite atingido: {local_error}")
                
                if self.cloud_model:
                    logger.info("Protocolo de transbordo ativado. Acionando Gemini-1.5-Flash na nuvem...")
                    try:
                        response = await self.cloud_model.ainvoke(prompt_messages)
                        return self._extract_content(response)
                    except Exception as cloud_error:
                        logger.critical(f"Falha crítica: Ambos os motores de IA falharam. Erro nuvem: {cloud_error}")
                        return "Senhor, houve uma falha catastrófica em ambos os meus módulos de processamento centrais."
                else:
                    logger.error("Falha no modelo local e nenhum modelo de nuvem configurado para fallback.")
                    return "Senhor, meu módulo local está sobrecarregado e não possuo conexões de contingência ativas."


    def _extract_content(self, response) -> str:
        """Trata e extrai o conteúdo textual bruto de forma resiliente."""
        content = response.content
        
        if isinstance(content, list):
            extracted = []
            for item in content:
                if isinstance(item, dict):
                    extracted.append(item.get("text", str(item)))
                elif hasattr(item, "text"):
                    extracted.append(item.text)
                else:
                    extracted.append(str(item))
            return "".join(extracted).strip()
            
        return str(content).strip()