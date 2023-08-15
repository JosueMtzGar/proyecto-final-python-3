import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def obtener_contenido_pagina(url):
    response = requests.get(url)
    return response.content

def analizar_contenido_html(html):
    return BeautifulSoup(html,'html.parser')

data = []

def procesar_pagina(soup):
    titulos = []
    autores = []
    links = []
    fecha_envio = []
    mes_envio = []
    año_envio = []
    categorias = []
    resumen = []

    titulo_item = soup.find_all('p', class_="title is-5 mathjax")

    for items in titulo_item:
        titulo = items.text
        titulo_limpio = titulo.strip()
        titulos.append(titulo_limpio)

    authors_item = soup.find_all('p', class_="authors")

    for item in authors_item:
        lista_autores = item.find_all('a')
        autores_item = []
        for item2 in lista_autores:
            autores_item.append(item2.text)
        autores.append(autores_item)

    link_item = soup.find_all('p', class_="list-title is-inline-block")

    for item in link_item:
        link = item.a
        links.append(link['href'])

    patron_mes = r'\b\s+(\w+)\b'
    patron_año = r' (\d{4})'

    fecha_envio_item = soup.find_all('span', class_="has-text-black-bis has-text-weight-semibold", string="Submitted")

    for item in fecha_envio_item:
        fecha = item.find_next_sibling(string=True)
        fecha_limpia = fecha.replace(';','').strip()
        fecha_envio.append(fecha_limpia)
        
        mes = re.search(patron_mes, fecha_limpia)
        mes_envio.append(mes.group().strip())
        
        año = re.search(patron_año,fecha_limpia)
        año_envio.append(año.group().strip())

    categorias_item = soup.find_all('div', class_="tags is-inline-block")

    for item in categorias_item:
        lista_categorias = item.find_all('span')
        cat_item = []
        for item2 in lista_categorias:
            cat_item.append(str(item2['data-tooltip']))
        categorias.append(cat_item)

    resumen_item = soup.find_all('span', class_="abstract-full has-text-grey-dark mathjax")

    for item in resumen_item:
        resumen_limpio = item.text.replace(' Less','').strip()
        resumen.append(resumen_limpio)

    for i in range(len(titulos)):
        data.append({
            "Titulo": titulos[i],
            "Autores": autores[i],
            "URL": links[i],
            "Fecha_Envío": fecha_envio[i],
            "Mes_Envío": mes_envio[i],
            "Año_Envío": año_envio[i],
            "Categorias": categorias[i],
            "Resumen": resumen[i]
        })

def manejar_paginacion(url_base, num_paginas):
    for i in range(num_paginas + 1):
        texto_nuevo = 'start='+str(i*50)
        url = url_base.replace('start=0',texto_nuevo)
        contenido = obtener_contenido_pagina(url)
        soup = analizar_contenido_html(contenido)
        procesar_pagina(soup)

url_base = 'https://arxiv.org/search/?query=Heavy+Ion+Collision&searchtype=all&source=header&order=-announced_date_first&size=50&abstracts=show&start=0'
num_paginas = 199

manejar_paginacion(url_base, num_paginas) 

dt = pd.DataFrame(data)

print(len(data))

dt.to_csv(f"../datasets/WebScrap_Proyecto.csv", index=False)
