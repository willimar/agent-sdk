# agent-sdk

SDK para construção de agentes compatíveis com a Agent Platform.
Fornece o contrato, os tipos compartilhados, o decorator de
ferramentas e um template para criar agentes novos em minutos.

Se você quer **criar um agente**, comece aqui.

---

## Instalação

```bash
uv add agent-sdk

# Ou a partir do repositório:

uv add git+https://github.com/<org>/agent-sdk.git
```

## Quick start — criar um agente em 5 minutos

### 1. Gere o boilerplat

```bash
uv run agent-sdk init meu-primeiro-agente
```

**Isso cria:**

```
meu-primeiro-agente/
├── agent.yaml
├── tools/
│   ├── __init__.py
│   └── example.py
├── tests/
│   └── test_example.py
├── requirements.txt
└── README.md
```

### Edite o `agent.yaml`

```yaml
nome: "Meu Primeiro Agente"
versao: "0.1.0"
modelo: "llama3.1:8b"
instrucoes: >
  Você é um assistente que responde perguntas simples.
ferramentas:
  - meu_agente_responder
tarefa:
  descricao: "Responda a pergunta do usuário."
  saida_esperada: "Resposta direta e concisa."
```

### 3. Implemente a ferramenta

```python
# tools/example.py
from agent_sdk import tool

@tool("meu_agente_responder")
def responder(pergunta: str) -> str:
    """Responde uma pergunta simples (mock)."""
    return f"Você perguntou: {pergunta}"
```

### 4. Execute

```bash
uv run platform run ./meu-primeiro-agente/agent.yaml
```
## API do SDK

Decorator `@tool`

```python
from agent_sdk import tool

@tool("nome_da_ferramenta")
def minha_funcao(param1: str, param2: int = 10) -> str:
    """Primeira linha vira a descrição pro LLM.

    Args:
        param1: Descrição do primeiro parâmetro.
        param2: Descrição do segundo parâmetro.

    Returns:
        Descrição do retorno.
    """
    ...
```

*Regras:*

* Nome em snake_case com prefixo de domínio
* Docstring obrigatória (primeira linha = descrição)
* Type hints obrigatórios em todos os parâmetros
* Retorno: str ou dict[str, Any]
* Erros: lançar ToolExecutionError

## Tipos

```python
from agent_sdk.types import ToolResult, ToolExecutionError

# Retorno padronizado
resultado = ToolResult(
    sucesso=True,
    dados={"eventos": [...]},
    duracao_ms=234.5,
)

# Erro controlado
raise ToolExecutionError("API fora do ar", retry=True)
```

## Testes

```python
from agent_sdk.testing import mock_llm, mock_tool_registry

def test_meu_agente():
    with mock_llm(resposta='{"acao": "finalizar", "resposta": "ok"}'):
        # executa o agente com LLM fake
        ...
```

## Estrutura

```
src/
└── agent_sdk/
    ├── __init__.py             # exporta: tool, ToolResult, ToolExecutionError
    ├── base.py                 # protocolo de agente
    ├── decorators.py           # implementação do @tool
    ├── types.py                # ToolResult, ToolExecutionError, AgentConfig
    └── testing.py              # helpers de teste (mocks)

templates/
└── agent-template/             # boilerplate do `agent-sdk init`
    ├── agent.yaml
    ├── tools/
    │   ├── __init__.py
    │   └── example.py
    ├── tests/
    │   └── test_example.py
    ├── requirements.txt
    └── README.md

pyproject.toml
README.md
```

## Contrato com a plataforma

O `agent-sdk` define o contrato entre agentes e `platform-core`:

```
┌────────────────┐         ┌────────────────┐
│  agent-sdk     │◄────────│  *-agent repos │
│  (contrato)    │         │  (implementam) │
└───────┬────────┘         └────────────────┘
        │
        │  importa
        ▼
┌────────────────┐
│ platform-core  │
│ (consome)      │
└────────────────┘
```

* Agentes importam `agent-sdk` pra definir ferramentas
* `platform-core` importa `agent-sdk` pra validar e executar
* Nenhum agente importa `platform-core` diretamente

## Desenvolvimento

```bash
uv sync --group dev
uv run pytest
uv run ruff check src/
uv run ruff format src/
```

## Convenção de nomenclatura de ferramentas

```
<dominio>_<acao>[_<qualificador>]

google_calendar_list_events
youtube_upload_video
file_read_text
http_get
```

Detalhes em: [platform-docs/tool-contract.md](https://github.com/%3Corg%3E/platform-docs/blob/main/tool-contract.md).

## Versão
`v0.1.0`

Repositórios relacionados
 | Repo | Propósito | 
 | ------ | ------ | 
 | `platform-docs` | Documentação e ADRs | 
 | `platform-core` | Motor de execução | 
 | `google-calendar-agent` | Primeiro agente funcional | 

## Licença
