"""Testes dos tipos da agent-sdk."""

from agent_sdk.types import ToolExecutionError, ToolResult, ToolSpec


class TestToolResult:
    def test_ok_cria_resultado_de_sucesso(self):
        resultado = ToolResult.ok("dados aqui")
        assert resultado.sucesso is True
        assert resultado.dados == "dados aqui"
        assert resultado.erro is None

    def test_falha_cria_resultado_de_erro(self):
        resultado = ToolResult.falha("algo deu errado")
        assert resultado.sucesso is False
        assert resultado.erro == "algo deu errado"

    def test_to_prompt_text_com_string(self):
        resultado = ToolResult.ok("evento: reunião")
        assert resultado.to_prompt_text() == "evento: reunião"

    def test_to_prompt_text_com_dict(self):
        resultado = ToolResult.ok({"eventos": []})
        texto = resultado.to_prompt_text()
        assert "eventos" in texto

    def test_to_prompt_text_com_erro(self):
        resultado = ToolResult.falha("timeout")
        assert "ERRO" in resultado.to_prompt_text()
        assert "timeout" in resultado.to_prompt_text()


class TestToolExecutionError:
    def test_erro_sem_retry(self):
        erro = ToolExecutionError("falhou")
        assert erro.mensagem == "falhou"
        assert erro.retry is False

    def test_erro_com_retry(self):
        erro = ToolExecutionError("timeout", retry=True)
        assert erro.retry is True

    def test_erro_eh_excecao(self):
        erro = ToolExecutionError("teste")
        assert isinstance(erro, Exception)


class TestToolSpec:
    def test_to_prompt_text(self):
        spec = ToolSpec(
            nome="google_calendar_list_events",
            descricao="Lista eventos",
            descricao_completa="Lista os próximos eventos.",
            parametros={"qtd": {"tipo": "int", "default": 5}},
            funcao=lambda: None,
        )
        texto = spec.to_prompt_text()
        assert "google_calendar_list_events" in texto
        assert "Lista eventos" in texto
        assert "qtd" in texto
        assert "int" in texto