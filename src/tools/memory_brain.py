from langchain_core.tools import tool
from src.brain.memory_manager import AtlasBrain

brain = AtlasBrain()

class MemoryManager:
    def fetch_tools(self):
        
        @tool
        def remember_fact(key: str, value: str):
            """
            Guarda uma informação importante sobre o usuário ou o sistema no banco de dados.
            Use isso para lembrar nomes, preferências, datas de viagens ou lembretes permanentes.
            Exemplo: key='viagem_paris', value='Junho de 2026'
            """
            try:
                brain.store_fact(key, value)
                return f"Entendido, senhor. Memorizei que {key} é {value}."
            except Exception as e:
                return f"Erro ao acessar meus módulos de memória: {e}"

        @tool
        def retrieve_fact(key: str):
            """
            Recupera uma informação guardada anteriormente na memória.
            Use quando o usuário perguntar algo que você já deveria saber.
            """
            fact = brain.get_fact(key)
            if fact:
                return f"Minha base de dados indica: {fact}"
            return "Não encontrei nenhum registro sobre isso em minha memória, senhor."
        

        return [remember_fact, retrieve_fact]