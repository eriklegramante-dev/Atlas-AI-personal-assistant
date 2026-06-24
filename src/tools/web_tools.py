from langchain_core.tools import tool

class WebManager:
    """Internet tool manager."""
    
    def fetch_tools(self):
        @tool
        def search_web(query: str):
            pass