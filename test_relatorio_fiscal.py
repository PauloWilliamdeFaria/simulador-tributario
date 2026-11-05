"""
Módulo de Testes Unitários e de Integração.

Este arquivo contém a suíte de testes automatizados responsável por garantir:
1. A conversão e validação correta de strings monetárias em objetos Decimal.
2. A rejeição de entradas malformatadas, vazias, tipos inválidos, negativas ou não finitas.
3. A exatidão dos cálculos tributários mensais e trimestrais.
4. O funcionamento completo da pipeline (geração de CSV, acionamento da interrupção por dados
   inválidos e tratamento de exceções de E/S na exportação).
"""

import os
import unittest
from decimal import Decimal
from unittest.mock import patch

from relatorio_fiscal import (
    FaturamentoService,
    CalculadoraTributaria,
    DadoFiscalCorrompidoError,
    processar_folha_fiscal
)


class TestFaturamentoService(unittest.TestCase):
    """Testes unitários direcionados às funções de conversão e validação da classe FaturamentoService."""

    def test_conversao_valida(self):
        """Valida se strings formatadas em BRL são convertidas corretamente para Decimal."""
        self.assertEqual(FaturamentoService.converter_para_decimal("R$ 95.141,98"), Decimal("95141.98"))

    def test_rejeicao_entradas_invalidas(self):
        """Garante que entradas de texto aleatório ou vazias lancem a exceção DadoFiscalCorrompidoError."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("R$ INVALIDO")
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("")

    def test_rejeicao_valores_negativos(self):
        """Garante a rejeição de valores de faturamento com sinal negativo."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("-R$ 1.500,00")

    def test_rejeicao_valores_nao_finitos(self):
        """Garante a rejeição de valores especiais não finitos como 'NaN'."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("NaN")

    def test_rejeicao_tipo_invalido(self):
        """Garante que entradas que não sejam do tipo string sejam rejeitadas."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal(1234.56)  # type: ignore

    def test_conversao_formatos_sem_simbolo_moeda(self):
        """Valida se formatos válidos sem o prefixo 'R$' (ex: '1000,00', '1.000,00', '1000') são aceitos."""
        self.assertEqual(FaturamentoService.converter_para_decimal("1000,00"), Decimal("1000.00"))
        self.assertEqual(FaturamentoService.converter_para_decimal("1.000,00"), Decimal("1000.00"))
        self.assertEqual(FaturamentoService.converter_para_decimal("1000"), Decimal("1000.00"))

    def test_rejeicao_formato_monetario_malformatado(self):
        """Garante a rejeição de pontuações de milhar/decimal incorretas pela nova Regex."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("10.00,00")
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("1,000.00")

    def test_formato_brasileiro_valido(self):
        """Valida a conversão de valor padrão brasileiro com R$ e separadores de milhar e decimal."""
        valor = FaturamentoService.converter_para_decimal("R$ 1.234,56")
        self.assertEqual(valor, Decimal("1234.56"))

    def test_formato_decimal_ambiguo(self):
        """Garante a rejeição de valores ambíguos no formato americano com ponto decimal."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("1.23")

    def test_separadores_invalidos(self):
        """Garante a rejeição de strings com agrupamentos numéricos de milhar inconsistentes."""
        with self.assertRaises(DadoFiscalCorrompidoError):
            FaturamentoService.converter_para_decimal("12.34,56")


class TestCalculadoraTributaria(unittest.TestCase):
    """Testes unitários focados na exatidão das fórmulas matemáticas de cálculo de tributos."""

    def test_imposto_mensal(self):
        """Testa a apuração mensal (ISS 5% + PIS 0.65% + COFINS 3% = 8.65%)."""
        fat = Decimal("100000.00")
        self.assertEqual(CalculadoraTributaria.calcular_imposto_mensal(fat), Decimal("8650.00"))

    def test_imposto_trimestral_com_adicional_didatico(self):
        """Testa a apuração trimestral incluindo os 10% adicionais sobre o excedente de R$ 60.000,00."""
        fat_trimestre = Decimal("100000.00")
        self.assertEqual(CalculadoraTributaria.calcular_imposto_trimestral(fat_trimestre), Decimal("11680.00"))


class TestIntegracaoRelatorioFiscal(unittest.TestCase):
    """Testes de integração para validar a pipeline completa de execução."""

    def setUp(self):
        """Prepara o ambiente de teste definindo o caminho do arquivo temporário e dados de entrada."""
        self.caminho_csv_teste = "relatorio_teste_temp.csv"
        self.faturamento_valido = {
            'jan': 'R$ 10.000,00', 'fev': 'R$ 10.000,00', 'mar': 'R$ 10.000,00',
            'abr': 'R$ 10.000,00', 'mai': 'R$ 10.000,00', 'jun': 'R$ 10.000,00',
            'jul': 'R$ 10.000,00', 'ago': 'R$ 10.000,00', 'set': 'R$ 10.000,00',
            'out': 'R$ 10.000,00', 'nov': 'R$ 10.000,00', 'dez': 'R$ 10.000,00',
        }

    def tearDown(self):
        """Limpa os artefatos criados removendo o arquivo CSV temporário se ele existir."""
        if os.path.exists(self.caminho_csv_teste):
            os.remove(self.caminho_csv_teste)

    @patch('builtins.print')
    def test_processamento_completo_sucesso(self, mock_print):
        """Valida se a função executa perfeitamente até o fim e cria o arquivo CSV com o conteúdo correto."""
        sucesso = processar_folha_fiscal(self.faturamento_valido, self.caminho_csv_teste)
        
        self.assertTrue(sucesso)
        self.assertTrue(os.path.exists(self.caminho_csv_teste))

        # Lê e valida as linhas gravadas no CSV
        with open(self.caminho_csv_teste, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            self.assertIn("MENSAL;JAN;10000.00;865.00", conteudo)
            self.assertIn("TRIMESTRAL;1º Trimestre (Jan-Mar);30000.00;2304.00", conteudo)

    @patch('builtins.print')
    def test_processamento_abortado_por_dados_corrompidos(self, mock_print):
        """Garante que a pipeline seja abortada e o CSV não seja gerado se houver dados inválidos."""
        faturamento_corrompido = self.faturamento_valido.copy()
        faturamento_corrompido['mar'] = 'R$ INVALIDO'

        sucesso = processar_folha_fiscal(faturamento_corrompido, self.caminho_csv_teste)

        self.assertFalse(sucesso)
        self.assertFalse(os.path.exists(self.caminho_csv_teste))

    @patch('builtins.print')
    def test_processamento_abortado_por_meses_faltantes(self, mock_print):
        """Garante a interrupção da execução se a base de dados contiver menos de 12 meses."""
        faturamento_incompleto = self.faturamento_valido.copy()
        del faturamento_incompleto['dez']

        sucesso = processar_folha_fiscal(faturamento_incompleto, self.caminho_csv_teste)

        self.assertFalse(sucesso)
        self.assertFalse(os.path.exists(self.caminho_csv_teste))

    @patch('builtins.print')
    @patch(
        'relatorio_fiscal.RelatorioExporter.exportar_csv',
        side_effect=OSError("Falha simulada de gravação")
    )
    def test_falha_exportacao_csv(
        self, mock_exportar, mock_print
    ):
        """Valida o tratamento gracioso quando ocorre um erro de E/S ao salvar o arquivo CSV."""
        sucesso = processar_folha_fiscal(
            self.faturamento_valido,
            self.caminho_csv_teste
        )

        self.assertFalse(sucesso)
        mock_exportar.assert_called_once()


if __name__ == '__main__':
    unittest.main()