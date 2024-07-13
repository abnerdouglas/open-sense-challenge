''' 
SOLUÇÃO DO CÓDIGO

Optei por utilizar a biblioteca BeautifulSoup para realizar a leitura dos dados dos arquivos html, de forma que
a biblioteca transforma os dados em objetos passíveis de serem navegáveis, como por exemplo: soup.find_all("tr")
para encontrar algo específico no documento dentro da tag <tr/>. Coloquei também comentários ao longo da resolução
do código para ficar mais didático o entendimento. Além da biblioteca BeautifulSoup, utilizei o módulo os para 
interagir com o sistema operacional através de funções, e o módulo re para busca de padrões nos arquivos html.

OBS: O arquivo 00028986000108-01.html, o qual eu defini como ARQUIVO10 no arquivo PATENTES.html de saída, possui 3 páginas 
para visualização dos 41 processos, no entanto, o arquivo fornecido permite acesso apenas a página 1. Portanto, não consegui
obter os dados dos 41 processos deste arquivo, apenas de 20 processos que estavam visíveis para manipulação no arquivo 
mencionado e na página 1.

'''

import os
from bs4 import BeautifulSoup
import re

# Diretório onde estão os arquivos html de patentes fornecido pela empresa via email
diretorio_patentes = "./PATENTES"

# Lista para armazenar os dados extraídos das patentes
dados_patentes = []

# Loop para acessar cada arquivo na pasta de patentes e definir o nome de cada arquivo juntamente com um índice
for indice, nome_arquivo in enumerate(sorted(os.listdir(diretorio_patentes))):
    if nome_arquivo.endswith(".html"):
        caminho_arquivo = os.path.join(diretorio_patentes, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='cp1252') as arquivo:
            conteudo_html = arquivo.read()
        
        # Transformação do conteúdo html para um objeto BeautifulSoup
        soup = BeautifulSoup(conteudo_html, 'html.parser')

        # Extrai o nome do arquivo e adiciona um índice incremental (usando o formato ARQUIVO1, ARQUIVO2, ...)
        nome_arquivo_formatado = f"ARQUIVO{indice+1}"

        # Busca por CNPJ do depositante através de um padrão de string presente nos arquivos
        cnpj_depositante = ""
        tag_cnpj = soup.find(string=re.compile(r'CPF ou CNPJ do Depositante: \'(\d{14})\''))
        if tag_cnpj:
            cnpj_depositante = re.search(r'CPF ou CNPJ do Depositante: \'(\d{14})\'', tag_cnpj).group(1)

        # Busca pelo número de resultados de patentes encontrados com base no id da div, e extrai o número de dentro da tag b -> <b>?<b/>
        numero_resultados = "0"
        div_resultados = soup.find("div", {"id": "tituloEResumoContextGlobal"})
        if div_resultados:
            tag_numero_resultados = div_resultados.find("b")
            if tag_numero_resultados:
                numero_resultados = tag_numero_resultados.text.strip()

        # Inicializa a lista de detalhes dos resultados das patentes(NÚMERO DO PEDIDO, DATA DO DEPÓSITO, TÍTULO E IPC)
        detalhes_resultados = []

        # Se houver resultados, extrai cada detalhe encontrado
        if numero_resultados != "0":
            # Busca todos os elementos 'tr' dentro do soup
            linhas_resultados = soup.find_all("tr")
            
            # Aqui é realizado a captação dos detalhes dos resultados de forma sequencial
            for linha in linhas_resultados:
                # Verifica se a linha contém as informações que queremos de acordo com a tag <a/> e o class='visitado'
                if linha.find("a", class_="visitado"):
                    # Número do pedido da patente
                    numero_pedido = linha.find("a", class_="visitado").text.strip()

                    # Data do depósito da patente com base no alinhamento da div=center
                    tag_data_deposito = linha.find_next("td", align="center").find_next("td", align="center")
                    data_deposito = tag_data_deposito.text.strip() if tag_data_deposito and tag_data_deposito.text.strip() not in ['', '-'] else "0"

                    # Título da patente com base no alinhamento da div=left e realização de uma formatação em um dos títulos
                    tag_titulo = linha.find_next("td", align="left")
                    titulo_patente = tag_titulo.get_text(strip=True).replace("CONFIGURAï¿½ï¿½O", "CONFIGURAÇÃO") if tag_titulo else '-'
                    titulo_patente = titulo_patente if titulo_patente not in ['', '-'] else "-"

                    # IPC com base na tag <font/> e no class=alerta
                    tag_ipc = linha.find_next("font", class_="alerta")
                    ipc_patente = tag_ipc.text.strip()

                    detalhes_resultados.append({
                        "numero_pedido": numero_pedido,
                        "data_deposito": data_deposito,
                        "titulo_patente": titulo_patente,
                        "ipc_patente": ipc_patente
                    })
        else:
            # Adiciona uma entrada vazia('-') se não houver detalhes dos resultados presentes nos arquivos
            detalhes_resultados.append({
                "numero_pedido": "-",
                "data_deposito": "-",
                "titulo_patente": "-",
                "ipc_patente": "-"
            })

        # Armazena os dados coletados em uma única entrada para cada arquivo de patente
        dados_patentes.append({
            "nome_arquivo": nome_arquivo_formatado,
            "cnpj_depositante": cnpj_depositante,
            "numero_resultados": numero_resultados,
            "detalhes_resultados": detalhes_resultados
        })

# Esqueleto html para construção da tabela e um css simples para definição das linhas e colunas
html_output = """
<html>
<head>
    <title>Relatório de Patentes</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Relatório de Patentes</h1>
    <table>
        <tr>
            <th>Arquivo</th>
            <th>CNPJ</th>
            <th>Número de Resultados</th>
            <th>Número do Pedido</th>
            <th>Data do Depósito</th>
            <th>Título da Patente</th>
            <th>IPC</th>
        </tr>
"""

# Preenche a tabela com os dados coletados dos arquivos sobre as patentes
for dados_patente in dados_patentes:
    for detalhe_resultado in dados_patente['detalhes_resultados']:
        html_output += f"""
        <tr>
            <td>{dados_patente['nome_arquivo']}</td>
            <td>{dados_patente['cnpj_depositante']}</td>
            <td>{dados_patente['numero_resultados']}</td>
            <td>{detalhe_resultado['numero_pedido']}</td>
            <td>{detalhe_resultado['data_deposito']}</td>
            <td>{detalhe_resultado['titulo_patente']}</td>
            <td>{detalhe_resultado['ipc_patente']}</td>
        </tr>
        """

# Fecha a tabela e o arquivo html
html_output += """
    </table>
</body>
</html>
"""

# Escreve todo o conteúdo html em um arquivo de saída chamado PATENTES.HTML
with open("PATENTES.HTML", "w", encoding="utf-8") as arquivo_html:
    arquivo_html.write(html_output)

print("Arquivo HTML gerado com sucesso: PATENTES.HTML")