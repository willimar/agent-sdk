"""Decorator @tool para registro de ferramentas.

Uso:
    from agent_sdk import tool

    @tool("google_calendar_list_events")
    def listar_eventos(qtd: int = 5) -> str:
        \"\"\"Busca os próximos eventos na agenda.\"\"\"
        ...
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

from agent_sdk.types import ToolSpec

# Registry global. O platform-core importa e lê daqui.
_GLOBAL_REGISTRY: dict[str, ToolSpec] = {}


def _extrair_tipo(param: inspect.Parameter) -> str:
    """Extrai o nome do tipo de um parâmetro."""
    if param.annotation is inspect.Parameter.empty:
        return "Any"
    annotation = param.annotation
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    return str(annotation)


def _extrair_parametros(funcao: Callable) -> dict[str, Any]:
    """Inspeciona a assinatura da função e extrai schema dos parâmetros."""
    sig = inspect.signature(funcao)
    params: dict[str, Any] = {}

    for nome, param in sig.parameters.items():
        if nome in ("self", "cls"):
            continue
        params[nome] = {
            "tipo": _extrair_tipo(param),
            "default": param.default if param.default is not inspect.Parameter.empty else None,
            "obrigatorio": param.default is inspect.Parameter.empty,
        }

    return params


def _extrair_descricao(funcao: Callable) -> tuple[str, str]:
    """Extrai descrição curta e completa da docstring.

    Returns:
        Tupla (descricao_curta, descricao_completa).
    """
    doc = inspect.getdoc(funcao) or ""
    linhas = doc.strip().split("\n") if doc.strip() else []
    curta = linhas[0].strip() if linhas else funcao.__name__
    completa = doc.strip() if doc else f"Ferramenta: {funcao.__name__}"
    return curta, completa


def tool(nome: str) -> Callable:
    """Decorator que registra uma função como ferramenta.

    Args:
        nome: Nome único da ferramenta. Convenção:
              <dominio>_<acao>[_<qualificador>] em snake_case.

    Returns:
        Decorator que registra a função no registry global.

    Raises:
        ValueError: Se o nome for inválido ou já estiver registrado.

    Example:
        @tool("file_read_text")
        def ler_arquivo(caminho: str) -> str:
            \"\"\"Lê o conteúdo de um arquivo texto.\"\"\"
            ...
    """

    def decorator(funcao: Callable) -> Callable:
        # Validação do nome
        if not nome or not nome.strip():
            raise ValueError("Nome da ferramenta não pode ser vazio")
        if " " in nome:
            raise ValueError(f"Nome da ferramenta não pode conter espaços: '{nome}'")
        if nome in _GLOBAL_REGISTRY:
            raise ValueError(f"Ferramenta '{nome}' já está registrada")

        # Extrai metadados
        descricao_curta, descricao_completa = _extrair_descricao(funcao)
        parametros = _extrair_parametros(funcao)

        # Cria a spec e registra
        spec = ToolSpec(
            nome=nome,
            descricao=descricao_curta,
            descricao_completa=descricao_completa,
            parametros=parametros,
            funcao=funcao,
        )
        _GLOBAL_REGISTRY[nome] = spec

        # Anexa metadata na função pra introspecção
        funcao._tool_spec = spec  # type: ignore[attr-defined]
        funcao._tool_name = nome  # type: ignore[attr-defined]

        return funcao

    return decorator


def get_registry() -> dict[str, ToolSpec]:
    """Retorna o registry global de ferramentas.

    Usado pelo platform-core para descobrir ferramentas registradas.
    """
    return _GLOBAL_REGISTRY.copy()


def clear_registry() -> None:
    """Limpa o registry global. Usado apenas em testes."""
    _GLOBAL_REGISTRY.clear()
