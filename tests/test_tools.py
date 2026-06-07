import pytest
from src.tools.system_tools import diagnostico_sistema
from config.logger import logger

@pytest.mark.asyncio
async def test_system_telemetry_tool():
    """
    Valida se a ferramenta de diagnóstico consegue ler os dados do Ubuntu
    e retornar a string formatada corretamente.
    """
    logger.info("=== Iniciando Teste de Ferramenta de Sistema ===")
    
    resultado = await diagnostico_sistema.ainvoke(input={})
    
    assert resultado is not None
    assert "Diagnóstico" in resultado
    assert "%" in resultado
    
    print(f"\n\n[TOOL OUTPUT]: {resultado}\n")
    logger.info("=== Teste de Ferramenta Concluído com Sucesso ===")