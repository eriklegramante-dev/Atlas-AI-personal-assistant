from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

search = DuckDuckGoSearchRun()

class WebManager:
    """Gerenciador de ferramentas de internet."""
    
    def fetch_tools(self):
        @tool
        def search_web(query: str):
            """Pesquisa na internet por informações em tempo real. 
            Use para notícias, fatos recentes ou dúvidas que não estão na sua memória."""
            return search.run(query)
            
        @tool
        def read_web_page(url: str):
            """
            Lê o conteúdo completo de uma página web ou documentação a partir de uma URL.
            Use esta ferramenta quando precisar analisar detalhes técnicos de um site específico.
            """
            from langchain_community.document_loaders import WebBaseLoader
            
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                return docs[0].page_content[:10000]
            except Exception as e:
                return f"Erro ao ler a página: {e}"

        return [search_web, read_web_page]