import json
import aiosqlite
from pathlib import Path
from config.settings import settings
from config.logger import logger

class AtlasBrain:
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        self.db_path = db_path

    async def initialize_db(self):
        """Inicializa as tabelas do banco de dados de forma assíncrona."""
        logger.debug(f"Conectando ao banco de dados seguro em: {self.db_path}")
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_profile (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL DEFAULT 'default',
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                await conn.commit()
            logger.info("Banco de dados da ATLAS inicializado e protegido contra Git.")
        except Exception as e:
            logger.error(f"Falha crítica ao inicializar o banco de dados: {e}", exc_info=True)
            raise e

    async def add_message(self, role: str, content: str, session_id: str = "default"):
        """Adiciona uma mensagem ao histórico da sessão atual (human ou ai)."""
        logger.debug(f"Registrando mensagem no histórico [{session_id}]: {role}")
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                    (session_id, role, content)
                )
                await conn.commit()
        except Exception as e:
            logger.error(f"Falha ao registrar mensagem no banco: {e}")

    async def get_chat_history(self, session_id: str = "default", limit: int = 20) -> list[dict]:
        """
        Recupera as últimas mensagens da sessão para alimentar o prompt.
        Retorna uma lista de dicionários estruturados por data.
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                query = """
                    SELECT role, content FROM (
                        SELECT id, role, content FROM chat_history 
                        WHERE session_id = ? 
                        ORDER BY id DESC LIMIT ?
                    ) ORDER BY id ASC
                """
                async with conn.execute(query, (session_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    return [{"role": row[0], "content": row[1]} for row in rows]
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico da sessão {session_id}: {e}")
            return []

    async def clear_session_history(self, session_id: str = "default"):
        """Limpa a memória de curto prazo de uma sessão específica."""
        logger.warning(f"Protocolo de limpeza de memória ativado para a sessão: {session_id}")
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
                await conn.commit()
            logger.info(f"Histórico da sessão {session_id} foi completamente limpo.")
        except Exception as e:
            logger.error(f"Erro ao limpar histórico da sessão {session_id}: {e}")

    async def store_fact(self, key: str, value: str):
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, value))
                await conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar fato '{key}' no banco: {e}")

    async def get_fact(self, key: str) -> str | None:
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("SELECT value FROM user_profile WHERE key = ?", (key,)) as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"Erro ao recuperar fato '{key}': {e}")
            return None