from .system_tools import SystemManager
from .web_tools import WebManager
from .memory_brain import MemoryManager 

def get_all_atlas_tools(username="Root"):
    sys_m = SystemManager(username=username)
    web_m = WebManager()
    mem_m = MemoryManager()
    
    return sys_m.fetch_tools() + web_m.fetch_tools() + mem_m.fetch_tools()