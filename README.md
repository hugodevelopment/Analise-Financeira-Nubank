# Analise-Financeira-Nubank

# 📊 Projeto Nubank - Pipeline de Dados e Dashboard

Este projeto tem como objetivo **automatizar o processo de extração, transformação e análise de dados financeiros** a partir de faturas do Nubank, consolidando tudo em uma base única e gerando insights relevantes sobre os gastos. Como pico de gastos por semana, categorias com mais gastos etc. Deste modo posso rastrear meus gastos e otimizar meu controle financeiro.

---

## 🚀 Funcionalidades

- **ETL completo**:
  - Extração de dados de faturas em CSV.
  - Transformação e padronização (tratamento de datas, acréscimo automático de ano, criação de colunas inteligentes).
  - Carga em arquivos consolidados (`extratos_nubank_final_por_fatura.csv`).

- **Análises implementadas**:
  - Evolução mensal dos gastos.
  - Variação percentual mês a mês.
  - Concentração de gastos por estabelecimento/categoria.
  - Ticket médio por transação.
  - Análise semanal de consumo.

- **Visualização**:
  - Dashboard interativo no **Power BI**.
  - Protótipo de dashboard em **Streamlit** para visualização web.

---

## 🛠️ Tecnologias Utilizadas

- **Python** (Pandas, NumPy, Streamlit)
- **Power BI** para visualização
- **CSV/Excel** para armazenamento intermediário
- **GitHub** para versionamento e documentação

---

## 📂 Estrutura do Repositório

- `Pipeline_Nubank.py` → Script principal de ETL.
- `analise-semana.py` / `analise-semanal-nubank.py` → Scripts de análise semanal.
- `dash_finance.py` → Protótipo de dashboard em Streamlit.
- `Dashboard - Nubank.pbix` → Dashboard interativo no Power BI.
- `extratos_nubank_final_por_fatura.csv` → Base consolidada final.
- `README.md` → Documentação do projeto.

---

## 📈 Exemplos de Insights

- **Evolução mensal**: identificar aumento ou redução dos gastos em cada ciclo.
- **Concentração de gastos**: descobrir os 5 estabelecimentos que mais impactam no orçamento.
- **Ticket médio**: entender o valor médio das transações.
- **Picos semanais**: detectar quais semanas concentram maior volume de gastos.
