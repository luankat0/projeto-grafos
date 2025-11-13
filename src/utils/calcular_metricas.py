import csv
import json
from pathlib import Path


def normalizar_nome(name):
    letras = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A',
        'É': 'E', 'Ê': 'E',
        'Í': 'I',
        'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U',
        'Ç': 'C'
    }
    result = name
    for velho, novo in letras.items():
        result = result.replace(velho, novo)
    return result.strip()


def calcular_densidade(num_vertices, num_arestas):
    if num_vertices < 2:
        return 0.0
    return (2 * num_arestas) / (num_vertices * (num_vertices - 1))


def carregar_csv(csv_path):

    grafo = {}
    vertices = set()
    arestas = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            origem = normalizar_nome(row['bairro_origem'])
            destino = normalizar_nome(row['bairro_destino'])
            
            vertices.add(origem)
            vertices.add(destino)
            
            if origem not in grafo:
                grafo[origem] = set()
            if destino not in grafo:
                grafo[destino] = set()
            
            grafo[origem].add(destino)
            grafo[destino].add(origem)
            
            aresta = tuple(sorted([origem, destino]))
            arestas.add(aresta)
    
    return grafo, vertices, arestas


def calcular_grafo_completo(vertices, arestas):
    ordem = len(vertices)
    tamanho = len(arestas)
    densidade = calcular_densidade(ordem, tamanho)
    
    return {
        "ordem": ordem,
        "tamanho": tamanho,
        "densidade": round(densidade, 6)
    }


def carregar_microrregiao(csv_path):
    microrregiao = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        for header in headers:
            if header.strip():
                microrregiao[header] = []
        
        for row in reader:
            for i, value in enumerate(row):
                if i < len(headers) and value.strip():
                    nome_regiao = headers[i]
                    bairro = normalizar_nome(value)
                    if nome_regiao in microrregiao:
                        microrregiao[nome_regiao].append(bairro)
    
    return microrregiao


def calcular_microrregiao(vertices, arestas, microrregiao):
    data = {}
    
    for nome_regiao, bairros_regiao in microrregiao.items():

        bairros_set = set(bairros_regiao) & vertices
        arestas_in_regiao = 0

        for aresta in arestas:
            v1, v2 = aresta
            if v1 in bairros_set and v2 in bairros_set:
                arestas_in_regiao += 1
        
        ordem = len(bairros_set)
        tamanho = arestas_in_regiao
        densidade = calcular_densidade(ordem, tamanho)
        
        data[nome_regiao] = {
            "ordem": ordem,
            "tamanho": tamanho,
            "densidade": round(densidade, 6),
            "bairros": sorted(list(bairros_set))
        }
    
    return data


def calcular_ego(grafo, vertices):
    data = {}
    
    for bairro in sorted(vertices):
        vizinhos = grafo.get(bairro, set())
        grau = len(vizinhos)
        
        ego_vertices = {bairro} | vizinhos
        ordem_ego = len(ego_vertices)
        
        tamanho_ego = 0
        for v in ego_vertices:
            for u in grafo.get(v, set()):
                if u in ego_vertices and v < u:
                    tamanho_ego += 1
        
        densidade_ego = calcular_densidade(ordem_ego, tamanho_ego)
        
        data[bairro] = {
            "grau": grau,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": round(densidade_ego, 6),
            "vizinhos": sorted(list(vizinhos))
        }
    
    return data


def main():
    base_path = Path(__file__).parent.parent.parent
    adjacencias_path = base_path / "data" / "adjacencias_bairros.csv"
    bairros_path = base_path / "data" / "bairros_recife.csv"
    
    recife_global_path = base_path / "out" / "recife_global.json"
    microrregioes_path = base_path / "out" / "microrregioes.json"
    ego_bairro_path = base_path / "out" / "ego_bairro.csv"

    grafo, vertices, arestas = carregar_csv(adjacencias_path)
    dados_recife = calcular_grafo_completo(vertices, arestas)
    microrregiao = carregar_microrregiao(bairros_path)
    dados_microrregiao = calcular_microrregiao(vertices, arestas, microrregiao)
    dados_ego = calcular_ego(grafo, vertices)
    
    with open(recife_global_path, 'w', encoding='utf-8') as f:
        json.dump(dados_recife, f, ensure_ascii=False, indent=2)
    
    with open(microrregioes_path, 'w', encoding='utf-8') as f:
        json.dump(dados_microrregiao, f, ensure_ascii=False, indent=2)
    
    with open(ego_bairro_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['bairro', 'grau', 'ordem_ego', 'tamanho_ego', 'densidade_ego'])
        for bairro in sorted(dados_ego.keys()):
            metrics = dados_ego[bairro]
            writer.writerow([
                bairro,
                metrics['grau'],
                metrics['ordem_ego'],
                metrics['tamanho_ego'],
                metrics['densidade_ego']
            ])

main()
