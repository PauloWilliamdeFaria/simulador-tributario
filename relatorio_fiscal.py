"""
Módulo de Apuração Fiscal e Cálculo Tributário (Simulação Didática).

Este módulo disponibiliza uma engine orientada a objetos desenvolvida para:
1. Higienizar e converter valores monetários em formato BRL para objetos Decimal.
2. Validar a integridade da base de dados anual (verificando presença dos 12 meses,
   valores não finitos, vazios ou negativos).
3. Aplicar alíquotas didáticas para apuração de tributos mensais e trimestrais acumulados.
4. Exibir o demonstrativo consolidado no console e exportar os dados em arquivo CSV.
"""

import csv
import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Dict, List, Tuple

# Configuração global de logs do sistema
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


class DadoFiscalCorrompidoError(Exception):
    """
    Exceção customizada de domínio.
    
    Lançada sempre que uma string de faturamento contiver caracteres inválidos,
    estiver vazia, for negativa ou representar um valor não finito (ex: NaN, Infinity).
    """
    pass


@dataclass(frozen=True)
class FaturamentoMensal:
    """
    Estrutura imutável de dados para armazenamento do faturamento individual de um mês.

    Atributos:
        mes (str): Sigla ou nome do mês (ex: 'jan', 'fev').
        valor_bruto (Decimal): Valor do faturamento bruto processado.
        imposto_mensal (Decimal): Valor total dos impostos mensais apurados (ISS + PIS + COFINS).
    """
    mes: str
    valor_bruto: Decimal
    imposto_mensal: Decimal


@dataclass(frozen=True)
class ApuracaoTrimestral:
    """
    Estrutura imutável de dados para armazenamento do faturamento consolidado do trimestre.

    Atributos:
        nome_trimestre (str): Identificador do trimestre (ex: '1º Trimestre (Jan-Mar)').
        faturamento_acumulado (Decimal): Soma dos faturamentos dos 3 meses do trimestre.
        imposto_trimestral (Decimal): Valor dos impostos trimestrais (IRPJ + CSLL + Adicional Didático).
    """
    nome_trimestre: str
    faturamento_acumulado: Decimal
    imposto_trimestral: Decimal


class FaturamentoService:
    """
    Serviço responsável pela sanitização, validação e formatação de valores monetários.

    Aplica a política estrita de arredondamento financeiro (2 casas decimais com ROUND_HALF_UP).
    """

    PRECISAO_MOEDA = Decimal('0.01')

    @classmethod
    def arredondar(cls, valor: Decimal) -> Decimal:
        """
        Aplica a política padrão de arredondamento financeiro do sistema.

        Parâmetros:
            valor (Decimal): O valor numérico a ser arredondado.

        Retorna:
            Decimal: Valor arredondado exatamente para 2 casas decimais.
        """
        return valor.quantize(cls.PRECISAO_MOEDA, rounding=ROUND_HALF_UP)

    @classmethod
    def converter_para_decimal(cls, texto: str) -> Decimal:
        """Converte valores monetários brasileiros para Decimal."""

        if not isinstance(texto, str) or not texto.strip():
            raise DadoFiscalCorrompidoError(
                "Entrada vazia ou inválida."
            )

        texto_limpo = texto.strip()

        if texto_limpo.startswith("R$"):
            texto_limpo = texto_limpo[2:].strip()

        # Aceita 1000,00; 1.000,00; 1000; 1.000
        padrao = r"(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{1,2})?"

        if not re.fullmatch(padrao, texto_limpo):
            raise DadoFiscalCorrompidoError(
                f"Formato monetário inválido: '{texto}'"
            )

        texto_limpo = texto_limpo.replace(".", "").replace(",", ".")

        try:
            valor = Decimal(texto_limpo)
        except InvalidOperation as erro:
            raise DadoFiscalCorrompidoError(
                f"Valor numérico inválido: '{texto}'"
            ) from erro

        if not valor.is_finite() or valor < 0:
            raise DadoFiscalCorrompidoError(
                f"Valor monetário inválido: '{texto}'"
            )

        return cls.arredondar(valor)

    @classmethod
    def formatar_moeda(cls, valor: Decimal) -> str:
        """
        Formata um objeto Decimal na representação padrão de moeda BRL (R$).

        Parâmetros:
            valor (Decimal): O valor numérico a ser formatado.

        Retorna:
            str: String formatada (ex: 'R$    95.141,98').
        """
        valor_arredondado = cls.arredondar(valor)
        texto_formatado = f"R$ {valor_arredondado:>12,.2f}"
        return texto_formatado.replace(',', 'X').replace('.', ',').replace('X', '.')


class CalculadoraTributaria:
    """
    Engine para cálculo dos tributos incidentes.

    IMPORTANTE: As alíquotas abaixo constituem uma simulação didática aplicada
    diretamente sobre a receita bruta para fins de demonstração técnica.
    """

    ALIQUOTAS_DIDATICAS = {
        'ISS': Decimal('0.05'),                     # 5.00%
        'PIS': Decimal('0.0065'),                   # 0.65%
        'COFINS': Decimal('0.03'),                  # 3.00%
        'IRPJ': Decimal('0.048'),                   # 4.80%
        'CSLL': Decimal('0.0288'),                  # 2.88%
        'ADICIONAL_IR': Decimal('0.10'),            # 10.00%
        'LIMITE_TRIMESTRAL_DIDATICO': Decimal('60000.00')  # R$ 60.000,00/trimestre
    }

    @classmethod
    def calcular_imposto_mensal(cls, faturamento: Decimal) -> Decimal:
        """
        Calcula a soma dos impostos mensais (ISS + PIS + COFINS).

        Parâmetros:
            faturamento (Decimal): O faturamento bruto do mês.

        Retorna:
            Decimal: Total de tributos mensais apurados.
        """
        iss = faturamento * cls.ALIQUOTAS_DIDATICAS['ISS']
        pis = faturamento * cls.ALIQUOTAS_DIDATICAS['PIS']
        cofins = faturamento * cls.ALIQUOTAS_DIDATICAS['COFINS']
        return FaturamentoService.arredondar(iss + pis + cofins)

    @classmethod
    def calcular_imposto_trimestral(cls, faturamento_trimestre: Decimal) -> Decimal:
        """
        Calcula a soma dos impostos trimestrais (IRPJ + CSLL + Adicional de IR Didático).

        Aplica o adicional de 10% sobre a parcela que ultrapassar R$ 60.000,00 no trimestre.

        Parâmetros:
            faturamento_trimestre (Decimal): O faturamento bruto acumulado do trimestre.

        Retorna:
            Decimal: Total de tributos trimestrais apurados.
        """
        ir = faturamento_trimestre * cls.ALIQUOTAS_DIDATICAS['IRPJ']
        csll = faturamento_trimestre * cls.ALIQUOTAS_DIDATICAS['CSLL']

        adicional_ir = Decimal('0.00')
        limite = cls.ALIQUOTAS_DIDATICAS['LIMITE_TRIMESTRAL_DIDATICO']
        if faturamento_trimestre > limite:
            adicional_ir = (faturamento_trimestre - limite) * cls.ALIQUOTAS_DIDATICAS['ADICIONAL_IR']

        return FaturamentoService.arredondar(ir + csll + adicional_ir)


class RelatorioExporter:
    """Responsável pela saída dos dados: exibição no terminal e exportação em CSV."""

    @staticmethod
    def exibir_console(mensais: List[FaturamentoMensal], trimestrais: List[ApuracaoTrimestral]) -> None:
        """
        Gera e exibe a tabela de demonstrativos e o Resumo Executivo Anual no terminal.

        Parâmetros:
            mensais (List[FaturamentoMensal]): Lista de dados mensais processados.
            trimestrais (List[ApuracaoTrimestral]): Lista de dados trimestrais processados.
        """
        fmt = FaturamentoService.formatar_moeda

        print('\n' + '=' * 75)
        print(f'{"DEMONSTRATIVO FISCAL MENSAL (SIMULAÇÃO DIDÁTICA)":^75}')
        print('=' * 75)
        print(f'{"MÊS":<6} | {"FATURAMENTO":<18} | {"IMPOSTO MENSAL":<30}')
        print('-' * 75)
        for item in mensais:
            print(f'{item.mes.upper():<6} | {fmt(item.valor_bruto)} | {fmt(item.imposto_mensal)}')

        print('\n' + '=' * 75)
        print(f'{"DEMONSTRATIVO FISCAL TRIMESTRAL (ACUMULADO)":^75}')
        print('=' * 75)
        print(f'{"TRIMESTRE":<25} | {"FATURAMENTO TOTAL":<18} | {"IMPOSTO TRIMESTRAL":<20}')
        print('-' * 75)
        for item in trimestrais:
            print(f'{item.nome_trimestre:<25} | {fmt(item.faturamento_acumulado)} | {fmt(item.imposto_trimestral)}')

        total_fat = sum((item.valor_bruto for item in mensais), Decimal('0.00'))
        total_imp_m = sum((item.imposto_mensal for item in mensais), Decimal('0.00'))
        total_imp_t = sum((item.imposto_trimestral for item in trimestrais), Decimal('0.00'))
        total_impostos = total_imp_m + total_imp_t
        aliquota = (total_impostos / total_fat * Decimal('100')) if total_fat > 0 else Decimal('0.00')

        print('\n' + '=' * 75)
        print(f'{"RESUMO EXECUTIVO ANUAL":^75}')
        print('=' * 75)
        print(f' • Faturamento Anual Bruto:        {fmt(total_fat)}')
        print(f' • Total Impostos Mensais:         {fmt(total_imp_m)}')
        print(f' • Total Impostos Trimestrais:     {fmt(total_imp_t)}')
        print(f' • Total de Tributos Apurados:     {fmt(total_impostos)}')
        print(f' • Alíquota Efetiva Média Anual:   {aliquota:.2f}%')
        print('=' * 75)

    @staticmethod
    def exportar_csv(
        mensais: List[FaturamentoMensal],
        trimestrais: List[ApuracaoTrimestral],
        caminho_arquivo: str = "relatorio_fiscal.csv"
    ) -> None:
        """
        Escreve os relatórios em um arquivo no formato CSV utilizando delimitador ';'.

        Parâmetros:
            mensais (List[FaturamentoMensal]): Apuração mensal.
            trimestrais (List[ApuracaoTrimestral]): Apuração trimestral.
            caminho_arquivo (str): Nome ou caminho de destino do arquivo.

        Exceções:
            OSError: Captura erro de E/S ao salvar o arquivo, registra no log e o relança.
        """
        arredondar = FaturamentoService.arredondar
        try:
            with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['TIPO', 'PERIODO', 'FATURAMENTO_BRUTO', 'IMPOSTO_APURADO'])

                for item in mensais:
                    writer.writerow([
                        'MENSAL',
                        item.mes.upper(),
                        f"{arredondar(item.valor_bruto):.2f}",
                        f"{arredondar(item.imposto_mensal):.2f}"
                    ])

                for item in trimestrais:
                    writer.writerow([
                        'TRIMESTRAL',
                        item.nome_trimestre,
                        f"{arredondar(item.faturamento_acumulado):.2f}",
                        f"{arredondar(item.imposto_trimestral):.2f}"
                    ])

            logging.info(f"✅ Relatório CSV exportado com sucesso: '{caminho_arquivo}'.")
        except OSError as erro:
            logging.error(f"Erro ao salvar arquivo CSV: {erro}")
            raise


def processar_folha_fiscal(dados_brutos: Dict[str, str], caminho_csv: str = "relatorio_fiscal.csv") -> bool:
    """
    Função orquestradora principal da pipeline de apuração fiscal.

    Passos de execução:
    1. Valida se o dicionário possui todos os 12 meses do ano.
    2. Converte e valida cada valor individualmente via `FaturamentoService`.
    3. Interrompe o processamento caso sejam encontrados dados inválidos.
    4. Agrupa os faturamentos nos 4 trimestres civis e calcula os tributos acumulados.
    5. Dispara a exibição no console e tenta a gravação do arquivo CSV (retornando False em caso de OSError).

    Parâmetros:
        dados_brutos (Dict[str, str]): Dicionário no formato {'mes': 'R$ 00,00'}.
        caminho_csv (str): Nome do arquivo CSV a ser gerado.

    Retorna:
        bool: True se a apuração foi concluída com êxito, False se foi abortada por erro ou falha de E/S.
    """
    meses_esperados = {'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'}
    meses_presentes = set(dados_brutos.keys())

    # 1. Validação da completude da base de dados
    if meses_esperados != meses_presentes:
        faltantes = meses_esperados - meses_presentes
        print('\n' + '❌' * 40)
        print(" EXECUÇÃO ABORTADA: BASE DE DADOS INCOMPLETA")
        print('❌' * 40)
        print(f" • Meses ausentes no faturamento anual: {', '.join(sorted(faltantes)).upper()}")
        return False

    mensais: List[FaturamentoMensal] = []
    erros_encontrados: List[Tuple[str, str]] = []

    # 2. Processamento individual de cada mês
    for mes in ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']:
        texto = dados_brutos[mes]
        try:
            valor = FaturamentoService.converter_para_decimal(texto)
            imp_mensal = CalculadoraTributaria.calcular_imposto_mensal(valor)
            mensais.append(FaturamentoMensal(mes=mes, valor_bruto=valor, imposto_mensal=imp_mensal))
        except DadoFiscalCorrompidoError as err:
            logging.error(f"❌ Erro no mês [{mes.upper()}]: {err}")
            erros_encontrados.append((mes, texto))

    # 3. Interrupção do processamento por dados inválidos
    if erros_encontrados:
        print('\n' + '❌' * 40)
        print(" EXECUÇÃO ABORTADA: FORAM ENCONTRADOS ERROS NOS DADOS DE ENTRADA")
        print('❌' * 40)
        for mes, val in erros_encontrados:
            print(f" • Mês [{mes.upper()}]: Valor inválido '{val}'.")
        print("\nO relatório fiscal NÃO foi gerado para evitar inconsistências.")
        return False

    # 4. Agrupamento trimestral
    mapa_mensal = {item.mes: item.valor_bruto for item in mensais}
    trimestres_config = {
        '1º Trimestre (Jan-Mar)': ['jan', 'fev', 'mar'],
        '2º Trimestre (Abr-Jun)': ['abr', 'mai', 'jun'],
        '3º Trimestre (Jul-Set)': ['jul', 'ago', 'set'],
        '4º Trimestre (Out-Dez)': ['out', 'nov', 'dez']
    }

    trimestrais: List[ApuracaoTrimestral] = []
    for nome_trim, lista_meses in trimestres_config.items():
        fat_trimestre = sum((mapa_mensal[m] for m in lista_meses), Decimal('0.00'))
        imp_trimestre = CalculadoraTributaria.calcular_imposto_trimestral(fat_trimestre)
        trimestrais.append(ApuracaoTrimestral(
            nome_trimestre=nome_trim,
            faturamento_acumulado=FaturamentoService.arredondar(fat_trimestre),
            imposto_trimestral=imp_trimestre
        ))

    # 5. Emissão de resultados com tratamento de falhas de gravação (OSError)
    RelatorioExporter.exibir_console(mensais, trimestrais)

    try:
        RelatorioExporter.exportar_csv(mensais, trimestrais, caminho_csv)
    except OSError:
        return False

    return True


def main() -> None:
    """Ponto de entrada da aplicação ao ser executada diretamente."""
    faturamento_anual = {
        'jan': 'R$ 95.141,98',
        'fev': 'R$ 95.425,16',
        'mar': 'R$ 89.716,31',
        'abr': 'R$ 78.459,99',
        'mai': 'R$ 71.087,28',
        'jun': 'R$ 83.911,06',
        'jul': 'R$ 56.467,26',
        'ago': 'R$ 88.513,58',
        'set': 'R$ 66.552,49',
        'out': 'R$ 80.164,07',
        'nov': 'R$ 66.964,33',
        'dez': 'R$ 71.525,25',
    }

    processar_folha_fiscal(faturamento_anual)


if __name__ == '__main__':
    main()