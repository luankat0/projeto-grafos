from pyvis.network import Network
from pathlib import Path
import csv
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

base_path = Path(__file__).parent.parent.parent
output_html = base_path / 'out' / 'grafo_bairros.html'
output_html.parent.mkdir(parents=True, exist_ok=True)

net.write_html(str(output_html))

print("Grafo criado com sucesso: 'out/grafo_bairros.html'")


def gerar_csv_bairros_microrregiao():
    base_path = Path(__file__).parent.parent.parent
    input_csv = base_path / 'data' / 'bairros_recife.csv'
    output_csv = base_path / 'data' / 'bairros_unique.csv'
    
    bairros_data = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        for row in reader:
            for i, bairro in enumerate(row):
                if bairro.strip():
                    microrregiao = headers[i] if i < len(headers) else ''
                    bairros_data.append({
                        'bairro': bairro.strip(),
                        'microrregiao': microrregiao.strip()
                    })
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['bairro', 'microrregiao'])
        writer.writeheader()
        writer.writerows(bairros_data)
    
    print(f"CSV de bairros e microrregiões criado: {output_csv}")


gerar_csv_bairros_microrregiao()
