# 📊 Sistema de Apuração Fiscal e Calculadora Tributária

[![Autor: Paulo William de Faria](https://img.shields.io/badge/autor-Paulo%20William%20de%20Faria-blue.svg)](https://github.com/PauloWilliamdeFaria/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Precisão: Decimal](https://img.shields.io/badge/precis%C3%A3o-Decimal-green.svg)](https://docs.python.org/3/library/decimal.html)

Projeto educacional em **Python**, com programação orientada a objetos, para validar faturamentos mensais, simular cálculos tributários mensais e trimestrais, apresentar um resumo anual no terminal e exportar os resultados para **CSV**.

> **Aviso importante:** este projeto é uma **simulação didática**, não um sistema de apuração fiscal real. As alíquotas e bases de cálculo foram definidas para demonstrar técnicas de programação. Em particular, o adicional de IR utilizado aqui é aplicado diretamente ao faturamento trimestral acima de R$ 60.000,00, o que **não representa a regra legal de cálculo do IRPJ**. A tributação real depende do regime e da base de cálculo aplicável. Não utilize os resultados para recolhimento de tributos ou tomada de decisões contábeis.

## 💡 Funcionalidades

- Conversão de valores monetários em reais para `Decimal`.
- Arredondamento monetário centralizado em duas casas decimais com `ROUND_HALF_UP`.
- Validação de entradas vazias, inválidas, negativas e não finitas (`NaN`, `Infinity`).
- Verificação da presença dos 12 meses de faturamento.
- **Interrupção do processamento** caso existam dados inconsistentes.
- Simulação de tributos mensais e trimestrais.
- Demonstrativos no terminal e exportação automática para `relatorio_fiscal.csv`.
- Testes unitários e de integração com `unittest` e `unittest.mock`.

## 🛠️ Tecnologias e conceitos

**Python 3.10+**, programação orientada a objetos, `dataclasses`, `decimal`, `csv`, `logging`, tratamento de exceções, anotações de tipos e testes automatizados.

## 📋 Alíquotas e premissas didáticas

| Periodicidade | Tributo | Alíquota | Base usada na simulação |
| --- | --- | ---: | --- |
| Mensal | ISS | 5,00% | Faturamento bruto mensal |
| Mensal | PIS | 0,65% | Faturamento bruto mensal |
| Mensal | COFINS | 3,00% | Faturamento bruto mensal |
| Trimestral | IRPJ | 4,80% | Faturamento bruto trimestral |
| Trimestral | CSLL | 2,88% | Faturamento bruto trimestral |
| Trimestral | Adicional de IR (didático) | 10,00% | Parcela do faturamento trimestral acima de R$ 60.000,00 |

**Todas as alíquotas e bases desta tabela são premissas do exercício, não instruções de cálculo tributário real.**

## 🚀 Como executar

### 1. Pré-requisitos

- Python 3.10 ou superior.
- Git (opcional, para clonar o repositório).
- Não é necessário instalar dependências externas.

### 2. Obter o projeto

```bash
git clone https://github.com/PauloWilliamdeFaria/simulador-tributario.git
cd simulador-tributario
```

> **Atenção:** os comandos a seguir pressupõem que `relatorio_fiscal.py` e `test_relatorio_fiscal.py` estejam na pasta atual. Se os arquivos estiverem em uma subpasta do repositório, entre nessa pasta antes de executá-los.

### 3. Executar a simulação

```bash
python relatorio_fiscal.py
```

No Windows, caso o comando `python` não esteja disponível, experimente `py relatorio_fiscal.py`.

A aplicação utiliza um conjunto de faturamentos de exemplo definido no próprio arquivo `relatorio_fiscal.py`. Após a execução, exibe os demonstrativos mensais e trimestrais, além do resumo anual, e gera o arquivo `relatorio_fiscal.csv` na pasta de execução.

### 4. Executar os testes

```bash
python -m unittest -v test_relatorio_fiscal.py
```

A suíte contém **16 testes**, incluindo validação de valores, cálculos didáticos, geração de CSV, rejeição de dados inválidos e interrupção por ausência de meses.

## 📁 Estrutura dos arquivos

```text
.
├── relatorio_fiscal.py         # Programa principal
├── test_relatorio_fiscal.py    # Testes unitários e de integração
├── README.md                   # Documentação
└── relatorio_fiscal.csv        # Arquivo gerado após executar o programa
```

O arquivo CSV é gerado automaticamente; não é necessário que ele exista antes da execução.

## 📄 Formato do CSV

O arquivo utiliza codificação **UTF-8** e separador `;`. Possui as colunas:

- `TIPO`: `MENSAL` ou `TRIMESTRAL`.
- `PERIODO`: mês ou trimestre.
- `FATURAMENTO_BRUTO`: valor monetário com duas casas decimais.
- `IMPOSTO_APURADO`: resultado da simulação com duas casas decimais.

Exemplo ilustrativo:

```csv
TIPO;PERIODO;FATURAMENTO_BRUTO;IMPOSTO_APURADO
MENSAL;JAN;10000.00;865.00
TRIMESTRAL;1º Trimestre (Jan-Mar);30000.00;2304.00
```

## 🧪 Organização do código

- **`FaturamentoService`**: conversão, validação, arredondamento e formatação monetária.
- **`CalculadoraTributaria`**: aplicação das fórmulas didáticas.
- **`FaturamentoMensal` e `ApuracaoTrimestral`**: estruturas de dados imutáveis com `@dataclass`.
- **`RelatorioExporter`**: exibição dos demonstrativos e gravação em CSV.
- **`processar_folha_fiscal()`**: coordenação das etapas, com interrupção em caso de dados inválidos.

## 🎯 Objetivo do projeto

Demonstrar competências práticas em Python por meio de um exercício de processamento de dados financeiros, organização de código, validação, tratamento de exceções, geração de arquivos e testes automatizados.

**Autor:** [Paulo William de Faria](https://github.com/PauloWilliamdeFaria/)
