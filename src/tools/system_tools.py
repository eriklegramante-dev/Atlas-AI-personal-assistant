import psutil
import shutil
from langchain_core.tools import tool
from config.logger import logger

@tool
async def system_diagnostics() -> str:
    """
    Executes a real-time health check on the operating system hardware resources.
    Must be invoked whenever the user queries computer health, memory footprint,
    CPU utilization, available disk space, or central system integrity.
    """
    logger.info("Tool [system_diagnostics] triggered by the agent execution flow.")
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        
        total, used, free = shutil.disk_usage("/")
        disk_free_gb = free // (2**30)
        
        report = (
            f"Hardware diagnostics completed, Sir. "
            f"Current CPU utilization is at {cpu_usage} percent. "
            f"RAM consumption stands at {memory.percent} percent of total capacity. "
            f"The primary partition has {disk_free_gb} gigabytes of free storage available."
        )
        
        logger.debug(f"Telemetry metrics successfully parsed: {cpu_usage}% CPU, {memory.percent}% RAM")
        return report

    except Exception as e:
        logger.error(f"Failed to extract active system hardware metrics: {e}", exc_info=True)
        return "Sir, I failed to access the physical hardware telemetry layers due to an internal execution restriction."