import csv
import json
from pathlib import Path
import re

def carregas_grafos_pesos(csv_path):
    grafo = {}
    vertices = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for linha in reader:
            origem = linha['bairro_origem'].strip()
            destino = linha['bairro_destino'].strip()
            peso = int(linha['peso'].strip())
            
            vertices.add(origem)
            vertices.add(destino)
            
            if origem not in grafo:
                grafo[origem] = {}
            if destino not in grafo:
                grafo[destino] = {}
            
            grafo[origem][destino] = peso
            grafo[destino][origem] = peso
    
    return grafo, vertices


def dijkstra(grafo, origem, destino):
    distancias = {bairro: float('inf') for bairro in grafo}
    distancias[origem] = 0
    visitados = set()
    predecessores = {bairro: None for bairro in grafo}
    
    while len(visitados) < len(grafo):
        menor_distancia = float('inf')
        vertice_atual = None
        
        for bairro in grafo:
            if bairro not in visitados and distancias[bairro] < menor_distancia:
                menor_distancia = distancias[bairro]
                vertice_atual = bairro
        
        if vertice_atual is None:
            break
        
        visitados.add(vertice_atual)
        
        if vertice_atual == destino:
            break
        
        for vizinho, peso in grafo[vertice_atual].items():
            if vizinho not in visitados:
                nova_distancia = distancias[vertice_atual] + peso
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    predecessores[vizinho] = vertice_atual
    
    caminho = []
    if distancias[destino] != float('inf'):
        atual = destino
        while atual is not None:
            caminho.insert(0, atual)
            atual = predecessores[atual]
    
    return distancias[destino], caminho


def main():
    base_path = Path(__file__).parent.parent.parent
    input_path = base_path / "data" / "adjacencias_bairros.csv"
    output_path = base_path / "out" / "distancia_enderecos.csv"
    pares_especificos = [
        ("Nova Descoberta", "Boa Viagem(Setubal)"),
        ("Dois Irmaos", "Casa Amarela"),
        ("Jaqueira", "Derby"),
        ("Boa Viagem", "Brasilia Teimosa"),
        ("Macaxeira", "Passarinho")
    ]

    enderecos = [
        ("R. Dr. Alto Caeté 222", "Av. Visc. de Jequitinhonha 455"),
        ("R. Dois Irmãos 1113 R.", "Padre Lemos 94"),
        ("Rua Hoel Sette 144", "Av. Gov. Agamenon Magalhães 2132"),
        ("R. Marquês de Valença 50", "R. Badejo 32"),
        ("Av. José Américo de Almeida 811", "Estrada do Passarinho 2198")
    ]

    grafo, vertices = carregas_grafos_pesos(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resultados = []
    distancias = {}

    for (bairro_x, bairro_y), (addr_x, addr_y) in zip(pares_especificos, enderecos):
        if bairro_x not in grafo or bairro_y not in grafo:
            print(f"Um dos bairros não está no grafo: {bairro_x}, {bairro_y}")
            continue

        custo, caminho = dijkstra(grafo, bairro_x, bairro_y)
        caminho_str = " -> ".join(caminho) if caminho else "Sem caminho"

        resultados.append({
            'X': addr_x,
            'Y': addr_y,
            'bairro_X': bairro_x,
            'bairro_Y': bairro_y,
            'custo': custo if custo != float('inf') else 'Infinito',
            'caminho': caminho_str
        })

        chave = f"{bairro_x}-{bairro_y}"
        distancias[chave] = {'caminho': caminho}
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['X', 'Y', 'bairro_X', 'bairro_Y', 'custo', 'caminho'])
        writer.writeheader()
        writer.writerows(resultados)

    def safe_arquivo(s: str) -> str:
        s = s.strip()
        s = s.replace(' ', '_')
        s = re.sub(r"[^A-Za-z0-9_\-]", '', s)
        return s

    for r in resultados:
        bx = r['bairro_X']
        by = r['bairro_Y']
        arquivo = f"distancia_{safe_arquivo(bx)}__{safe_arquivo(by)}.json"
        arquivo_path = output_path.parent / arquivo
        data = {
            'bairro_X': bx,
            'bairro_Y': by,
            'X': r['X'],
            'Y': r['Y'],
            'custo': r['custo'],
            'caminho': r['caminho']
        }
        with open(arquivo_path, 'w', encoding='utf-8') as jf:
            json.dump(data, jf, ensure_ascii=False, indent=2)
    
main()
