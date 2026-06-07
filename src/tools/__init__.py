from src.tools.system_tools import diagnostico_sistema

ATLAS_TOOLS = [diagnostico_sistema]

TOOLS_MAP = {tool.name: tool for tool in ATLAS_TOOLS}