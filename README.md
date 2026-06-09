# SalesInsight PY
### Pipeline de Análise e Visualização de Dados de Vendas

Mini-Projeto Avaliativo – Módulo 01 – IA para Análise Preditiva

---

## Sobre o projeto

O **SalesInsight PY** é um pipeline completo de análise de dados de vendas desenvolvido em Python. O sistema realiza um processo completo de ETL (Extract, Transform, Load) e análise de dados local: gerando dados fictícios, limpando inconsistências, extraindo novos indicadores, agregando métricas de negócios, calculando estatísticas científicas com NumPy, gerando projeções matemáticas de vendas futuras e gerando visualizações gráficas de alta qualidade.

---

## 🛠️ Passo a Passo do Pipeline de Execução

O script principal `salesinsight.py` executa os seguintes passos coordenados:

1. **Configuração de Ambiente**: Garante que o console de saída do terminal (especialmente no Windows) esteja configurado em UTF-8 para exibição correta de acentuação, e inicializa o logging profissional estruturado para rastreamento de execução.
2. **Geração/Carregamento do Dataset (RF01)**: Tenta carregar o arquivo `vendas.csv`. Se ele não existir, o sistema gera dinamicamente 200 transações de vendas com ruído intencional (valores nulos em quantidade/preço, espaçamentos desnecessários e datas em formatos incorretos).
3. **Inspeção Inicial dos Dados (RF02)**: Apresenta estatísticas descritivas básicas, contagem de valores ausentes e formatos de coluna antes de qualquer alteração, para contextualizar a necessidade da limpeza.
4. **Limpeza e Tratamento de Dados (RF03)**: Remove espaçamentos extras, converte datas filtrando inconsistências, remove registros com valores essenciais nulos (quantidade e preço) e corrige a tipagem numérica.
5. **Engenharia de Recursos (RF04 & RF11)**: Cria colunas calculadas como receita total (`receita_total`), ano, trimestre, número do mês e nome do mês mapeado de forma estática em português (sem dependência do locale do sistema operacional). Além disso, categoriza cada venda por faixas de receita ("Baixo Valor", "Médio Valor", "Alto Valor").
6. **Agregação de Métricas de Negócio (RF05)**: Calcula estatísticas agrupadas para análise comercial, incluindo a receita total mensal, top 5 produtos mais vendidos, faturamento por categoria e faturamento total com ticket médio por região.
7. **Segmentação de Clientes (RF06)**: Classifica os clientes de acordo com o volume financeiro acumulado de compras nas categorias **Ouro** (acima de R$ 15.000), **Prata** (entre R$ 5.000 e R$ 15.000) e **Bronze** (abaixo de R$ 5.000) usando funções lambda.
8. **Análise Estatística Avançada (RF07)**: Utiliza NumPy de forma vetorizada para calcular média, mediana, desvio padrão, percentis (Q1 e Q3), além de normalização de receitas (broadcasting) e contagem de vendas acima do valor médio geral.
9. **Visualização de Dados Premium (RF08)**: Gera e exporta três gráficos analíticos refinados em formato PNG na pasta `outputs/graficos/`:
   - Evolução mensal de faturamento (Gráfico de linha com área sombreada).
   - Top 5 produtos mais rentáveis (Barras horizontais estilizadas com rotulagem formatada em milhares).
   - Distribuição de valores de transações por região geográfica (Boxplot).
10. **Projeções de Tendência (RF10)**: Realiza uma projeção de tendência de faturamento para os próximos 3 meses baseada em média móvel simples e desvio padrão.
11. **Exportação de Artefatos (RF12 & RF13)**: Salva as métricas mensais e a segmentação de clientes em planilhas CSV (`utf-8-sig`) e exporta as estatísticas calculadas em um arquivo JSON formatado, executando uma validação subsequente de leitura (`json.load`) para garantir a integridade dos dados salvos.

---

## Objetivo pedagógico

Praticar os principais conceitos do Módulo 01:

| Conceito | Como foi aplicado |
|---|---|
| Lógica de programação | Cálculos, condicionais, repetições ao longo de todo o pipeline |
| Variáveis e tipos de dados | `int`, `float`, `str`, `bool`, `list`, `dict` em todo o código |
| `if / elif / else` | Classificação de segmentos (Bronze/Prata/Ouro) e faixas de receita |
| Operadores | Cálculo de `receita_total`, filtros booleanos, comparações |
| `for / while` | Iteração para exibição de ranking e relatórios no console |
| Funções com parâmetros e retorno | Todas as 10+ funções do pipeline |
| Funções lambda | `segmentar_clientes`, `processar_coluna`, `sorted` com key lambda |
| Função de ordem superior | `processar_coluna(df, coluna, funcao_transformacao)` |
| Leitura de CSV | `pd.read_csv()` |
| Escrita de CSV | `.to_csv()` |
| Escrita de JSON | `json.dump()` |
| Leitura de JSON | `json.load()` para confirmação |
| `datetime` | Extração de mês, trimestre e ano de `data_venda` |
| Expressões regulares (`re`) | `re.sub()` e `re.compile()` em `limpar_strings_com_regex()` |
| Pandas – Series e DataFrames | Estrutura principal de todos os dados |
| Pandas – Filtros e seleções | Filtros com condicionais booleanas (`dropna`, `isnull`) |
| Pandas – `groupby` | Agregações por mês, produto, categoria e região |
| NumPy – Arrays | Conversão de colunas com `.to_numpy()` |
| NumPy – Operações vetorizadas | `mean`, `std`, `median`, `percentile`, `sum` sem loops |
| NumPy – Broadcasting | Normalização min-max de receitas |
| NumPy – `np.select` | Classificação condicional vetorizada de `faixa_receita_item` |
| Matplotlib – gráfico de linha | Receita total por mês |
| Seaborn – gráfico de barras | Top 5 produtos por receita |
| Seaborn – boxplot | Distribuição de receita por região |
| Exportação de gráficos PNG | `plt.savefig()` com `dpi=150` |
| Classes com `__init__` | `AnalisadorDeVendas` com construtor, atributos e métodos |
| Atributos de instância (`self`) | `self.df_limpo`, `self.metricas`, `self.clientes` etc. |
| Métodos de instância | `.carregar()`, `.limpar()`, `.analisar()`, `.visualizar()` etc. |
| Herança e `super()` | `AnalisadorComProjecao(AnalisadorDeVendas)` |
| Módulos e importações | `pandas`, `numpy`, `matplotlib`, `seaborn`, `re`, `json`, `os` |
| GitHub + branches | Versionamento com GitFlow simplificado |
| Kanban | Organização das tarefas de desenvolvimento |

---

## Como executar

### No Google Colab (recomendado)

1. Faça upload do `salesinsight.py` e do `vendas.csv` para o Colab.  
2. Execute no terminal do Colab:
```bash
!python salesinsight.py
```
3. Ou cole o conteúdo em células de um notebook `.ipynb`.

### Localmente com VS Code

1. Instale Python 3.10+ e o VS Code com a extensão Python.  
2. Instale as dependências:
```bash
pip install pandas numpy matplotlib seaborn
```
3. Execute:
```bash
python salesinsight.py
```

---

## Estrutura do projeto

```
salesinsight-py/
│
├── salesinsight.py              # Pipeline principal (RF01 a RF14)
├── vendas.csv                   # Dataset gerado sinteticamente
├── README.md                    # Este arquivo
│
└── outputs/
    ├── relatorio_resumo.csv         # Métricas mensais
    ├── metricas_por_mes.csv         # Detalhamento mensal
    ├── segmentacao_clientes.csv     # Clientes segmentados
    ├── estatisticas_gerais.json     # Estatísticas NumPy exportadas
    └── graficos/
        ├── vendas_por_mes.png       # Gráfico de linha (RF08)
        ├── top_produtos.png         # Gráfico de barras (RF08)
        └── distribuicao_regioes.png # Boxplot por região (RF08)
```

---

## Ferramentas utilizadas

- **Python 3.10+**
- **Google Colab / VS Code**
- **Bibliotecas:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `re`, `json`, `datetime`, `os`, `random`
- **GitHub + GitHub Desktop** para versionamento
- **GitHub Projects / Trello** para Kanban

---

## Como a internet funciona (contexto do projeto)

Neste projeto, os dados são lidos de um arquivo local CSV. Em um cenário real de produção, esses dados poderiam vir de uma **API REST** — o cliente (script Python) faria uma requisição HTTP GET para um servidor que retornaria os dados em JSON, seguindo a **arquitetura cliente-servidor**. A biblioteca `requests` do Python permite consumir essas APIs diretamente.

---

## Sobre variáveis em Python vs JavaScript

Em Python não existe distinção entre `var`, `let` e `const` como no JavaScript. Toda variável é declarada com simples atribuição (`=`). Por convenção, **constantes são escritas em MAIÚSCULAS** (ex.: `CAMINHO_CSV = "vendas.csv"`). Para imutabilidade real, usa-se tuplas no lugar de listas.

---

## 🚀 Próximos Passos (O que falta fazer no projeto)

Após a conclusão deste pipeline básico de análise e visualização de dados de vendas, o projeto pode ser expandido com as seguintes implementações:

1. **Dashboard Interativo em Streamlit**:
   - Construir uma interface web interativa onde o usuário possa fazer o upload de seu próprio CSV de vendas e interagir com filtros dinâmicos de categoria, região e data, além de exportar os relatórios clicando em botões.
2. **Conexão com Banco de Dados SQL**:
   - Modificar o carregamento e exportação de dados para ler e escrever diretamente em bancos de dados relacionais reais (como PostgreSQL ou SQLite) usando a biblioteca `SQLAlchemy` do Python.
3. **Modelagem Preditiva com Aprendizado de Máquina**:
   - Substituir a estimativa de vendas simples (média móvel) por um modelo preditivo baseado em machine learning (ex: Regressão Linear, Random Forest ou Prophet) para prever vendas futuras com intervalo de confiança.
4. **Conteinerização com Docker & CI/CD**:
   - Empacotar o projeto em um container Docker para execução em qualquer infraestrutura.
   - Criar workflows de automação no GitHub Actions para rodar testes automáticos (`pytest`) antes de cada commit.

---

## Vídeo de demonstração

> [Inserir link do Google Drive ou YouTube aqui]

---

*Projeto desenvolvido para a disciplina de IA – Desenvolvedor(a) em IA para Análise Preditiva – Módulo 01, Semana 08.*
