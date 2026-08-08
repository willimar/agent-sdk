"""Tipos compartilhados da agent-sdk.

Estes tipos formam o contrato entre ferramentas, agentes e a plataforma.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Resultado padronizado de uma ferramenta.

    Toda ferramenta deve retornar um ToolResult ou uma string/dict
    que será convertido automaticamente pelo registry.

    Attributes:
        sucesso: True se a ferramenta executou sem erros.
        dados: Resultado útil (string ou dicionário).
        erro: Mensagem de erro, se houver.
        duracao_ms: Tempo de execução em milissegundos.
    """

    sucesso: bool
    dados: str | dict[str, Any]
    erro: str | None = None
    duracao_ms: float = 0.0

    @classmethod
    def ok(cls, dados: str | dict[str, Any], duracao_ms: float = 0.0) -> ToolResult:
        """Cria um resultado de sucesso."""
        return cls(sucesso=True, dados=dados, duracao_ms=duracao_ms)

    @classmethod
    def falha(cls, erro: str, duracao_ms: float = 0.0) -> ToolResult:
        """Cria um resultado de erro."""
        return cls(sucesso=False, dados="", erro=erro, duracao_ms=duracao_ms)

    def to_prompt_text(self) -> str:
        """Converte o resultado em texto para injetar no prompt do LLM."""
        if self.sucesso:
            if isinstance(self.dados, dict):
                import json
                return json.dumps(self.dados, ensure_ascii=False, indent=2)
            return str(self.dados)
        return f"ERRO: {self.erro}"


class ToolExecutionError(Exception):
    """Erro controlado durante execução de uma ferramenta.

    A ferramenta deve lançar esta exceção quando encontra um erro
    recuperável ou não-recuperável. O motor de execução decide se
    faz retry com base no flag `retry`.

    Attributes:
        mensagem: Descrição do erro.
        retry: Se True, o motor pode tentar novamente.
    """

    def __init__(self, mensagem: str, retry: bool = False):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.retry = retry


@dataclass
class ToolSpec:
    """Especificação de uma ferramenta registrada.

    Contém todos os metadados necessários para o LLM decidir
    quando e como usar a ferramenta.

    Attributes:
        nome: Identificador único da ferramenta.
        descricao: Descrição curta (primeira linha da docstring).
        descricao_completa: Docstring completa.
        parametros: Schema dos parâmetros (nome → tipo/default).
        funcao: Referência à função original.
    """

    nome: str
    descricao: str
    descricao_completa: str
    parametros: dict[str, Any]
    funcao: Any = field(repr=False)

    def to_prompt_text(self) -> str:
        """Gera a descrição que o LLM vê no system prompt."""
        linhas = [f"- {self.nome}"]
        linhas.append(f"  Descrição: {self.descricao}")

        if self.parametros:
            linhas.append("  Parâmetros:")
            for nome, info in self.parametros.items():
                tipo = info.get("tipo", "Any")
                default = info.get("default")
                default_str = f", default={default!r}" if default is not None else ""
                linhas.append(f"    - {nome} ({tipo}{default_str})")
        else:
            linhas.append("  Parâmetros: nenhum")

        return "\n".join(linhas)