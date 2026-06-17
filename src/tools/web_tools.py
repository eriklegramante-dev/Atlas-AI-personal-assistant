from langchain_core.tools import tool

class WebManager:
    """Gerenciador de ferramentas de internet."""
    
    def fetch_tools(self):
        @tool
        def search_web(query: str):
            pass