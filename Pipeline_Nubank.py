import pandas as pd
import os
from pathlib import Path
import numpy as np
import math

# --- CONFIGURAÇÃO ---
# ⚠️ Substitua 'caminho/para/seus/extratos' pelo caminho real da sua pasta
PASTA_EXTRATOS = Path('C:\\Users\\T-Gamer\\Desktop\\dash-finance\\extratos')
ARQUIVO_SAIDA = 'extratos_nubank_consolidado_analise.csv'
COLUNA_DATA_ORIGINAL = 'date' # Coluna que contém a data da transação no seu extrato

def criar_pipeline_nubank_etl(pasta_origem, arquivo_saida, coluna_data):
    """
    Pipeline que extrai, consolida, transforma e carrega os extratos mensais do Nubank.
    """
    
    # Lista para armazenar todos os DataFrames lidos
    lista_dfs = []
    
    print("--- INICIANDO PIPELINE ETL ---")
    
    # =================================================================
    # ETAPA 1: EXTRAÇÃO E CONSOLIDAÇÃO (UNION)
    # =================================================================
    
    print(f"1. Extraindo arquivos de: {pasta_origem.resolve()}")
    
    # Busca por arquivos CSV na pasta
    arquivos_csv = list(pasta_origem.glob('*.csv'))

    if not arquivos_csv:
        print("⚠️ ERRO: Nenhum arquivo CSV encontrado na pasta especificada.")
        return

    for arquivo in arquivos_csv:
        try:
            # Leitura do arquivo CSV. Ajuste o delimitador se necessário (sep=',')
            df = pd.read_csv(arquivo)
            lista_dfs.append(df)
            print(f"   - Arquivo lido: {arquivo.name}")
        except Exception as e:
            print(f"   - Falha ao ler {arquivo.name}: {e}")
            
    # Consolida todos os DataFrames em um único
    df_consolidado = pd.concat(lista_dfs, ignore_index=True)
    print(f"\n2. Consolidação concluída. Total de transações: {len(df_consolidado):,}")
    
    # =================================================================
    # ETAPA 2: TRANSFORMAÇÃO (CRIAÇÃO DE FEATURES)
    # =================================================================
    
    print("3. Iniciando Transformações...")
    
    # 3.1. Garantir que a coluna de data é datetime
    # Fixed code
    # converter datas (valores inválidos viram NaT)
    df_consolidado[coluna_data] = pd.to_datetime(df_consolidado[coluna_data])
    print(f"   - Coluna '{coluna_data}' convertida para datetime (errors='coerce').")

    
        # garantir amount como float e criar string formatada no padrão brasileiro
    df_consolidado['amount'] = df_consolidado['amount'].astype(float)
    df_consolidado['valor_formatado'] = df_consolidado['amount'].map(lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
    print("   - Coluna 'valor_formatado' criada (formato brasileiro R$ X.XXX,XX).")
    
    # ...existing code...- Coluna 'valor_formatado' criada (string).")

    # criar coluna MÊS com abreviações em pt-br via mapeamento (mais robusto que indexação direta)
    meses_dict = {1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
                  7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'}
    df_consolidado['MÊS'] = df_consolidado[coluna_data].dt.month.map(meses_dict)
    print("   - Coluna 'MÊS' criada com abreviações.")

    # 3.3. Criar a coluna SEMANA_DO_MÊS (Lógica: ceil(Dia / 7))
    # Extrai o dia do mês
    dia_do_mes = df_consolidado[coluna_data].dt.day
    
    # Aplica a lógica: ceil(dia / 7)
    df_consolidado['SEMANA_DO_MÊS'] = np.ceil(dia_do_mes / 7).astype('Int64')
    print("   - Coluna 'SEMANA_DO_MÊS' criada com sucesso.")

    # Opcional: Reordenar colunas para melhor visualização
    cols = ['MÊS', 'SEMANA_DO_MÊS', coluna_data] + [col for col in df_consolidado.columns if col not in ['MÊS', 'SEMANA_DO_MÊS', coluna_data]]
    df_consolidado = df_consolidado[cols]

    # =================================================================
    # ETAPA 3: CARREGAMENTO (LOAD)
    # =================================================================
    
    # Salva o DataFrame final em um novo arquivo CSV
    df_consolidado.to_csv(arquivo_saida, index=False, encoding='utf-8')
    
    print(f"\n4. Carregamento concluído! Arquivo final salvo como: {arquivo_saida}")
    print("--- PIPELINE CONCLUÍDO COM SUCESSO ---")
    
    return df_consolidado

# --- EXECUÇÃO DO PIPELINE ---
# Para testar, lembre-se de criar uma pasta de exemplo com alguns arquivos CSV de extrato.
df_final = criar_pipeline_nubank_etl(PASTA_EXTRATOS, ARQUIVO_SAIDA, COLUNA_DATA_ORIGINAL)

# --- Exemplo de Teste da Lógica (Se precisar):
# data_teste = pd.to_datetime(['2024-01-01', '2024-01-07', '2024-01-08', '2024-01-15', '2024-01-29'])
# semana_teste = np.ceil(data_teste.day / 7).astype(int)
# print(f"\nTeste da Lógica (dias 1, 7, 8, 15, 29): {semana_teste.tolist()}") 
# Esperado: [1, 1, 2, 3, 5]