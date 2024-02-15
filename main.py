
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
from PIL import Image
from io import BytesIO


def ObterSiglaPartido(partido):
    url = f'https://www.camara.leg.br/internet/Deputado/img/partidos/{partido}.gif'
    # Faz a requisição
    return url

    

def ObterDeputados():
    url = 'https://www.camara.leg.br/SitCamaraWS/Deputados.asmx/ObterDeputados'
    # Faz a requisição
    res = requests.get(url)

    # Verifica se a requisição foi bem-sucedida (código de status 200)
    if res.status_code == 200:
        # Converte o conteúdo XML em uma estrutura de árvore
        root = ET.fromstring(res.text)

        # Extrai os dados relevantes do XML
        deputados = []
        for deputado_elem in root.findall('.//deputado'):
            deputado = {}
            for child_elem in deputado_elem:
                deputado[child_elem.tag] = child_elem.text
            deputados.append(deputado)

        # Converte os dados em um DataFrame
        df = pd.DataFrame(deputados)
        return df

    # Exibe o DataFrame

    else:
        print(f"Falha na requisição. Código de status: {res.status_code}")


def redimensionar_imagem(url, novo_tamanho=(100, 75)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        imagem = Image.open(BytesIO(response.content))
        imagem_redimensionada = imagem.resize(novo_tamanho)
        return imagem_redimensionada
    except Exception as e:
        st.error(f"Erro ao carregar a imagem: {e}")
        return None


def ObterDetalhesDeputados(id):
    url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/despesas?ordem=ASC&ordenarPor=ano"

# Faz a requisição para a API
    resposta = requests.get(url, headers={"Accept": "application/xml, application/json"})

    # Verifica se a requisição foi bem-sucedida (código de status 200)
    if resposta.status_code == 200:
        # Parse do conteúdo XML
        if "application/xml" in resposta.headers["Content-Type"]:
            root = ET.fromstring(resposta.content)

        # Lista para armazenar os dados
            dados = []

        # Iterar sobre os elementos 'registroCotas'
            for registro_cotas in root.findall('.//registroCotas'):
                ano = registro_cotas.find('ano').text
                mes = registro_cotas.find('mes').text
                tipo_despesa = registro_cotas.find('tipoDespesa').text
                cod_documento = registro_cotas.find('codDocumento').text
                tipo_documento = registro_cotas.find('tipoDocumento').text
                data_documento = registro_cotas.find('dataDocumento').text
                num_documento = registro_cotas.find('numDocumento').text
                valor_documento = registro_cotas.find('valorDocumento').text
                url_documento = registro_cotas.find('urlDocumento').text
                nome_fornecedor = registro_cotas.find('nomeFornecedor').text
                cnpj_cpf_fornecedor = registro_cotas.find('cnpjCpfFornecedor').text
                valor_liquido = registro_cotas.find('valorLiquido').text
                

                # Adiciona os dados à lista
                dados.append({
                    'Ano': ano,
                    'Mês': mes,
                    'Tipo de Despesa': tipo_despesa,
                    'Código do Documento': cod_documento,
                    'Tipo de Documento': tipo_documento,
                    'Data do Documento': data_documento,
                    'Número do Documento': num_documento,
                    'Valor do Documento': valor_documento,
                    'URL do Documento': url_documento,
                    'Nome do Fornecedor': nome_fornecedor,
                    'CNPJ/CPF do Fornecedor': cnpj_cpf_fornecedor,
                    'Valor Líquido': valor_liquido
                })

        # Cria o DataFrame
            df_despesas = pd.DataFrame(dados)

            # Exibe o DataFrame
            return df_despesas
        elif "application/json" in resposta.headers["Content-Type"]:
        # Parse do conteúdo JSON
            data = resposta.json()
            dados = data['dados']

        # Cria o DataFrame
            df_despesas = pd.DataFrame(dados)

        # Exibe o DataFrame
            return df_despesas

        else:
            print("Formato de resposta não suportado")
            
    
df = ObterDeputados()
st.set_page_config(
        page_title="DADOS ABERTOS - DEPUTADOS",
        page_icon="chart_with_upwards_trend",
        layout="wide",
    )
st.sidebar.image('brasilia.png',use_column_width=True, caption='Congresso Nacional')
st.sidebar.info('DADOS ABERTOS - LEGISLATIVO - DEPUTADOS', icon="ℹ️")
partidos = df['partido'].value_counts().index
partido = st.sidebar.selectbox('Selecione o Partido ', partidos)

ufs = df[df['partido'] == partido]
uf = ufs['uf'].value_counts().index
df_uf = st.sidebar.selectbox('Selecione o Deputado', uf)

df_deputados = df[(df['uf'] == df_uf) & (df['partido'] == partido)]
nome_deputados = df_deputados['nome'].value_counts().index
nome = st.sidebar.selectbox('Selecione o Deputado', nome_deputados)


quantidade_deputados = len(nome_deputados)

st.image('logo.png',use_column_width=False)
st.info('DEPUTADO FEDERAL ',icon="ℹ️")
icone_partido = ObterSiglaPartido(partido)
if icone_partido:
    st.image(icone_partido)
st.header(f'{nome} - PARTIDO {partido}', divider='blue')
conteudo = df[df['nome'] == nome].iloc[0]


col1,col2 = st.columns(2)

imagem_redimensionada = redimensionar_imagem(conteudo['urlFoto'])
col1.image(imagem_redimensionada, caption=f"{conteudo['nomeParlamentar']}")


col1,col2 = st.columns(2)


col1.markdown(f"**Nome do Parlamentar :** {conteudo['nomeParlamentar']}")
col1.markdown(f"**Partido :** {conteudo['partido']}")
col1.markdown(f"**Estado :** {conteudo['uf']}")
col2.markdown(f"**Telefone :** {conteudo['fone']}")
col2.markdown(f"**Email :** {conteudo['email']}")
st.markdown(f"**Numero do Gabinete :** {conteudo['gabinete']} - **Anexo:** {conteudo['anexo']}")
st.divider()
id_cadastro = conteudo['ideCadastro']
detalhe = ObterDetalhesDeputados(id_cadastro)
#Est.table(detalhe)
st.sidebar.divider()
st.sidebar.info('Despesas Deputados',icon="ℹ️")
coluna_selecionada = st.sidebar.selectbox("Selecione o Codigo do Documento ", detalhe['Código do Documento'].value_counts().index)
df_dep = detalhe[detalhe['Código do Documento'] == coluna_selecionada].iloc[0]

st.subheader('Despesas Deputado Federal ', divider='blue')

col1,col2,col3 = st.columns(3)
col1.subheader('Nome Fornecedor ')
col1.markdown(f"**{df_dep['Nome do Fornecedor']}**")
col2.subheader('CNPJ/CPF')
col2.markdown(f"**{df_dep['CNPJ/CPF do Fornecedor']}**")

col1,col2,col3,col4 = st.columns(4)
col1.subheader("Data Ano e Mês")
col1.markdown(f"**Mês:** {df_dep['Mês']} - **Ano :** {df_dep['Ano']}")
col2.subheader("Tipo Doc")
col2.markdown(f"**{df_dep['Tipo de Documento']}**")
col3.subheader("Data Doc ")
col3.markdown(f"**{df_dep['Data do Documento']}**")

st.header("", divider='blue')
col1,col2,col3 = st.columns(3)
col1.metric(label='Valor Documento', value=df_dep['Valor do Documento'])
col2.metric(label='Valor Liquido', value=df_dep['Valor Líquido'])
col3.markdown("**Documento da Despesa**", help='Visualização de Despesas')
col3.link_button("Visualizar Documento", f"{df_dep['URL do Documento']}")


# Exibe a coluna selecionada na barra lateral

#fornecedor = st.sidebar.selectbox('Selecione',detalhe[[coluna_selecionada]])

st.caption('Todos dados  utilizados : :blue[https://dadosabertos.camara.leg.br]')