import csv
from pathlib import Path

def carregas_grafos_pesos(csv_path):
    graph = {}
    vertices = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for linha in reader:
            origem = linha['bairro_origem'].strip()
            destino = linha['bairro_destino'].strip()
            peso = int(linha['peso'].strip())
            
            vertices.add(origem)
            vertices.add(destino)
            
            if origem not in graph:
                graph[origem] = {}
            if destino not in graph:
                graph[destino] = {}
            
            graph[origem][destino] = peso
            graph[destino][origem] = peso
    
    return graph, vertices


def dijkstra(graph, origem, destino):
    distancias = {bairro: float('inf') for bairro in graph}
    distancias[origem] = 0
    visitados = set()
    predecessores = {bairro: None for bairro in graph}
    
    while len(visitados) < len(graph):
        menor_distancia = float('inf')
        vertice_atual = None
        
        for bairro in graph:
            if bairro not in visitados and distancias[bairro] < menor_distancia:
                menor_distancia = distancias[bairro]
                vertice_atual = bairro
        
        if vertice_atual is None:
            break
        
        visitados.add(vertice_atual)
        
        if vertice_atual == destino:
            break
        
        for vizinho, peso in graph[vertice_atual].items():
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
        ("Boa Vista", "Corrego do Jenipapo"),
        ("Dois Irmaos", "Casa Amarela"),
        ("Jaqueira", "Derby"),
        ("Boa Viagem", "Brasilia Teimosa"),
        ("Macaxeira", "Passarinho")
    ]
    
    graph, vertices = carregas_grafos_pesos(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    resultados = []
    
    for i, (bairro_x, bairro_y) in enumerate(pares_especificos, 1):
        
        if bairro_x not in graph:
            continue
        if bairro_y not in graph:
            continue
        
        custo, caminho = dijkstra(graph, bairro_x, bairro_y)
        caminho_str = " -> ".join(caminho) if caminho else "Sem caminho"
        
        resultados.append({
            'X': '',
            'Y': '',
            'bairro_X': bairro_x,
            'bairro_Y': bairro_y,
            'custo': custo if custo != float('inf') else 'Infinito',
            'caminho': caminho_str
        })
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['X', 'Y', 'bairro_X', 'bairro_Y', 'custo', 'caminho'])
        writer.writeheader()
        writer.writerows(resultados)
    
main()
