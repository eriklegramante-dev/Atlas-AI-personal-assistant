# ⚡ ATLAS — Personal Cyber Assistant (v4.0)

ATLAS é um assistente de voz pessoal e autônomo projetado para rodar localmente no ecossistema Linux (Ubuntu/Debian), integrando processamento de linguagem natural por grafos, persistência de memória segura e redundância de motores de IA.

---

## 🎯 Visão Geral

O projeto foi construído com foco em:

- Execução local e privacidade dos dados
- Arquitetura assíncrona de ponta a ponta
- Persistência de memória segura
- Roteamento inteligente entre múltiplos modelos de IA
- Processamento de voz em tempo real
- Facilidade de manutenção e escalabilidade
- Conformidade com os princípios do 12-Factor App

---

## 🛠️ Arquitetura e Engenharia do Sistema

O ATLAS foi totalmente refatorado seguindo os padrões do **12-Factor App**, garantindo isolamento entre código e configuração, portabilidade e facilidade de implantação.

```text
[Usuário] ──(Microfone/sounddevice)──> [src/speech/listener.py] (faster-whisper)
                                                     │
                                                     │ (Texto Puro)
                                                     ▼
[Saída de Voz] <──(edge-tts)── [src/brain/agent_graph.py] (LangGraph)
                                                     │
                         ┌───────────────────────────┴───────────────────────────┐
                         ▼                                                       ▼
      [src/database/brain_database.py]                      [src/brain/model_manager.py]
         (aiosqlite - Memória Local)                          (Ollama / Gemini Flash)
```

---

## 🗂️ Estrutura do Projeto

```text
atlas/
│
├── config/
│   ├── settings.py
│   └── logger.py
│
├── src/
│   ├── brain/
│   │   ├── agent_graph.py
│   │   └── model_manager.py
│   │
│   ├── database/
│   │   └── brain_database.py
│   │
│   ├── speech/
│   │   ├── listener.py
│   │   └── speaker.py
│   │
│   └── tools/
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
└── main.py
```

---

## 📦 Componentes

### Configurações (`config/`)

#### `settings.py`
Responsável pelo gerenciamento centralizado das configurações utilizando Pydantic Settings.

Principais benefícios:

- Validação automática de tipos
- Carregamento seguro via `.env`
- Configuração desacoplada do código
- Facilidade de manutenção

#### `logger.py`
Sistema central de logs com:

- Rotação automática de arquivos
- Limite de 5 MB por arquivo
- Saída colorida no terminal
- Rastreabilidade de erros e eventos

---

### Banco de Dados (`src/database/`)

#### `brain_database.py`

Camada responsável pela memória do ATLAS.

Funcionalidades:

- Persistência assíncrona via `aiosqlite`
- Histórico de conversas
- Memória de curto prazo
- Base para memória de longo prazo
- Operações não bloqueantes

---

### Cérebro (`src/brain/`)

#### `agent_graph.py`

Implementa o núcleo cognitivo utilizando LangGraph.

Responsabilidades:

- Gerenciamento de estados
- Fluxo de raciocínio
- Encadeamento de decisões
- Integração com memória e modelos

#### `model_manager.py`

Gerencia múltiplos provedores de IA.

Estratégia atual:

```text
Ollama (Primário)
        │
        ▼
Gemini Flash (Fallback)
```

Benefícios:

- Alta disponibilidade
- Redundância operacional
- Continuidade do serviço

---

### Voz (`src/speech/`)

#### `listener.py`

Responsável pela entrada de voz.

Tecnologias:

- sounddevice
- faster-whisper

Características:

- Captura em float32
- Baixa latência
- Conversão local de fala para texto

#### `speaker.py`

Responsável pela saída de voz.

Tecnologias:

- edge-tts
- pygame mixer

Características:

- Síntese natural
- Reprodução não bloqueante
- Resposta rápida ao usuário

---

### Ferramentas (`src/tools/`)

Módulo reservado para integrações futuras.

Objetivos:

- Automação local
- Monitoramento do Ubuntu
- Execução de scripts
- Integração ao LangGraph

Status: Em desenvolvimento.

---

## 📡 Status dos Módulos

| Camada | Tecnologia | Status | Observação |
|----------|------------|---------|------------|
| Configurações | Pydantic Settings + .env | 🟢 Operacional | Tipagem validada |
| Logging | RotatingFileHandler | 🟢 Operacional | Logs persistentes |
| Banco de Dados | aiosqlite | 🟢 Operacional | Assíncrono |
| Entrada de Áudio | faster-whisper | 🟢 Operacional | Captura estável |
| Roteamento IA | Ollama → Gemini Flash | 🟢 Operacional | Fallback ativo |
| Grafo Cognitivo | LangGraph | 🟢 Operacional | Estados funcionais |
| Saída de Áudio | edge-tts + pygame | 🟢 Operacional | Não bloqueante |
| Tools | Automação local | 🔴 Pendente | Próxima fase |

---

## 🚀 Instalação

### 1. Clonar o projeto

```bash
git clone https://github.com/seu-usuario/atlas.git
cd atlas
```

### 2. Criar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env`:

```env
GOOGLE_API_KEY=xxxxxxxx
OLLAMA_MODEL=llama3
DATABASE_PATH=data/atlas.db
LOG_LEVEL=INFO
```

---

## ▶️ Execução

```bash
python main.py
```

---

## 🧪 Suíte de Diagnósticos

### Teste de memória

```bash
pytest tests/test_memory_integration.py -s -v
```

### Teste do grafo cognitivo

```bash
pytest tests/test_graph.py -s -v
```

### Teste de síntese de voz

```bash
pytest tests/test_speech.py -s -v
```

---

## 🔒 Segurança

Práticas adotadas:

- Segregação entre código e segredos
- Arquivo `.env` protegido por `.gitignore`
- Execução local sempre que possível
- Logs controlados
- Persistência isolada

---

## 📈 Roadmap

### Fase Atual (v4)

- [x] Arquitetura 12-Factor
- [x] Banco assíncrono
- [x] LangGraph
- [x] STT local
- [x] TTS assíncrono
- [x] Fallback de modelos

### Próxima Fase (v5)

- [ ] Ferramentas de automação Linux
- [ ] Agendamento de tarefas
- [ ] Memória vetorial
- [ ] Sistema de plugins
- [ ] Monitoramento do sistema operacional
- [ ] Painel web administrativo

---

## 🏛️ Filosofia do Projeto

ATLAS foi desenvolvido com foco em autonomia, privacidade, escalabilidade e aprendizado contínuo.

O objetivo é construir um assistente pessoal capaz de operar localmente, compreender contexto ao longo do tempo e integrar múltiplas ferramentas sem dependência obrigatória de serviços externos.

---

## 📄 Licença

Este projeto pode ser distribuído sob a licença MIT ou outra licença definida pelo mantenedor.

---

## 👨‍💻 Autor

Desenvolvido em ambiente estritamente ético (White Hat) e otimizado para aplicações modernas de Inteligência Artificial, automação local e assistentes cognitivos.
