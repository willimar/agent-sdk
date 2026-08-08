"""Testes do decorator @tool."""

import pytest

from agent_sdk.decorators import clear_registry, get_registry, tool


@pytest.fixture(autouse=True)
def limpar_registry():
    """Garante registry limpo entre testes."""
    clear_registry()
    yield
    clear_registry()


class TestToolDecorator:
    def test_registra_funcao_no_registry(self):
        @tool("teste_tool")
        def minha_funcao():
            """Uma ferramenta de teste."""
            return "ok"

        registry = get_registry()
        assert "teste_tool" in registry

    def test_spec_contem_descricao(self):
        @tool("teste_tool")
        def minha_funcao():
            """Descrição curta aqui."""
            return "ok"

        spec = get_registry()["teste_tool"]
        assert spec.descricao == "Descrição curta aqui."

    def test_spec_contem_parametros(self):
        @tool("teste_tool")
        def minha_funcao(nome: str, qtd: int = 5):
            """Ferramenta com parâmetros."""
            return "ok"

        spec = get_registry()["teste_tool"]
        assert "nome" in spec.parametros
        assert "qtd" in spec.parametros
        assert spec.parametros["nome"]["tipo"] == "str"
        assert spec.parametros["qtd"]["default"] == 5

    def test_funcao_continua_funcional(self):
        @tool("teste_tool")
        def soma(a: int, b: int) -> int:
            """Soma dois números."""
            return a + b

        assert soma(2, 3) == 5

    def test_nome_duplicado_lanca_erro(self):
        @tool("duplicada")
        def primeira():
            """Primeira."""
            pass

        with pytest.raises(ValueError, match="já está registrada"):
            @tool("duplicada")
            def segunda():
                """Segunda."""
                pass

    def test_nome_com_espaco_lanca_erro(self):
        with pytest.raises(ValueError, match="não pode conter espaços"):
            @tool("nome invalido")
            def funcao():
                """Teste."""
                pass

    def test_nome_vazio_lanca_erro(self):
        with pytest.raises(ValueError, match="não pode ser vazio"):
            @tool("")
            def funcao():
                """Teste."""
                pass

    def test_funcao_tem_metadata_anexado(self):
        @tool("teste_tool")
        def minha_funcao():
            """Teste."""
            pass

        assert hasattr(minha_funcao, "_tool_name")
        assert minha_funcao._tool_name == "teste_tool"
        assert hasattr(minha_funcao, "_tool_spec")