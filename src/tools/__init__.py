from src.tools.system_tools import system_diagnostics

ATLAS_TOOLS = [system_diagnostics]

TOOLS_MAP = {tool.name: tool for tool in ATLAS_TOOLS}