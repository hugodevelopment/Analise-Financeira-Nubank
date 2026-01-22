import pandas as pd
import locale

# Configuração para formatar valores monetários em BRL (Brasil)
# 'pt_BR.UTF-8' é um locale comum para sistemas Linux/macOS. Pode ser diferente no Windows.
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        # Tenta um locale comum no Windows
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        print("Aviso: Não foi possível configurar o locale para BRL. Usando formatação simples.")
        # Define uma função de formatação simples como fallback
        def format_currency(value):
            return f"R$ {value:,.2f}".replace(",", "_TEMP_").replace(".", ",").replace("_TEMP_", ".")
        locale_ativo = False
    else:
        locale_ativo = True
else:
    locale_ativo = True

# Função de formatação que usa o locale, ou o fallback simples
if locale_ativo:
    def format_currency(value):
        return locale.currency(value, grouping=True, symbol=True)
else:
    # A função format_currency já está definida no bloco 'except' acima
    pass


# Carregando o arquivo consolidado
try:
    df = pd.read_csv("extratos_nubank_consolidado_analise.csv")
except FileNotFoundError:
    print("ERRO: O arquivo 'extratos_nubank_consolidado_analise.csv' não foi encontrado.")
    # Adicionar código para carregar o arquivo real se for o caso
    raise

# Convertendo a coluna 'amount' (valor) para numérica
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
# Filtrando valores nulos e estornos/pagamentos de fatura para análise de gasto puro
# Consideramos apenas gastos (valores positivos)
df_gastos = df[df['title'] != 'Pagamento recebido']

print(df_gastos)

print("=" * 70)
print("ANÁLISE DE PADRÕES DE GASTO POR SEMANA DO MÊS")
print(f"Base de dados analisada: {len(df_gastos)} transações (após remover estornos/nulos)")
print("=" * 70)

# 1. Agregação principal por SEMANA_DO_MÊS
analise_semana = df_gastos.groupby('SEMANA_DO_MÊS')['amount'].agg(
    Gasto_Total='sum',
    Num_Transacoes='count',
    Gasto_Medio_Transacao='mean'
).reset_index()

# 2. Adicionar o Gasto Médio Semanal e a representatividade
# Calcula o número de meses únicos na base (para normalizar)
num_meses = df_gastos['MÊS'].nunique()

analise_semana['Gasto_Medio_Semanal'] = analise_semana['Gasto_Total'] / num_meses
analise_semana['%_Gasto_Total'] = (analise_semana['Gasto_Total'] / analise_semana['Gasto_Total'].sum()) * 100

# 3. Formatação
analise_semana['Gasto_Total'] = analise_semana['Gasto_Total'].apply(format_currency)
analise_semana['Gasto_Medio_Semanal'] = analise_semana['Gasto_Medio_Semanal'].apply(format_currency)
analise_semana['Gasto_Medio_Transacao'] = analise_semana['Gasto_Medio_Transacao'].apply(format_currency)
analise_semana['%_Gasto_Total'] = analise_semana['%_Gasto_Total'].map('{:.1f}%'.format)


# Renomeando as semanas para um formato mais legível
mapeamento_semana = {
    1: 'Semana 1 (Dias 1-7)',
    2: 'Semana 2 (Dias 8-14)',
    3: 'Semana 3 (Dias 15-21)',
    4: 'Semana 4 (Dias 22-28)',
    5: 'Semana 5 (Dias 29+)'
}
analise_semana['Semana_Periodo'] = analise_semana['SEMANA_DO_MÊS'].map(mapeamento_semana)

# Ordenando e Selecionando Colunas Finais
analise_final = analise_semana[['Semana_Periodo', 'Gasto_Total', '%_Gasto_Total', 'Gasto_Medio_Transacao', 'Num_Transacoes']]

print("\nPADRÕES DE GASTO CONSOLIDADOS POR SEMANA DO MÊS:\n")
#print(analise_final.to_markdown(index=False))

print("\n--- INSIGHTS DE NEGÓCIO ---\n")

# Extraindo insights (Qual semana tem o maior gasto?)
# Refazendo o cálculo sem formatação para encontrar o máximo
gasto_por_semana_sem_formatar = df_gastos.groupby('SEMANA_DO_MÊS')['amount'].sum()
semana_de_pico = gasto_por_semana_sem_formatar.idxmax()

print(semana_de_pico)

valor_pico = format_currency(gasto_por_semana_sem_formatar.max())
perc_pico = (gasto_por_semana_sem_formatar.max() / df_gastos['amount'].sum()) * 100

print(f"1. Semana de PICO: A {mapeamento_semana[semana_de_pico]} concentra o maior gasto, totalizando {valor_pico} ({perc_pico:.1f}% do total).")

# Extraindo insights (Qual semana tem mais transações?)
transacoes_por_semana = df_gastos.groupby('SEMANA_DO_MÊS')['amount'].count()
semana_mais_ativa = transacoes_por_semana.idxmax()
num_transacoes_pico = transacoes_por_semana.max()

print(f"2. Frequência de Uso: A {mapeamento_semana[semana_mais_ativa]} é a mais ativa, com {num_transacoes_pico} transações registradas.")

# Extraindo insights (Qual semana o gasto médio é maior/menor?)
gasto_medio_por_semana = df_gastos.groupby('SEMANA_DO_MÊS')['amount'].mean()
semana_medio_alto = gasto_medio_por_semana.idxmax()

print(f"3. Ticket Médio: O gasto médio por transação é mais alto na {mapeamento_semana[semana_medio_alto]} ({format_currency(gasto_medio_por_semana.max())}).")