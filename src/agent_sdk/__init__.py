"""agent-sdk — SDK para construção de agentes.

Exports principais:
    - tool: decorator para registrar ferramentas
    - ToolResult: resultado padronizado de ferramenta
    - ToolExecutionError: erro controlado de ferramenta
    - ToolSpec: especificação de ferramenta registrada
"""

from agent_sdk.decorators import clear_registry, get_registry, tool
from agent_sdk.types import ToolExecutionError, ToolResult, ToolSpec

__version__ = "0.1.0"

__all__ = [
    "tool",
    "ToolResult",
    "ToolExecutionError",
    "ToolSpec",
    "get_registry",
    "clear_registry",
]