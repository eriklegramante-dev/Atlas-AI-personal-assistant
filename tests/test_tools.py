import pytest
from src.tools.system_tools import system_diagnostics
from config.logger import logger

@pytest.mark.asyncio
async def test_system_telemetry_tool():
    """
    Validates if the diagnostics tool can correctly read Ubuntu resource data
    and return the properly formatted string telemetry.
    """
    logger.info("=== Starting System Telemetry Tool Integration Test ===")
    
    result = await system_diagnostics.ainvoke(input={})
    
    assert result is not None
    assert "Hardware" in result
    assert "percent" in result
    
    print(f"\n\n[TOOL OUTPUT]: {result}\n")
    logger.info("=== System Telemetry Tool Test Completed Successfully ===")