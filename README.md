# DataView: Exploração e Análise de Dados de Vendas

O **DataView** é um miniprojeto prático de análise exploratória de dados (EDA) de vendas, desenvolvido em Python no formato de Jupyter Notebook. Ele implementa um fluxo completo de coleta, carga, limpeza, engenharia de recursos, agregação, estatística descritiva, segmentação de clientes e visualização gráfica de dados.

O objetivo do projeto é consolidar conceitos fundamentais de Python, Pandas, NumPy, Matplotlib e Seaborn para transformar um conjunto de dados "sujo" em relatórios limpos e visualizações prontas para apresentação em reuniões de negócios.

---

## Estrutura do Projeto

O projeto foi estruturado seguindo as melhores práticas de organização de repositórios de ciência de dados:

```text
projeto/
├── data/                               # Armazenamento dos arquivos de dados
│   ├── raw/                            # Dados brutos, originais e imutáveis
│   │   └── vendas.csv                  # Dataset de vendas gerado com inconsistências
│   ├── processed/                      # Dados limpos e transformados
│   │   ├── v1_com_outliers/            # Limpeza geral realizada, mas mantendo outliers
│   │   │   └── vendas_v1.csv
│   │   └── v2_outliers_tratado/        # Limpeza geral + tratamento de outliers
│   │       └── vendas_v2.csv
│   └── final/                          # Dataset final enriquecido pronto para modelos de IA
│       └── vendas_final.csv            # v2 + colunas derivadas
│
├── notebooks/                          # Notebooks de desenvolvimento
│   └── dataview.ipynb                  # Notebook principal com o pipeline executado
│
├── outputs/                            # Resultados e relatórios gerados
│   ├── metricas_por_mes.csv            # Resumo de receitas e volumes mensais
│   ├── segmentacao_clientes.csv        # Tabela com classificação dos clientes
│   ├── estatisticas_gerais.json        # Resumo estatístico calculado com NumPy
│   └── graficos/                       # Gráficos PNG gerados para apresentações
│       ├── receita_por_mes.png         # Gráfico de linha (receita temporal)
│       ├── top_produtos.png            # Gráfico de barras (ranking de produtos)
│       └── dist_regiao.png             # Boxplot (distribuição por região)
│
├── README.md                           # Documentação completa do projeto
└── .gitignore                          # Arquivos e pastas a ignorar no versionamento
```

---

##  Instalação e Execução

Você pode executar este projeto de duas formas principais:

### Opção 1: No Google Colab (Recomendado)
1. Faça o upload do arquivo `notebooks/dataview.ipynb` no Google Colab.
2. Como o ambiente do Colab já vem com todas as bibliotecas necessárias pré-instaladas, basta executar as células de cima para baixo.
3. Os arquivos de saída e pastas serão criados diretamente no sistema de arquivos do Colab e podem ser baixados individualmente.

### Opção 2: Localmente (VS Code ou Terminal)
1. Certifique-se de ter o Python 3.8+ instalado.
2. Clone o repositório em sua máquina:
   ```bash
   git clone https://github.com/[seu-usuario]/[seu-repositorio].git
   cd [seu-repositorio]
   ```
3. Instale as dependências requeridas utilizando o `pip`:
   ```bash
   pip install pandas numpy matplotlib seaborn notebook
   ```
4. Abra o notebook usando o VS Code (com a extensão de Jupyter) ou execute no terminal para abrir no navegador:
   ```bash
   jupyter notebook notebooks/dataview.ipynb
   ```
5. Execute todas as células (`Run All`).


##  Tecnologias e Ferramentas Utilizadas
- **Python 3.10**: Linguagem base do projeto.
- **Pandas**: Para leitura, manipulação, filtragem, agrupamento (`groupby`) e exportação de dados.
- **NumPy**: Para manipulação de arrays puros, operações vetorizadas de alta performance, broadcasting e indexação booleana.
- **Matplotlib & Seaborn**: Para criação de visualizações elegantes, com customização de títulos, rótulos e exportação de arquivos PNG.
- **Módulo `re` (Expressões Regulares)**: Para processamento e normalização robusta de colunas de texto.
- **Módulo `datetime`**: Para manipulação, ordenação e conversão de atributos temporais.
- **Jupyter Notebook / VS Code**: Ambientes integrados de desenvolvimento.

---

##  Resumo do Pipeline de Análise (RF01 a RF12)

1. **RF01 - Criação do Dataset**: Geração de dados de vendas sintéticos simulando o mundo real com nulos (`None` em quantidade/preço), string com espaços extras e datas com formato textual inválido ("DATA INVALIDA").
2. **RF02 - Inspeção de Dados**: Diagnóstico inicial das dimensões (`.shape`), tipos de dados (`.dtypes`), valores faltantes (`.isnull().sum()`) e estatísticas descritivas básicas.
3. **RF03 - Limpeza de Dados**:
   - Limpeza de strings com Regex (`re.sub` colapsando múltiplos espaços em branco e `.strip()` retirando rebarbas nas extremidades).
   - Conversão de datas com `pd.to_datetime` utilizando `errors="coerce"` para forçar datas inválidas a `NaT`, permitindo posterior exclusão.
   - Remoção de linhas sem informações cruciais (`quantidade` e `preco_unitario`), garantindo consistência numérica nos cálculos de receita.
   - Conversão dos tipos de dados finais para `int` (quantidade) e `float` (preço unitário).
   - Exportação da base limpa intermediária em `data/processed/v1_com_outliers/vendas_v1.csv`.
4. **RF04 - Tratamento de Outliers (IQR)**:
   - Identificação de valores extremos pelo método do Intervalo Interquartil (IQR), calculando os limites superiores e inferiores ($Q1 - 1.5 \times IQR$ e $Q3 + 1.5 \times IQR$).
   - Geração de duas versões: `v1` (mantém outliers) e `v2` (remove outliers nas colunas `quantidade` e em uma cópia temporária de `receita_total`).
   - Salva a versão tratada em `data/processed/v2_outliers_tratado/vendas_v2.csv`.
5. **RF05 - Criação de Colunas Derivadas**:
   - Criação da coluna `receita_total` ($quantidade \times preco\_unitario$).
   - Extração estruturada de partes da data: `mes`, `trimestre` (formato "Q1", "Q2", etc.) e `ano`.
   - Criação da coluna categórica `faixa_receita_item` utilizando a transformação condicional vetorizada `np.select` (baixo, médio e alto valor por item).
6. **RF06 - Agrupamentos (groupby)**: Consolidação de tabelas de receita e vendas agrupadas por Mês, Top 5 Produtos, Categoria de Produto e Região Comercial (calculando volume total e ticket médio).
7. **RF07 - Segmentação de Clientes**: Agrupamento por cliente com soma de gastos acumulados e classificação em níveis de gastos (**Bronze**, **Prata**, **Ouro**) através de funções **lambda** com ternários aninhados.
8. **RF08 - Estatísticas com NumPy**: Conversão das receitas para array NumPy (`.to_numpy()`), cálculo vetorizado de estatísticas (Média, Mediana, Desvio Padrão, Percentis 25 e 75), demonstração de **broadcasting** (percentual de contribuição por venda) e filtragem de registros com indexação booleana (vendas acima da média).
9. **RF09 - Criação de Gráficos**:
   - **Linha**: Evolução da receita mensal histórica de 2024.
   - **Barras Horizontais**: Ranking das maiores fontes de receita por produto (Top 5).
   - **Boxplot**: Distribuição e dispersão de valores de vendas por Região geográfica para identificar comportamentos regionais.
10. **RF10 - Modularização**: Encapsulamento de todas as etapas em funções documentadas com *docstrings* explicativos. Demonstração de funções de ordem superior com passagem de callbacks lambda (`aplicar_transformacao`).
11. **RF11 - Importação e Exportação**: Salvamento dos arquivos finais nos formatos CSV (com codificação `utf-8-sig` para compatibilidade com o Excel) e JSON formatado de forma amigável, testando e validando a leitura do JSON recém-criado.
12. **RF12 - Consolidação Final**: Geração do arquivo final unificado `data/final/vendas_final.csv` e validação de consistência dos caminhos criados no pipeline.

---

##  Decisão sobre Tratamento de Outliers (v1 vs v2)

> [!NOTE]
> Para a consolidação no dataset final (`data/final/vendas_final.csv`), optamos pela **Versão v2 (outliers tratados)**.
> **Justificativa**: Em uma análise de varejo, a presença de outliers em quantidade vendida ou valor total de transação (geralmente compras institucionais ou erros operacionais atípicos) pode distorcer métricas agregadas cruciais como o ticket médio regional e o comportamento sazonal de vendas da empresa. A remoção dos outliers assegura que os relatórios reflitam o padrão de consumo da grande maioria dos clientes, auxiliando em tomadas de decisões de marketing e estoque com menor variância estatística.
> Contudo, a versão `v1` foi preservada em `data/processed/v1_com_outliers/` para fins comparativos e de auditoria de compras de grande escala.

---

## Próximos Passos e Melhorias Futuras
1. **Modelagem Preditiva**: Integração de modelos de séries temporais (como ARIMA ou Prophet) sobre a base consolidada para prever a receita total dos próximos trimestres.
2. **Integração com Dashboards**: Criação de uma interface web dinâmica de visualização usando Streamlit para permitir filtros dinâmicos de categoria e região em tempo real.
3. **Automação de Pipeline**: Implementação de testes unitários (`pytest`) sobre as funções de limpeza de dados e orquestração do pipeline em um script de CI/CD (ex: GitHub Actions) para rodar a cada novo lote de dados imputado.
