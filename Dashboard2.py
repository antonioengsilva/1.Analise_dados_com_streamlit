import streamlit as st
import plotly.express as px
import pandas as pd
from io import BytesIO

#Para abrir o resultado no navegador
# Ctrl+J
# C:\Users\antonio.joseli\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\streamlit run C:\Users\antonio.joseli\Desktop\ANTONIO_CODAR\Estudo\Antonio\Dashboard2.py

st.set_page_config(page_title="Antonio Estácio!!!", page_icon="bar_chart", layout="wide")

# Título para a análise Intranet
st.title(" ")

st.title(":bar_chart: Projeto Análise de Dados com Python e Streamlit")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Baixar os arquivos da página
fl = st.file_uploader(":file_folder: Carregue um Arquivo", type=(["csv", "txt", "xlsx", "xls"]), accept_multiple_files=True)

# Definir DataFrame
dfs = []

if fl is not None:
    for file in fl:
        filename = file.name
        st.write(filename)
        if filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file, engine='openpyxl')
        else:
            df = pd.read_csv(file, encoding="ISO-8859-1")
        dfs.append(df)

if dfs:
    df = pd.concat(dfs)

    col1, col2 = st.columns((2))
    df["Data Emissão"] = pd.to_datetime(df["Data Emissão"])

    # Obter a data mínima e máxima
    startDate = pd.to_datetime(df["Data Emissão"]).min()
    endDate = pd.to_datetime(df["Data Emissão"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Data Início", startDate, format="DD/MM/YYYY"))

    with col2:
        date2 = pd.to_datetime(st.date_input("Data Final", endDate, format="DD/MM/YYYY"))

    df = df[(df["Data Emissão"] >= date1) & (df["Data Emissão"] <= date2)].copy()

    # Filtro por Fornecedor
    st.sidebar.header("Escolha seu filtro: ")
    Fornecedor = st.sidebar.multiselect("Escolha o Fornecedor", df["Fornecedor"].unique())
    if not Fornecedor:
        df2 = df.copy()
    else:
        df2 = df[df["Fornecedor"].isin(Fornecedor)]

    # Filtro por Unidade
    Unidade2 = st.sidebar.multiselect("Escolha a Unidade", df2["Unidade2"].unique())
    if not Unidade2:
        df3 = df2.copy()
    else:
        df3 = df2[df2["Unidade2"].isin(Unidade2)]

    # Filtre os dados com base em Fornecedor e Unidade

    # Tratamento para combinação
    if not Fornecedor and not Unidade2:
        filtered_df = df3
    elif not Unidade2:
        filtered_df = df3[df3["Fornecedor"].isin(Fornecedor)]
    elif not Fornecedor:
        filtered_df = df3[df3["Unidade2"].isin(Unidade2)]
    else:
        filtered_df = df3[df3["Fornecedor"].isin(Fornecedor) & df3["Unidade2"].isin(Unidade2)]

    # Agrupe os dados por "Fornecedor" e calcule a soma de "Valor Total NF2" e a contagem de "Nr Nota"
    category_df = filtered_df.groupby(by=["Fornecedor"], as_index=False).agg({"Valor Total NF2": "sum", "Nr Nota": "count"})

    # Renomeie as colunas
    category_df = category_df.rename(columns={"Valor Total NF2": "Valor Total NF2", "Nr Nota": "Nr Nota"})

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Faturamento por Empresa")
        fig = px.bar(category_df, x="Fornecedor", y="Valor Total NF2", text=['R${:,.2f}'.format(x) for x in category_df["Valor Total NF2"]],
                    template="seaborn")
        fig.update_yaxes(title_text='')
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        st.subheader("Faturamento por Empresa em %")
        fig = px.pie(filtered_df, values="Valor Total NF2", names="Fornecedor", hole=0.5)
        # Define o que será exibido na fatia (value+percent)
        #fig.update_traces(textinfo="value+percent")
        #fig.update_traces(textinfo="percent") #somente %
        st.plotly_chart(fig, use_container_width=True)



    # Filtrando fornecedor, valor e quantidade de NF 
    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander("Visualizar Pagamentos por Fornecedores"):
            st.dataframe(category_df, use_container_width=True)
            xls_data = BytesIO()
            with pd.ExcelWriter(xls_data, engine="openpyxl", mode="xlsx") as writer:
                category_df.to_excel(writer, index=False)
            st.download_button("Baixar Dados (XLS)", data=xls_data, file_name="Fornecedor.xlsx", key="fornecedor_xls",
                            help="Clique aqui para baixar os dados como um arquivo em XLSX")


    with cl2:
        with st.expander("Visualizar Pagamentos por Unidade"):
            Unidade2 = filtered_df.groupby(by="Unidade2", as_index=False).agg({"Valor Total NF2": "sum", "Nr Nota": "count"})
            st.dataframe(Unidade2, use_container_width=True)  # Corrigido para exibir o DataFrame correto
            xls_data = BytesIO()
            with pd.ExcelWriter(xls_data, engine="openpyxl", mode="xlsx") as writer:
                Unidade2.to_excel(writer, index=False)
            st.download_button("Baixar Dados (XLS)", data=xls_data, file_name="Unidade.xlsx", key="unidade_xls",
                            help="Clique aqui para baixar os dados como um arquivo em XLSX")








    