import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ----------------------------------------------------
# 1. FUNÇÕES DE LÓGICA E CATEGORIZAÇÃO
# ----------------------------------------------------

def categorize_transaction(description):
    """
    Categoriza transações baseado na descrição. 
    (Utilize a lógica de palavras-chave que você já implementou)
    """
    # Lógica de Categorização (Exemplo baseado no seu código anterior)
    description = str(description).lower()
    
    categories = {
        'Alimentação': ['restaurante', 'lanchonete', 'padaria', 'supermercado', 'mercado', 'ifood', 'comida'],
        'Transporte': ['uber', 'taxi', 'combustivel', 'posto', 'gasolina', 'metro'],
        'Lazer': ['cinema', 'teatro', 'show', 'netflix', 'spotify', 'amazon', "shopee"],
        'Saque': ['saque dinheiro banco 24h'],
        'Serviços/Contas': ['tarifa', 'servico', 'agua', 'energia', 'net', 'pix enviado'],
        'Educação': ['escola', 'curso', 'livro'],
        'Remuneração': ['salario', 'credito de', 'remuneracao'],
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in description:
                return category
                
    return 'Outros'

def process_uploaded_csv(uploaded_file):
    """
    Lê e padroniza o DataFrame de extrato CSV, consolidando Crédito e Débito.
    """
    # 1. Leitura do CSV
    csv_content = uploaded_file.read().decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_content), sep=",")

    print(df)  # Debug: Verifique as primeiras linhas do DataFrame
    
    # 2. Padronização das Colunas (Adaptando para extratos típicos)
    
# Tenta identificar as colunas automaticamente
# Procura por colunas que podem conter datas, valores e descrições
    date_col = None
    value_col = None
    description_col = None

    for col in df.columns:
        col_lower = col.lower()
        if any(word in col_lower for word in ['data', 'date', 'dt']):
            date_col = col
        elif any(word in col_lower for word in ['valor', 'value', 'amount', 'quantia']):
            value_col = col
        elif any(word in col_lower for word in ['descricao', 'description', 'historico', 'desc']):
            description_col = col

    # Se não encontrou as colunas, usa as primeiras disponíveis
    if not date_col and len(df.columns) > 0:
        date_col = df.columns[0]
    if not value_col and len(df.columns) > 1:
        value_col = df.columns[1]
    if not description_col and len(df.columns) > 2:
        description_col = df.columns[2]

    # Limpa e converte os dados
    df[value_col] = pd.to_numeric(df[value_col].astype(str).str.replace('.', ',').str.replace(r'[^\d.-]', '', regex=True), errors='coerce')

    # Remove linhas com valores NaN
    df = df.dropna(subset=[value_col])

    # Categoriza as transações
    if description_col:
        df['categoria'] = df[description_col].apply(categorize_transaction)
    else:
        df['categoria'] = 'Outros'

    # Converte datas
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        df = df.dropna(subset=[date_col])
        df['mes_ano'] = df[date_col].dt.to_period('M').astype(str)
    else:
        df['mes_ano'] = 'N/A'

    # Calcula métricas
    receitas = df[df[value_col] > 0][value_col].sum()
    despesas = abs(df[df[value_col] < 0][value_col].sum())
    saldo = receitas - despesas

    print(f"Receitas: {receitas}, Despesas: {despesas}, Saldo: {saldo}")

    # Aplica a categorização
    df['categoria'] = df[description_col].apply(categorize_transaction)

    return df

# ----------------------------------------------------
# 2. INTERFACE STREAMLIT
# ----------------------------------------------------

st.set_page_config(layout="wide")
st.title("💸 Dashboard de Análise de Extratos")
st.caption("Faça o upload do seu extrato no formato CSV.")

# Widget de Upload
uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=['csv'])

if uploaded_file is not None:
    
    with st.spinner('Processando e analisando dados...'):
        
        df_final = process_uploaded_csv(uploaded_file)

        print(df_final)  # Debug: Verifique as primeiras linhas do DataFrame final   
        
        if df_final is not None:

            print(df_final)  # Debug
            
            # Cálculo de Métricas
            print(df_final['Valor'].sum()) 
             # Debug: Verifique os valores na coluna 'valor'
            receitas = df_final[df_final['Valor'] > 0]['Valor'].sum()
            print("Receitas calculadas:", receitas)  # Debug
            despesas = abs(df_final[df_final['Valor'] < 0]['Valor'].sum())
            saldo = receitas - despesas

            # ----------------------------------
            # Exibição de Métricas (KPIs)
            # ----------------------------------
            st.header("Resumo Financeiro")
            col1, col2, col3 = st.columns(3)
            col1.metric("Receitas Totais", f"R$ {receitas:.2f}")
            col2.metric("Despesas Totais", f"R$ {despesas:.2f}")
            col3.metric("Saldo Líquido", f"R$ {saldo:.2f}", delta=f"{saldo:.2f}")

            st.markdown("---")
            
            # ----------------------------------
            # Gráfico 1: Despesas por Categoria (Pizza)
            # ----------------------------------
            st.subheader("Distribuição de Gastos")
            
            # Filtra apenas despesas
            df_despesas = df_final[df_final['Valor'] < 0].copy()
            
            # Agrupa e calcula a soma absoluta
            despesas_por_categoria = df_despesas.groupby('categoria')['Valor'].sum().abs().reset_index()
            
            fig_pizza = px.pie(
                despesas_por_categoria,
                values='Valor',
                names='categoria',
                title='Proporção de Gastos por Categoria',
                hole=.3 # Cria o efeito "Donut"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

            # ----------------------------------
            # Gráfico 2: Evolução Mensal (Barras)
            # ----------------------------------
            st.subheader("Evolução Mensal das Despesas")
            
            df_despesas['mes_ano'] = df_despesas['Data'].dt.to_period('M').astype(str)
            
            despesas_mensais = df_despesas.groupby('mes_ano')['Valor'].sum().abs().reset_index()
            
            fig_barras = px.bar(
                despesas_mensais,
                x='mes_ano',
                y='Valor',
                title='Gastos Totais por Mês',
                labels={'mes_ano': 'Mês/Ano', 'Valor': 'Despesa Total (R$)'}
            )
            st.plotly_chart(fig_barras, use_container_width=True)

            st.markdown("---")
            st.subheader("Tabela de Transações Categorizadas")
            st.dataframe(df_final.sort_values(by='data', ascending=False), use_container_width=True)

# ----------------------------------------------------
# Instrução para Execução
# ----------------------------------------------------
st.sidebar.markdown(
    """
    **Instruções para Rodar:**
    1. Salve o código como `app_streamlit.py`.
    2. Instale as bibliotecas: `pip install streamlit pandas plotly`.
    3. Execute no terminal: `streamlit run app_streamlit.py`.
    """
)