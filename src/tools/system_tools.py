import psutil
import shutil
from langchain_core.tools import tool
from config.logger import logger

@tool
async def diagnostico_sistema() -> str:
    """
    Executa uma verificação em tempo real dos recursos de hardware do sistema operacional.
    Deve ser chamada sempre que o usuário perguntar sobre a saúde do PC, uso de memória,
    status da CPU, espaço em disco ou integridade do sistema.
    """
    logger.info("Ferramenta [diagnostico_sistema] acionada pelo agente.")
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        
        total, used, free = shutil.disk_usage("/")
        disk_free_gb = free // (2**30)
        
        relatorio = (
            f"Diagnóstico de hardware concluído, Senhor. "
            f"O uso atual da CPU está em {cpu_usage}%. "
            f"A memória RAM está com {memory.percent}% de ocupação. "
            f"E o armazenamento principal possui {disk_free_gb} gigabytes disponíveis."
        )
        
        logger.debug(f"Resultado do diagnóstico gerado com sucesso: {cpu_usage}% CPU, {memory.percent}% RAM")
        return relatorio

    except Exception as e:
        logger.error(f"Falha ao executar telemetria do sistema: {e}", exc_info=True)
        return "Senhor, falhei em ler os sensores de hardware do sistema central devido a uma restrição interna."