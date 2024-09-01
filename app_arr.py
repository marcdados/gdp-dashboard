import streamlit as st
import pandas as pd
import plotly.express as px
import os


#   streamlit run app_arr.py
#------------- CRIANDO A BASE DE DADOS E IMPLEMENTANDO A VISAO NO STREAMLIT -----------------------------

caminho_pasta = r'C:\Users\kling\OneDrive - GRUPO EQUATORIAL ENERGIA\Marclinge\Monitoramento_Arquivos\Dataset\Processado'

st.set_page_config(layout='centered')

# -------------- criando o data frame base ---------------------------------------------------------------

dataframes = []

for arquivo in os.listdir(caminho_pasta):
    if arquivo.endswith('.xls') or arquivo.endswith('.xlsx'):
        caminho_arquivo = os.path.join(caminho_pasta, arquivo)
        df = pd.read_excel(caminho_arquivo)

        df['Nome_Arquivo'] = arquivo
        df['status'] = caminho_pasta
        df['status'] = df['status'].str.rsplit('\\', n=1).str[1]
        df = df[df['Filename'].str.endswith('RET')]
        df['capa'] = df['Filename'].str[:4]
        df['Cod. banco'] = df['capa'].str[:3]
        df['Modalidade'] = df['capa'].str[-1:]
        df['Empresa'] = df['Nome_Arquivo'].str.rsplit('_', n=1).str[1]
        df['Empresa'] = df['Empresa'].str.split('.', n=0).str[0]
        df['Data'] = pd.to_datetime(df['Data da última modificação'])
       
        dataframes.append(df)

df = pd.concat(dataframes, ignore_index=True)
colunas_selecionadas = [
    'Empresa',
    'Data',
    'Filename',
    'Cod. banco',
    'Modalidade',
    'status'
]

df = df[colunas_selecionadas]

def highlight_processed(val):
    color = 'background-color: #c6efce;' if val == "Processado" else ''
    return color

# ------------ criando seletores -------------------------------------

SEL_DATA = st.sidebar.selectbox("Data",df['Data'].unique())
SEL_EMPRESA = st.sidebar.selectbox("Empresa",df['Empresa'].unique())

# ------------ criando filtros dinamico no data frame base com os seletores -------------------------------------

df = df[(df['Data'] == SEL_DATA) & (df['Empresa'] == SEL_EMPRESA)]

# ------------ criando data frames especificos das modaldiades com base no data frame base (já com os filtros dinamicos) ---

df_boleto = df.loc[df['Modalidade']=='B', ['Cod. banco','status']].drop_duplicates().style.applymap(highlight_processed,subset = ["status"])
df_codbar = df.loc[df['Modalidade']=='C', ['Cod. banco','status']].drop_duplicates().style.applymap(highlight_processed,subset = ["status"])
df_debaut = df.loc[df['Modalidade']=='D', ['Cod. banco','status']].drop_duplicates().style.applymap(highlight_processed,subset = ["status"])


# ---------------- criano um grafico para total de arquivos por status -------


# ---------------- Listando os valores de 'status' para usar no eixo do grafico

all_status = ['Processado', 'Em fila', 'Erro']

# ---------------- criando uma contagem de ocorrencias por status -----------------

status_counts = df['status'].value_counts().reindex(all_status, fill_value=0).reset_index()
status_counts.columns = ['status', 'quantidade']
status_counts_processado = status_counts[status_counts["status"]=='Processado']
status_counts_processado.columns = ['status', 'quantidade']
# Calcular os percentuais
status_counts['percent'] = (status_counts['quantidade'] / status_counts['quantidade'].sum()) * 100
# Calcular os percentuais_processados
status_counts_processado['percent'] = (status_counts_processado['quantidade'] / status_counts_processado['quantidade'].sum()) * 100

# ----------------- Criando os graficos -----------------------------------
fig1 = px.bar(status_counts, x='status', y='quantidade',title=" Quantidade por status", text='quantidade') # grafico de colunas
fig1.update_traces(width=0.4, textposition='outside')

fig2 = px.pie(status_counts, names='status', values='quantidade', title='Avanço do processamento', hole=0.7,  hover_data=['percent']) # grafico de rosca
fig2.update_traces(textinfo='none')

# Adicionando  o valor total no centro do grafico de rosca
total_count = status_counts_processado['percent'].sum()
fig2.add_annotation(text=f"{total_count}%",
                    x=0.5, y=0.5, showarrow=False,
                    font_size=30, font_color="black",
                    xanchor='center', yanchor='middle')

# ------------------ criando metricas para exibir tipo cartao -------------------

total_recebido =   df[df["status"] == 'Recebido'].shape[0]
total_processado = df[df["status"] == 'Processado'].shape[0]
total_erro =       df[df["status"] == 'Erro'].shape[0]
total = total_recebido + total_processado + total_erro


# ---------------- montando  layout no streamlit -----------------------------


st.title("Monitoramento de arquivos")

col1, col2 = st.columns(2)

with col1:

    st.subheader(f"**EQUATORIAL {SEL_EMPRESA}**")
    st.subheader(f"Arquivos recebidos: {total}")
with col2:
    st.image(f"mapa_{SEL_EMPRESA}.svg",width=100)

col1, col2 = st.columns(2)

with col1:
 
    #st.image('mapa_maranhao.svg', use_column_width=False)
    #col1, col2, col3 = st.columns(3)
    # with col1:
    #    st.metric(label="Processados", value=total_processado)
    # with col2:
    #    st.metric(label="Em Fila", value=total_recebido)
    # with col3:
    #    st.metric(label="Erro", value=total_erro)

     fig2
with col2:
    fig1
   

col1, col2, col3 = st.columns(3)

with col1:
    
    st.write("**BOLETO**")
    st.dataframe(df_boleto, hide_index=True )
with col2:
    st.write("**COD. BARRAS**")
    st.dataframe(df_codbar, hide_index=True)
with col3:
    st.write("**DEB. AUTOMÁTICO**   ")
    st.dataframe(df_debaut, hide_index=True)

st.dataframe (df, hide_index=True)