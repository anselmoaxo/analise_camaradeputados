
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
from PIL import Image
from io import BytesIO





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


df = ObterDeputados()
st.set_page_config(
        page_title="DADOS ABERTOS - DEPUTADOS",
        page_icon="chart_with_upwards_trend",
        layout="wide",
    )

partidos = df['partido'].value_counts().index
partido = st.sidebar.selectbox('Selecione o Partido ', partidos)


df_deputados = df[df['partido'] == partido]
nome_deputados = df_deputados['nome'].value_counts().index
nome = st.sidebar.selectbox('Deputados', nome_deputados)
quantidade_deputados = len(nome_deputados)
st.header(f'Partido {partido} tem o total de {quantidade_deputados} Deputados')
conteudo = df[df['nome'] == nome].iloc[0]


st.divider()

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





id_cadastro = conteudo['ideCadastro']
url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_cadastro}/despesas?ordem=ASC&ordenarPor=ano"
res = requests.get(url)
print(res.content)

# Verificar se a solicitação foi bem-sucedida (código de status 200)
if res.status_code == 200:
    # Analisar o XML
    root = ET.fromstring(res.content)

    # Iterar sobre os elementos "registroCotas"
    for registro_cotas in root.findall(".//registroCotas"):
        ano = registro_cotas.find("ano").text
        mes = registro_cotas.find("mes").text
        tipo_despesa = registro_cotas.find("tipoDespesa").text
        valor_documento = registro_cotas.find("valorDocumento").text
        url_documento = registro_cotas.find("urlDocumento").text

        # Exibir informações
        st.write(f"Ano: {ano}, Mês: {mes}, Tipo de Despesa: {tipo_despesa}, Valor do Documento: {valor_documento}, URL do Documento: {url_documento}")
else:
    print(f"A solicitação falhou com o código de status: {res.status_code}")
pdf_url = "https://www.camara.leg.br/cota-parlamentar/documentos/publ/3605/2024/7677248.pdf"

# Aplicativo Streamlit
st.title('Link de Download para PDF')

# Adicionar link de download
st.markdown(f'[Clique aqui para baixar o PDF]({pdf_url})', unsafe_allow_html=True)
#st.write(f' Para mais infomrações acesse: {url}')