import csv
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from graphs.algorithms import dijkstra as dijkstra_base


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
    result = dijkstra_base(grafo, origem, destino)
    if result['path_to_end'] is None:
        return float('inf'), []
    return result['cost'], result['path_to_end']


def main():
    base_path = Path(__file__).parent.parent.parent
    input_path = base_path / "data" / "adjacencias_bairros.csv"
    enderecos_path = base_path / "data" / "enderecos.csv"
    output_path = base_path / "out" / "distancias_enderecos.csv"
    
    pares_especificos = [
        ("Nova Descoberta", "Boa Viagem(Setubal)"),
        ("Dois Irmaos", "Casa Amarela"),
        ("Jaqueira", "Derby"),
        ("Boa Viagem", "Brasilia Teimosa"),
        ("Macaxeira", "Passarinho")
    ]

    enderecos = []
    with open(enderecos_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for linha in reader:
            addr_x = linha['bairro_x'].strip()
            addr_y = linha['bairro_y'].strip()
            enderecos.append((addr_x, addr_y))

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
        arquivo = f"percurso_{safe_arquivo(bx).lower()}_{safe_arquivo(by).lower()}.json"
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
