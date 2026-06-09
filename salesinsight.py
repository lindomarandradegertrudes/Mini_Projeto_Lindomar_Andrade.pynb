# =============================================================================
#  SalesInsight PY – Pipeline de Análise e Visualização de Dados de Vendas
#  Desenvolvedor(a) em IA para Análise Preditiva – Módulo 01 – Semana 08
# =============================================================================

import os
import re
import json
import sys
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

from datetime import datetime, timedelta
import random

# Configuração de suporte a UTF-8 no console do Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Configuração global de logging para rastreabilidade
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# =============================================================================
# RF01 – Criar ou Carregar o Dataset de Vendas
# =============================================================================

def gerar_dataset_vendas(n_registros: int = 200, seed: int = 42) -> pd.DataFrame:
    """
    Gera um dataset sintético de vendas com dados intencionalmente sujos
    para exercitar o pipeline de limpeza e transformação.

    Parâmetros
    ----------
    n_registros : int
        Quantidade de linhas a gerar.
    seed : int
        Semente para reprodutibilidade.

    Retorna
    -------
    pd.DataFrame com as colunas:
        id_venda, data_venda, cliente, produto, categoria,
        regiao, quantidade, preco_unitario
    """
    random.seed(seed)
    np.random.seed(seed)

    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor", "Teclado", "Mouse", "Headset"]
    categorias = {
        "Notebook": "Computadores", "Smartphone": "Celulares", "Tablet": "Celulares",
        "Monitor": "Computadores", "Teclado": "Periféricos",
        "Mouse": "Periféricos", "Headset": "Periféricos"
    }
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    clientes = [f"Cliente_{i:03d}" for i in range(1, 51)]
    preco_base = {
        "Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
        "Monitor": 1200, "Teclado": 250, "Mouse": 120, "Headset": 350
    }
    data_inicio = datetime(2024, 1, 1)

    dados = []
    for i in range(n_registros):
        produto = random.choice(produtos)
        quantidade = random.randint(1, 10)
        preco = round(preco_base[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))

        # ── Sujeira intencional ──────────────────────────────────────────────
        if random.random() < 0.05:
            quantidade = None          # valor nulo
        if random.random() < 0.04:
            preco = None               # valor nulo
        if random.random() < 0.03:
            produto = "  " + produto   # espaço extra
        data_str = (
            data.strftime("%Y-%m-%d")
            if random.random() > 0.02
            else "DATA INVÁLIDA"
        )

        dados.append({
            "id_venda":       i + 1,
            "data_venda":     data_str,
            "cliente":        random.choice(clientes),
            "produto":        produto,
            "categoria":      categorias.get(produto.strip(), "Outros"),
            "regiao":         random.choice(regioes),
            "quantidade":     quantidade,
            "preco_unitario": preco,
        })

    return pd.DataFrame(dados)


# =============================================================================
# RF02 – Inspecionar e Descrever os Dados
# =============================================================================

def inspecionar_dados(df: pd.DataFrame) -> None:
    """Exibe informações básicas do DataFrame no console."""
    print("\n" + "=" * 50)
    print("       INSPEÇÃO INICIAL DO DATASET")
    print("=" * 50)
    print(f"  Shape         : {df.shape}")
    print(f"\n  Colunas       : {list(df.columns)}")
    print(f"\n  Tipos de dados:\n{df.dtypes.to_string()}")
    print(f"\n  Valores nulos por coluna:\n{df.isnull().sum().to_string()}")
    print(f"\n  Primeiros registros:\n{df.head().to_string()}")
    print(f"\n  Estatísticas descritivas:\n{df.describe(include='all').to_string()}")


# =============================================================================
# RF03 – Limpar e Tratar os Dados
# =============================================================================

def limpar_dados(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Limpa e trata o DataFrame de vendas.
    Trata: espaços extras, datas inválidas, valores nulos e tipos incorretos.

    Retorna
    -------
    (df_limpo, relatorio_limpeza)
    """
    n_inicial = len(df)
    relatorio: dict = {}

    # 1. Remover espaços extras em todas as colunas de texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # 2. Converter data e remover datas inválidas
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    n_datas_invalidas = int(df["data_venda"].isnull().sum())
    df = df.dropna(subset=["data_venda"])
    relatorio["datas_invalidas_removidas"] = n_datas_invalidas

    # 3. Remover linhas com quantidade ou preço nulos
    n_antes = len(df)
    df = df.dropna(subset=["quantidade", "preco_unitario"])
    relatorio["linhas_nulas_removidas"] = n_antes - len(df)

    # 4. Garantir tipos numéricos corretos
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    n_final = len(df)
    relatorio["registros_iniciais"] = n_inicial
    relatorio["registros_finais"] = n_final
    relatorio["registros_removidos_total"] = n_inicial - n_final

    logging.info(
        f"Limpeza de dados concluída. Removidos: {relatorio['registros_removidos_total']} "
        f"(Datas inválidas: {relatorio['datas_invalidas_removidas']}, Nulos: {relatorio['linhas_nulas_removidas']}). "
        f"Registros finais: {n_final}."
    )

    print("\n=== RELATÓRIO DE LIMPEZA ===")
    for chave, valor in relatorio.items():
        print(f"  {chave}: {valor}")

    return df.reset_index(drop=True), relatorio


# =============================================================================
# RF04 – Criar Colunas Derivadas com Transformações
# =============================================================================

def criar_colunas_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas calculadas e derivadas a partir do dataset limpo."""

    # Receita total por linha
    df["receita_total"] = df["quantidade"] * df["preco_unitario"]

    # Extração de componentes de data com mapeamento estático de meses (independente de locale)
    nomes_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    df["mes"] = df["data_venda"].dt.month
    df["mes_nome"] = df["mes"].map(nomes_meses)
    df["trimestre"] = df["data_venda"].dt.quarter.apply(lambda q: f"Q{q}")
    df["ano"] = df["data_venda"].dt.year

    # Classificação da receita por item com np.select (vetorizado)
    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000,
    ]
    classificacoes = ["Baixo Valor", "Médio Valor", "Alto Valor"]
    df["faixa_receita_item"] = np.select(condicoes, classificacoes, default="Não Classificado")

    print("\n=== COLUNAS DERIVADAS CRIADAS ===")
    print(df[["data_venda", "receita_total", "mes", "trimestre", "faixa_receita_item"]].head().to_string())

    return df


# =============================================================================
# RF05 – Calcular Métricas Agregadas (groupby)
# =============================================================================

def calcular_metricas(df: pd.DataFrame) -> dict:
    """Calcula e retorna um dicionário com métricas agrupadas."""
    metricas: dict = {}

    # Receita por mês
    por_mes = (
        df.groupby("mes")
        .agg(
            receita_total=("receita_total", "sum"),
            quantidade=("quantidade", "sum"),
            n_vendas=("id_venda", "count"),
        )
        .reset_index()
        .sort_values("mes")
    )
    metricas["por_mes"] = por_mes

    # Top 5 produtos por receita
    top_produtos = (
        df.groupby("produto")["receita_total"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    metricas["top_produtos"] = top_produtos

    # Receita por categoria
    por_categoria = df.groupby("categoria")["receita_total"].sum().reset_index()
    metricas["por_categoria"] = por_categoria

    # Receita e ticket médio por região
    por_regiao = (
        df.groupby("regiao")
        .agg(
            receita_total=("receita_total", "sum"),
            media_ticket=("receita_total", "mean"),
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )
    metricas["por_regiao"] = por_regiao

    for nome, tabela in metricas.items():
        print(f"\n=== {nome.upper().replace('_', ' ')} ===")
        print(tabela.to_string(index=False))

    return metricas


# =============================================================================
# RF06 – Segmentar Clientes por Nível de Gasto
# =============================================================================

def segmentar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Segmenta clientes pelo total gasto usando groupby e lambda.
    Bronze < R$5.000 | Prata R$5.000–15.000 | Ouro > R$15.000
    """
    clientes = df.groupby("cliente")["receita_total"].sum().reset_index()
    clientes.columns = ["cliente", "total_gasto"]

    # Classificação com função lambda (RF11 também coberto aqui)
    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda gasto: "Ouro" if gasto > 15_000 else ("Prata" if gasto >= 5_000 else "Bronze")
    )
    clientes = clientes.sort_values("total_gasto", ascending=False)

    print("\n=== SEGMENTAÇÃO DE CLIENTES ===")
    print(clientes.head(10).to_string(index=False))
    print(f"\n  Distribuição de segmentos:\n{clientes['segmento'].value_counts().to_string()}")

    return clientes


# =============================================================================
# RF07 – Calcular Estatísticas com NumPy
# =============================================================================

def calcular_estatisticas_numpy(df: pd.DataFrame) -> dict:
    """Usa NumPy para calcular estatísticas sobre as receitas."""
    print("\n=== ESTATÍSTICAS COM NUMPY ===")

    receitas = df["receita_total"].to_numpy()          # array NumPy

    media = np.mean(receitas)
    mediana = np.median(receitas)
    desvio = np.std(receitas)
    total = np.sum(receitas)
    p25 = np.percentile(receitas, 25)
    p75 = np.percentile(receitas, 75)

    print(f"  Receita média por venda:   R$ {media:,.2f}")
    print(f"  Receita mediana por venda: R$ {mediana:,.2f}")
    print(f"  Desvio padrão:             R$ {desvio:,.2f}")
    print(f"  Receita total:             R$ {total:,.2f}")
    print(f"  Percentil 25 (Q1):         R$ {p25:,.2f}")
    print(f"  Percentil 75 (Q3):         R$ {p75:,.2f}")

    # Broadcasting: normalizar receitas entre 0 e 1
    receitas_norm = (receitas - receitas.min()) / (receitas.max() - receitas.min())
    print(f"\n  Receitas normalizadas (primeiros 5): {receitas_norm[:5].round(4)}")

    # Operação vetorizada: vendas acima da média (sem loop)
    acima = receitas[receitas > media]
    print(f"\n  Vendas acima da média: {len(acima)} de {len(receitas)}")

    return {
        "media": float(media),
        "mediana": float(mediana),
        "desvio_padrao": float(desvio),
        "total": float(total),
        "p25": float(p25),
        "p75": float(p75),
    }


# =============================================================================
# RF08 – Criar Visualizações com Matplotlib e Seaborn
# =============================================================================

def gerar_visualizacoes(
    df: pd.DataFrame,
    metricas: dict,
    output_dir: str = "outputs/graficos",
) -> None:
    """Gera e exporta 3 gráficos informativos em PNG com design premium."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({
            "figure.figsize": (11, 5.5),
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "font.family": "sans-serif"
        })

        # Formatação monetária em 'k' (milhares)
        formatter = ticker.FuncFormatter(lambda x, pos: f"R$ {x*1e-3:.0f}k" if x >= 1e3 else f"R$ {x:.0f}")

        # ── Gráfico 1: Receita total por mês (linha) ────────────────────────────
        por_mes = metricas["por_mes"]
        fig, ax = plt.subplots()
        ax.plot(por_mes["mes"], por_mes["receita_total"], marker="o", markersize=6, linewidth=2.5, color="#1E88E5")
        ax.fill_between(por_mes["mes"], por_mes["receita_total"], alpha=0.15, color="#1E88E5")
        ax.set_title("Evolução da Receita Total por Mês (2024)", pad=15)
        ax.set_xlabel("Mês")
        ax.set_ylabel("Receita Total")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(
            ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"],
            rotation=0,
        )
        ax.yaxis.set_major_formatter(formatter)
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        caminho1 = os.path.join(output_dir, "vendas_por_mes.png")
        plt.savefig(caminho1, dpi=150)
        plt.close()
        logging.info(f"Gráfico exportado: {caminho1}")

        # ── Gráfico 2: Top 5 produtos por receita (barras horizontais) ──────────
        top = metricas["top_produtos"]
        fig, ax = plt.subplots()
        
        # Correção do aviso do Seaborn: atribuir y para hue e desativar legenda
        sns.barplot(data=top, y="produto", x="receita_total", ax=ax, hue="produto", palette="Blues_r", legend=False)
        ax.set_title("Top 5 Produtos por Faturamento", pad=15)
        ax.set_xlabel("Receita Total")
        ax.set_ylabel("Produto")
        ax.xaxis.set_major_formatter(formatter)
        
        # Rótulos das barras formatados de forma limpa
        for container in ax.containers:
            ax.bar_label(container, fmt=lambda x: f" R$ {x*1e-3:.1f}k" if x >= 1e3 else f" R$ {x:.0f}", padding=3)
            
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        caminho2 = os.path.join(output_dir, "top_produtos.png")
        plt.savefig(caminho2, dpi=150)
        plt.close()
        logging.info(f"Gráfico exportado: {caminho2}")

        # ── Gráfico 3: Distribuição de receita por região (boxplot) ─────────────
        fig, ax = plt.subplots()
        # Correção do aviso do Seaborn: atribuir x para hue e desativar legenda
        sns.boxplot(data=df, x="regiao", y="receita_total", ax=ax, hue="regiao", palette="Set2", legend=False)
        ax.set_title("Distribuição do Valor de Vendas por Região", pad=15)
        ax.set_xlabel("Região")
        ax.set_ylabel("Receita por Venda")
        ax.yaxis.set_major_formatter(formatter)
        
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        caminho3 = os.path.join(output_dir, "distribuicao_regioes.png")
        plt.savefig(caminho3, dpi=150)
        plt.close()
        logging.info(f"Gráfico exportado: {caminho3}")

        print("\n=== VISUALIZAÇÕES GERADAS COM SUCESSO ===")
    except Exception as e:
        logging.error(f"Erro ao gerar visualizações: {e}")
        raise


# =============================================================================
# RF11 – Funções Lambda e Funções de Ordem Superior
# =============================================================================

def processar_coluna(df: pd.DataFrame, coluna: str, funcao_transformacao) -> pd.DataFrame:
    """
    Aplica uma função de transformação a uma coluna do DataFrame.
    Demonstra o uso de funções como argumentos (higher-order function / callback).

    Parâmetros
    ----------
    df : pd.DataFrame
    coluna : str — coluna de origem
    funcao_transformacao : callable — função (pode ser lambda) aplicada linha a linha
    """
    df[f"{coluna}_transformado"] = df[coluna].apply(funcao_transformacao)
    logging.info(f"Coluna '{coluna}_transformado' criada com sucesso.")
    return df


# =============================================================================
# RF12 – Ler e Escrever Arquivos (CSV e JSON)
# =============================================================================

def exportar_resultados(metricas: dict, clientes: pd.DataFrame, stats: dict) -> None:
    """Exporta métricas em CSV e estatísticas em JSON; relê o JSON para confirmar com tratamento de erros."""
    try:
        os.makedirs("outputs", exist_ok=True)

        # CSV – métricas por mês
        caminho_csv = "outputs/metricas_por_mes.csv"
        metricas["por_mes"].to_csv(caminho_csv, index=False, encoding="utf-8-sig")
        logging.info(f"CSV exportado com sucesso: {caminho_csv}")

        # CSV – segmentação de clientes
        caminho_clientes = "outputs/segmentacao_clientes.csv"
        clientes.to_csv(caminho_clientes, index=False, encoding="utf-8-sig")
        logging.info(f"CSV exportado com sucesso: {caminho_clientes}")

        # JSON – estatísticas gerais
        caminho_json = "outputs/estatisticas_gerais.json"
        stats_serializaveis = {k: round(float(v), 2) for k, v in stats.items()}
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(stats_serializaveis, f, indent=4, ensure_ascii=False)
        logging.info(f"JSON exportado com sucesso: {caminho_json}")

        # Leitura de confirmação (RF12 exige json.load)
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados_lidos = json.load(f)
        logging.info("Confirmação de leitura do JSON realizada com sucesso.")
        print(f"\n  Conteúdo do JSON exportado:\n  {json.dumps(dados_lidos, indent=2, ensure_ascii=False)}")
    except Exception as e:
        logging.error(f"Erro ao exportar resultados em CSV/JSON: {e}")
        raise


# =============================================================================
# RF13 – Expressões Regulares para Limpeza de Dados
# =============================================================================

def limpar_strings_com_regex(df: pd.DataFrame) -> pd.DataFrame:
    """
    Usa expressões regulares para limpeza e validação de colunas de texto.
    - Remove caracteres especiais do nome do cliente.
    - Valida se o cliente segue o padrão Cliente_XXX.
    """
    # 1. Remover caracteres não alfanuméricos (exceto underline e espaço)
    df["cliente_limpo"] = df["cliente"].apply(
        lambda s: re.sub(r"[^a-zA-Z0-9_ ]", "", str(s)).strip()
    )

    # 2. Validar padrão Cliente_NNN
    padrao_cliente = re.compile(r"^Cliente_\d{3}$")
    df["cliente_valido"] = df["cliente_limpo"].apply(
        lambda s: bool(padrao_cliente.match(s))
    )

    n_invalidos = int((~df["cliente_valido"]).sum())
    print(f"\n=== LIMPEZA COM REGEX ===")
    print(f"  Clientes com formato inválido: {n_invalidos}")
    print(f"  Amostra de clientes limpos: {df['cliente_limpo'].head(5).tolist()}")

    return df


# =============================================================================
# RF09 – Classe AnalisadorDeVendas
# =============================================================================

class AnalisadorDeVendas:
    """
    Encapsula o pipeline de análise de vendas.
    Mantém o estado do DataFrame e os resultados intermediários.
    Padrão fluent interface: cada método retorna self para encadeamento.
    """

    def __init__(self, caminho_arquivo: str) -> None:
        self.caminho_arquivo: str = caminho_arquivo
        self.df_bruto: pd.DataFrame | None = None
        self.df_limpo: pd.DataFrame | None = None
        self.metricas: dict = {}
        self.clientes: pd.DataFrame | None = None
        self.relatorio_limpeza: dict = {}
        self.stats_numpy: dict = {}

    def carregar(self) -> "AnalisadorDeVendas":
        """Lê o arquivo CSV e armazena o DataFrame bruto com tratamento de erros."""
        try:
            self.df_bruto = pd.read_csv(self.caminho_arquivo)
            logging.info(f"Arquivo carregado com sucesso: {self.caminho_arquivo} | Registros: {len(self.df_bruto)}")
        except FileNotFoundError:
            logging.error(f"Arquivo não encontrado no caminho fornecido: {self.caminho_arquivo}")
            raise
        except Exception as e:
            logging.error(f"Falha inesperada ao ler arquivo {self.caminho_arquivo}: {e}")
            raise
        return self

    def limpar(self) -> "AnalisadorDeVendas":
        """Limpa os dados e armazena o DataFrame tratado."""
        if self.df_bruto is None:
            logging.warning("O DataFrame bruto está vazio. Chamando .carregar() antes de .limpar().")
            self.carregar()
        self.df_limpo, self.relatorio_limpeza = limpar_dados(self.df_bruto.copy())
        return self

    def transformar(self) -> "AnalisadorDeVendas":
        """Aplica transformações e cria colunas derivadas."""
        if self.df_limpo is None:
            logging.warning("O DataFrame limpo está vazio. Chamando .limpar() antes de .transformar().")
            self.limpar()
        self.df_limpo = criar_colunas_derivadas(self.df_limpo)
        # RF11 – uso de lambda em contextos distintos com função de ordem superior
        print("\n=== TRANSFORMAÇÕES ADICIONAIS (Higher-Order Functions + Lambda) ===")
        self.df_limpo = processar_coluna(
            self.df_limpo, "receita_total", lambda x: round(x / 1_000, 2)
        )
        self.df_limpo = processar_coluna(
            self.df_limpo, "quantidade", lambda x: "Alto" if x > 5 else "Baixo"
        )
        # RF11 – lambda em sorted (fora de apply)
        produtos_unicos = self.df_limpo.groupby("produto")["receita_total"].sum().reset_index()
        produtos_lista = produtos_unicos.to_dict("records")
        produtos_ord = sorted(produtos_lista, key=lambda p: p["receita_total"], reverse=True)
        print(f"\n  Ranking de produtos (lambda + sorted):")
        for i, p in enumerate(produtos_ord, 1):
            print(f"    {i}. {p['produto']:12s} – R$ {p['receita_total']:,.2f}")
        return self

    def analisar(self) -> "AnalisadorDeVendas":
        """Calcula métricas e segmentações."""
        if self.df_limpo is None:
            logging.warning("O DataFrame limpo está vazio. Executando etapas prévias.")
            self.transformar()
        self.metricas = calcular_metricas(self.df_limpo)
        self.clientes = segmentar_clientes(self.df_limpo)
        self.stats_numpy = calcular_estatisticas_numpy(self.df_limpo)
        return self

    def visualizar(self) -> "AnalisadorDeVendas":
        """Gera e exporta os gráficos."""
        if self.df_limpo is None or not self.metricas:
            logging.warning("DataFrame ou métricas ausentes. Executando .analisar() primeiro.")
            self.analisar()
        gerar_visualizacoes(self.df_limpo, self.metricas)
        return self

    def exportar_relatorio(self, caminho: str = "outputs/relatorio_resumo.csv") -> "AnalisadorDeVendas":
        """Exporta o relatório de métricas por mês em CSV."""
        try:
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            self.metricas["por_mes"].to_csv(caminho, index=False, encoding="utf-8-sig")
            logging.info(f"Relatório de resumo exportado com sucesso em: {caminho}")
        except Exception as e:
            logging.error(f"Erro ao exportar o relatório de resumo em {caminho}: {e}")
        return self

    def resumo(self) -> None:
        """Exibe um resumo executivo do pipeline."""
        print("\n" + "=" * 50)
        print("     RESUMO EXECUTIVO – SALESINSIGHT PY")
        print("=" * 50)
        print(f"  Arquivo analisado:   {self.caminho_arquivo}")
        print(f"  Registros brutos:    {self.relatorio_limpeza.get('registros_iniciais', 'N/A')}")
        print(f"  Registros limpos:    {self.relatorio_limpeza.get('registros_finais', 'N/A')}")
        receita = (
            self.df_limpo["receita_total"].sum()
            if self.df_limpo is not None
            else 0
        )
        print(f"  Receita total anual: R$ {receita:,.2f}")
        if self.clientes is not None:
            top = self.clientes.iloc[0]
            print(f"  Cliente top:         {top['cliente']} (R$ {top['total_gasto']:,.2f})")
        print("=" * 50)


# =============================================================================
# RF10 – Herança: AnalisadorComProjecao
# =============================================================================

class AnalisadorComProjecao(AnalisadorDeVendas):
    """
    Extensão do AnalisadorDeVendas com projeção simples de tendência.
    Herda todos os métodos da classe pai e adiciona projeção por média móvel.
    """

    def __init__(self, caminho_arquivo: str, meses_projecao: int = 3) -> None:
        super().__init__(caminho_arquivo)          # chama o __init__ do pai
        self.meses_projecao: int = meses_projecao
        self.projecoes: list[dict] = []

    def projetar_tendencia(self) -> "AnalisadorComProjecao":
        """
        Projeta a receita dos próximos meses com base na média móvel
        dos últimos 3 meses registrados. Método simples sem ML.
        """
        if not self.metricas or "por_mes" not in self.metricas:
            print("[AVISO] Rode .analisar() antes de .projetar_tendencia().")
            return self

        por_mes = self.metricas["por_mes"].sort_values("mes")
        receitas_hist = por_mes["receita_total"].to_numpy()

        ultimos_3 = receitas_hist[-3:]
        media_movel = np.mean(ultimos_3)
        tendencia = np.std(ultimos_3) * 0.1   # fator de crescimento simples

        ultimo_mes = int(por_mes["mes"].max())

        print("\n=== PROJEÇÃO DE TENDÊNCIA (Média Móvel Simples) ===")
        print(f"  Base: média dos últimos 3 meses = R$ {media_movel:,.2f}")

        self.projecoes = []
        for i in range(1, self.meses_projecao + 1):
            mes_proj = (ultimo_mes + i - 1) % 12 + 1
            receita_proj = media_movel + (tendencia * i)
            self.projecoes.append({"mes": mes_proj, "receita_projetada": round(receita_proj, 2)})
            print(f"  Mês {mes_proj:02d} (projeção): R$ {receita_proj:,.2f}")

        return self

    def exibir_projecao_detalhada(self) -> None:
        """Exibe as projeções calculadas em formato detalhado."""
        if not self.projecoes:
            print("[AVISO] Nenhuma projeção disponível. Rode .projetar_tendencia() primeiro.")
            return
        print("\n=== DETALHAMENTO DAS PROJEÇÕES ===")
        for p in self.projecoes:
            print(f"  Mês {p['mes']:02d}: R$ {p['receita_projetada']:,.2f}")


# =============================================================================
# RF14 – Ponto de Entrada (main)
# =============================================================================

def main() -> None:
    """Executa o pipeline completo do SalesInsight PY de ponta a ponta."""
    print("\n" + "=" * 60)
    print("   SALESINSIGHT PY – Pipeline de Análise de Dados de Vendas")
    print("=" * 60)

    # ── Etapa 0: Gerar dataset sintético se não existir ─────────────────────
    CAMINHO_CSV = "vendas.csv"
    if not os.path.exists(CAMINHO_CSV):
        print("\n[INFO] Gerando dataset sintético...")
        df_gerado = gerar_dataset_vendas(n_registros=200)
        df_gerado.to_csv(CAMINHO_CSV, index=False)
        print(f"  Dataset salvo em '{CAMINHO_CSV}' ({len(df_gerado)} registros).")
    else:
        print(f"\n[INFO] Dataset '{CAMINHO_CSV}' já existe. Carregando...")

    # ── Etapa 1: Inspeção inicial (antes da limpeza) ─────────────────────────
    df_raw = pd.read_csv(CAMINHO_CSV)
    inspecionar_dados(df_raw)

    # ── Etapas 2-6: Pipeline via classe com herança ──────────────────────────
    analisador = AnalisadorComProjecao(CAMINHO_CSV, meses_projecao=3)

    (
        analisador
        .carregar()
        .limpar()
        .transformar()
        .analisar()
        .projetar_tendencia()
        .visualizar()
        .exportar_relatorio()
    )

    # ── Etapa extra: limpeza com regex (RF13) ────────────────────────────────
    analisador.df_limpo = limpar_strings_com_regex(analisador.df_limpo)

    # ── Etapa extra: exportação JSON (RF12) ──────────────────────────────────
    print("\n=== EXPORTANDO RESULTADOS ===")
    exportar_resultados(analisador.metricas, analisador.clientes, analisador.stats_numpy)

    # ── Resumo final ─────────────────────────────────────────────────────────
    analisador.resumo()
    analisador.exibir_projecao_detalhada()

    print("\n[CONCLUÍDO] Pipeline finalizado com sucesso!")


if __name__ == "__main__":
    main()
