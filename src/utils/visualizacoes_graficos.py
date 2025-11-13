import csv
from pathlib import Path
from typing import Dict, Set
from collections import deque
import math

import matplotlib.pyplot as plt


def normalizar_nome(name: str) -> str:
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


def calcular_densidade(num_vertices: int, num_arestas: int) -> float:
    if num_vertices < 2:
        return 0.0
    return (2 * num_arestas) / (num_vertices * (num_vertices - 1))


def carregar_adjacencias(csv_path: Path):
    grafo: Dict[str, Set[str]] = {}
    arestas = set()
    vertices = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origem = normalizar_nome(row.get('bairro_origem', '').strip())
            destino = normalizar_nome(row.get('bairro_destino', '').strip())
            if not origem or not destino:
                continue
            vertices.add(origem); vertices.add(destino)
            grafo.setdefault(origem, set()).add(destino)
            grafo.setdefault(destino, set()).add(origem)
            arestas.add(tuple(sorted([origem, destino])))
    return grafo, vertices, arestas


def calcular_graus(grafo: Dict[str, Set[str]]):
    graus = {v: len(neigh) for v, neigh in grafo.items()}
    return graus


def calcular_ego(grafo: Dict[str, Set[str]], vertices: Set[str]):
    linhas = []
    for v in sorted(vertices):
        neigh = grafo.get(v, set())
        grau = len(neigh)
        S = {v} | neigh
        ordem = len(S)
        arestas_in = 0
        for a in S:
            for b in grafo.get(a, set()):
                if b in S and a < b:
                    arestas_in += 1
        dens = calcular_densidade(ordem, arestas_in)
        linhas.append({'bairro': v, 'grau': grau, 'ordem_ego': ordem, 'tamanho_ego': arestas_in, 'densidade_ego': dens})
    return linhas


def carregar_microrregiao(csv_path: Path):
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


def calcular_microrregiao(vertices: Set[str], arestas: Set[tuple], microrregiao: Dict[str, list]):
    data = []
    for nome, bairros in microrregiao.items():
        bairros_set = set(bairros) & vertices
        arestas_in = 0
        for a, b in arestas:
            if a in bairros_set and b in bairros_set:
                arestas_in += 1
        ordem = len(bairros_set)
        tamanho = arestas_in
        dens = calcular_densidade(ordem, tamanho)
        data.append({'microrregiao': nome, 'ordem': ordem, 'tamanho': tamanho, 'densidade': dens})
    return data


def main():
    base = Path(__file__).parent.parent.parent
    csv_adj = base / 'data' / 'adjacencias_bairros.csv'
    csv_bairros = base / 'data' / 'bairros_recife.csv'
    out_dir = base / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    grafo, vertices, arestas = carregar_adjacencias(csv_adj)

    graus = calcular_graus(grafo)
    graus_list = sorted(graus.items(), key=lambda x: x[1], reverse=True)

    if graus:
        plt.figure(figsize=(8, 5))
        max_grau = max(graus.values())
        bins = range(0, max_grau + 2)
        plt.hist(list(graus.values()), bins=bins, edgecolor='black')
        plt.title('Distribuição de graus dos bairros')
        plt.xlabel('Grau')
        plt.ylabel('Número de bairros')
        plt.grid(axis='y', alpha=0.7)
        plt.tight_layout()
        plt.savefig(out_dir / 'grau_bairro_histograma.png')
        plt.close()

    ego_linhas = calcular_ego(grafo, vertices)

    micror = carregar_microrregiao(csv_bairros)
    micror_names = []
    micror_sets = []
    for name, bairros in micror.items():
        s = set(bairros) & vertices
        if len(s) > 0:
            micror_names.append(name)
            micror_sets.append(sorted(s))

    def bfs_distances(adj: Dict[str, Set[str]], src: str) -> Dict[str, int]:
        dist = {src: 0}
        q = deque([src])
        while q:
            u = q.popleft()
            for v in adj.get(u, []):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    n = len(micror_names)
    if n > 0:
        matrix = [[math.nan] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                total = 0.0
                count = 0
                for u in micror_sets[i]:
                    dists = bfs_distances(grafo, u)
                    for v in micror_sets[j]:
                        if v in dists:
                            total += dists[v]
                            count += 1
                if count > 0:
                    matrix[i][j] = total / count

        plt.figure(figsize=(10, 8))
        im = plt.imshow(matrix, interpolation='nearest', cmap='viridis')
        plt.colorbar(im, fraction=0.046, pad=0.04, label='Distância média (saltos)')
        plt.xticks(range(n), micror_names, rotation=90, fontsize=8)
        plt.yticks(range(n), micror_names, fontsize=8)
        plt.title('Heatmap: distância média entre microrregiões')
        plt.tight_layout()
        plt.savefig(out_dir / 'microrregioes_distancia_heatmap.png')
        plt.close()

    micror_data = calcular_microrregiao(vertices, arestas, micror)

    pie_names = [d['microrregiao'] for d in micror_data if d['ordem'] > 0]
    pie_sizes = [d['ordem'] for d in micror_data if d['ordem'] > 0]
    if pie_sizes:
        plt.figure(figsize=(8, 8))
        plt.pie(pie_sizes, labels=pie_names, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
        plt.title('Proporção de bairros por Microrregião')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(out_dir / 'piechart_microrregioes.png')
        plt.close()


main()
