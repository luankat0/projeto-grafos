import csv
import heapq
import json
from pathlib import Path
from typing import Dict, List, Tuple

from pyvis.network import Network

def gerar_grafo(csv_path: Path) -> Dict[str, Dict[str, float]]:
    adj: Dict[str, Dict[str, float]] = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for linha in reader:

            origem = linha.get('bairro_origem', '').strip()
            destino = linha.get('bairro_destino', '').strip()

            if not origem or not destino:
                continue

            try:
                w = float((linha.get('peso') or '').strip() or 1.0)
            except Exception:
                w = 1.0
            adj.setdefault(origem, {})[destino] = w
            adj.setdefault(destino, {})[origem] = w

    return adj


def dijkstra(adj: Dict[str, Dict[str, float]], src: str, dst: str) -> Tuple[float, List[str]]:
    dist: Dict[str, float] = {n: float('inf') for n in adj}
    dist[src] = 0.0
    ant: Dict[str, str] = {}
    pilha: List[Tuple[float, str]] = [(0.0, src)]
    visitado = set()

    while pilha:
        atual, origem = heapq.heappop(pilha)

        if origem in visitado:
            continue

        visitado.add(origem)

        if origem == dst:
            break

        for destibo, peso in adj.get(origem, {}).items():

            novo = atual + (peso or 1.0)
            if novo < dist.get(destibo, float('inf')):
                dist[destibo] = novo
                ant[destibo] = origem
                heapq.heappush(pilha, (novo, destibo))

    if dist.get(dst, float('inf')) == float('inf'):
        return float('inf'), []

    path: List[str] = []
    caminho_temp = dst
    while caminho_temp is not None:
        path.append(caminho_temp)
        caminho_temp = ant.get(caminho_temp)
    path.reverse()
    return dist[dst], path


def gerar_caminho_pyviz(adj: Dict[str, Dict[str, float]], path: List[str], out_html_path: Path) -> None:
    net = Network(height='800px', width='100%', directed=False)
    for i, node in enumerate(path):
        if i == 0:
            net.add_node(node, label=node, color='green', size=30, title=node)
        elif i == len(path) - 1:
            net.add_node(node, label=node, color='red', size=30, title=node)
        else:
            net.add_node(node, label=node, color='lightblue', size=20, title=node)

    for origem, destino in zip(path, path[1:]):
        peso = adj.get(origem, {}).get(destino, 1.0)
        net.add_edge(origem, destino, value=peso, title=f'peso={peso}')

    net.toggle_physics(False)
    out_html_path.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(out_html_path.as_posix(), notebook=False)


def main() -> None:
    base = Path(__file__).parent.parent.parent
    csv_path = base / 'data' / 'adjacencias_bairros.csv'
    out_html = base / 'out' / 'arvore_percurso.html'

    origem = 'Nova Descoberta'
    destino = 'Boa Viagem(Setubal)'

    try:
        adj = gerar_grafo(csv_path)
    except Exception as e:
        return

    if origem not in adj or destino not in adj:
        return

    custo, caminho = dijkstra(adj, origem, destino)
    if not caminho:
        return

    gerar_caminho_pyviz(adj, caminho, out_html)

main()
