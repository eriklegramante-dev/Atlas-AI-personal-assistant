from langchain_core.tools import tool
from datetime import datetime

import os
import shutil
import platform
import subprocess
import psutil

class SystemManager:
    def __init__(self, username="Senhor"):
        self.username = username

    def fetch_tools(self):
        """
        Gera e retorna a lista de ferramentas. 
        As funções internas utilizam o 'self.username'.
        """
        
        @tool
        def get_personal_info():
            """Gera uma saudação personalizada para o dono da Atlas ."""
            return f"Bem vindo de volta, senhor {self.username}."
        
        @tool
        def check_disk_space():
            """Verifica o espaço em disco disponível no sistema."""
            total, used, free = shutil.disk_usage("/")
            
            total_gb = total // (2**30)
            used_gb = used // (2**30)
            free_gb = free // (2**30)

            return (f"Espaço total: {total_gb} GB, "
                    f"Espaço usado: {used_gb} GB, "
                    f"Espaço livre: {free_gb} GB")
    
        @tool
        def get_date_by_city(city: str):
            """Retorna a data e hora atual. Útil para quando o usuário pergunta que dia é hoje ou a hora."""
            current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            return f"A data e hora atual (baseada no sistema) para {city} é: {current_date}"

        @tool
        def verify_user_access(user: str):
            """Verifica se o usuário é autorizado a usar a Atlas, utilizará codigo de acesso '06' para liberar acesso a funções sensíveis."""
            authorized_users = ["root", "legramante"] 
            if user.lower() in authorized_users:
                return f"Usuário {user} verificado. Acesso concedido."
            else:
                return f"Usuário {user} não autorizado. Protocolo de segurança ativado."
            
        @tool
        def list_directory_files(directory_path: str):
            """Lista os arquivos em um diretório específico."""
            try:
                files = os.listdir(directory_path)
                return f"Arquivos em {directory_path}: {', '.join(files)}"
            except Exception as e:
                return f"Erro ao listar arquivos em {directory_path}: {str(e)}"

        @tool
        def get_system_specs():
            """Retorna informações básicas do sistema e hardware."""
            specs = {
                "Sistema Operacional": platform.system(),
                "Versão": platform.version(),
                "Arquitetura": platform.architecture()[0],
                "Processador": platform.processor()
            }
            return specs
        
        @tool
        def get_current_datetime():
            """Retorna a data e hora atual do sistema."""
            return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        @tool
        def turn_off():
            """Desliga o sistema. Use com cautela."""
            os.system("shutdown /s /t 1") 
            return "Iniciando protocolo de desligamento. Até a próxima, senhor!"
        
        @tool
        def move_atlas(direcao: str):
            """
            Move a janela da ATLAS para posições específicas na tela.
            Argumentos: direcao (str) - 'direita', 'esquerda', 'centro', 'topo' ou 'fundo'.
            """
            try:
                window_id = subprocess.check_output(["xdotool", "search", "--name", "pygame window"]).decode().split()[0]
                
                coords = {
                    "esquerda": "100 100",
                    "direita": "1200 100",
                    "centro": "500 300",
                    "fundo": "500 700"
                }
                
                pos = coords.get(direcao.lower(), "100 100")
                
                subprocess.run(["xdotool", "windowmove", window_id] + pos.split())
                subprocess.run(["xdotool", "windowactivate", window_id])
                
                return f"Sistemas realinhados para a {direcao}, senhor."
            except Exception as e:
                return "Senhor, não consegui localizar a assinatura da minha janela no servidor X11."
            
        @tool
        def system_diagnostics():
            """Realiza um diagnóstico rápido do sistema e retorna um resumo."""
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                ram_usage = psutil.virtual_memory()

                monitor = subprocess.check_output("xrandr --listmonitors", shell=True).decode()

                status = (
                    f"Senhor, a CPU está operando em {cpu_usage}%. "
                    f"O uso de memória RAM está em {ram_usage.percent}%. "
                    f"Detectei a seguinte configuração de exibição:\n{monitor}"
                )
                return status
            except Exception as e:
                return f"Erro ao realizar diagnóstico do sistema: {str(e)}"

        return [
            get_personal_info, 
            check_disk_space, 
            get_date_by_city, 
            verify_user_access, 
            list_directory_files, 
            get_system_specs,
            get_current_datetime,
            turn_off,
            move_atlas,
            system_diagnostics,
        ]