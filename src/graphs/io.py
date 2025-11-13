from pyvis.network import Network
import os

bairros = [
    "Aflitos", "Afogados", "Agua Fria", "Alto Jose Bonifacio", "Alto Jose do Pinho",
    "Alto Santa Teresinha", "Alto do Mandu", "Apipucos", "Areias", "Arruda",
    "Barro", "Beberibe", "Boa Viagem", "Boa Vista", "Bomba do Hemeterio",
    "Bongi", "Brasilia Teimosa", "Brejo da Guabiraba", "Brejo de Beberibe",
    "Cabanga", "Cacote", "Cajueiro", "Campina do Barreto", "Campo Grande",
    "Casa Amarela", "Casa Forte", "Caxanga", "Cidade Universitaria", "Coelhos",
    "Cohab", "Coqueiral", "Cordeiro", "Corrego do Jenipapo", "Curado", "Derby",
    "Dois Irmaos", "Dois Unidos", "Encruzilhada", "Engenho do Meio", "Espinheiro",
    "Estancia", "Fundao", "Gracas", "Guabiraba", "Hipodromo", "Ibura",
    "Ilha Joana Bezerra", "Ilha do Leite", "Ilha do Retiro", "Imbiribeira",
    "Ipsep", "Iputinga", "Jaqueira", "Jardim Sao Paulo", "Jiquia", "Jordao",
    "Linha do Tiro", "Macaxeira", "Madalena", "Mangabeira", "Mangueira",
    "Monteiro", "Morro da Conceicao", "Mustardinha", "Nova Descoberta", "Paissandu",
    "Parnamirim", "Passarinho", "Pau-Ferro", "Peixinhos", "Pina", "Poco",
    "Ponto de Parada", "Porto da Madeira", "Prado", "Recife", "Rosarinho",
    "San Martin", "Sancho", "Santana", "Santo Amaro", "Santo Antonio", "Sao Jose",
    "Sitio dos Pintos", "Soledade", "Tamarineira", "Tejipio", "Torre", "Torreao",
    "Torroes", "Toto", "Varzea", "Vasco da Gama", "Zumbi"
]

net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

for bairro in bairros:
    net.add_node(bairro, label=bairro)

net.write_html("../../out/grafo_bairros.html")

print("✅ Grafo criado com sucesso! Abra o arquivo 'out/grafo_bairros.html' no navegador.")
