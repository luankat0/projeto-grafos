import csv
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set
import math
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from graphs.algorithms import bfs, dfs, dijkstra, bellman_ford


def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def load_flights_data(csv_path: Path) -> Tuple[Dict, Dict]:
    airports = {}
    flights = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if row['Situacao.Voo'] == 'Cancelado':
                    continue
                
                origem = row['Aeroporto.Origem']
                destino = row['Aeroporto.Destino']
                
                if origem not in airports and row['LatOrig'] and row['LongOrig']:
                    airports[origem] = {
                        'lat': float(row['LatOrig']),
                        'lon': float(row['LongOrig']),
                        'cidade': row['Cidade.Origem'],
                        'estado': row['Estado.Origem']
                    }
                
                if destino not in airports and row['LatDest'] and row['LongDest']:
                    airports[destino] = {
                        'lat': float(row['LatDest']),
                        'lon': float(row['LongDest']),
                        'cidade': row['Cidade.Destino'],
                        'estado': row['Estado.Destino']
                    }
                
                if row['Partida.Real'] and row['Chegada.Real']:
                    partida = datetime.fromisoformat(row['Partida.Real'].replace('Z', '+00:00'))
                    chegada = datetime.fromisoformat(row['Chegada.Real'].replace('Z', '+00:00'))
                    tempo_voo = (chegada - partida).total_seconds() / 3600
                    
                    flights.append({
                        'origem': origem,
                        'destino': destino,
                        'tempo': tempo_voo,
                        'companhia': row['Companhia.Aerea']
                    })
            except (KeyError, ValueError) as e:
                continue
    
    return airports, flights

def build_graph(airports: Dict, flights: List) -> Tuple[Dict, Dict]:
    weighted_graph = defaultdict(lambda: {})
    unweighted_graph = defaultdict(list)
    
    routes = defaultdict(list)
    for flight in flights:
        key = (flight['origem'], flight['destino'])
        routes[key].append(flight['tempo'])
    
    for (origem, destino), tempos in routes.items():
        if origem in airports and destino in airports:
            tempo_medio = sum(tempos) / len(tempos)
            
            lat1, lon1 = airports[origem]['lat'], airports[origem]['lon']
            lat2, lon2 = airports[destino]['lat'], airports[destino]['lon']
            distancia = calcular_distancia(lat1, lon1, lat2, lon2)
            
            peso = tempo_medio + (distancia / 1000)
            
            weighted_graph[origem][destino] = round(peso, 2)
            unweighted_graph[origem].append(destino)
    
    return dict(weighted_graph), dict(unweighted_graph)


def run_analysis():
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / 'data' / 'dataset_parte2' / 'voos_brasil.csv'
    out_path = base_path / 'out'
    out_path.mkdir(exist_ok=True)
    
    airports, flights = load_flights_data(data_path)

    weighted_graph, unweighted_graph = build_graph(airports, flights)
    
    num_vertices = len(airports)
    num_edges = sum(len(neighbors) for neighbors in weighted_graph.values())

    
    out_degrees = [len(neighbors) for neighbors in weighted_graph.values()]
    in_degrees = defaultdict(int)
    for node in weighted_graph:
        for neighbor in weighted_graph[node]:
            in_degrees[neighbor] += 1
    
    if out_degrees:
        avg_out = sum(out_degrees) / len(out_degrees)
        max_out = max(out_degrees)
        min_out = min(out_degrees)
        
        from collections import Counter
        degree_dist = Counter(out_degrees)
    
    in_degree_values = [in_degrees[node] for node in airports.keys()]
    if in_degree_values:
        avg_in = sum(in_degree_values) / len(in_degree_values)
        max_in = max(in_degree_values)
        min_in = min(in_degree_values)

        from collections import Counter
        in_degree_dist = Counter(in_degree_values)

    
    if num_vertices > 1:
        density = num_edges / (num_vertices * (num_vertices - 1))
    
    top_airports = sorted(unweighted_graph.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for i, (airport, connections) in enumerate(top_airports, 1):
        cidade = airports[airport]['cidade']
        grau_entrada = in_degrees[airport]
        grau_saida = len(connections)

    
    all_weights = [w for neighbors in weighted_graph.values() for w in neighbors.values()]
    if all_weights:
        avg_weight = sum(all_weights) / len(all_weights)
        min_weight = min(all_weights)
        max_weight = max(all_weights)
    
    report = {
        'dataset': {
            'vertices': num_vertices,
            'edges': num_edges,
            'type': 'Directed Weighted Graph (Flight Network)',
            'out_degree': {
                'avg': round(avg_out, 2) if out_degrees else 0,
                'min': min_out if out_degrees else 0,
                'max': max_out if out_degrees else 0,
                'distribution': dict(degree_dist) if out_degrees else {}
            },
            'in_degree': {
                'avg': round(avg_in, 2) if in_degree_values else 0,
                'min': min_in if in_degree_values else 0,
                'max': max_in if in_degree_values else 0,
                'distribution': dict(in_degree_dist) if in_degree_values else {}
            },
            'density': round(density, 6) if num_vertices > 1 else 0,
            'weights': {
                'avg': round(avg_weight, 2) if all_weights else 0,
                'min': round(min_weight, 2) if all_weights else 0,
                'max': round(max_weight, 2) if all_weights else 0
            }
        },
        'algorithms': {}
    }

    bfs_sources = [airport for airport, _ in top_airports[:3]]
    
    for source in bfs_sources:
        start_time = time.perf_counter()
        
        result = bfs(unweighted_graph, source)
        
        end_time = time.perf_counter()
        elapsed = (end_time - start_time) * 1000
        
        cidade = airports[source]['cidade']

        report['algorithms'][f'bfs_{source}'] = {
            'source': source,
            'cidade': cidade,
            'nodes_reached': len(result['order']),
            'layers': len(result['layers']),
            'time_ms': round(elapsed, 3)
        }
    
    
    dfs_sources = [airport for airport, _ in top_airports[2:5]]
    
    for source in dfs_sources:
        start_time = time.perf_counter()
        
        result = dfs(unweighted_graph, source)
        
        end_time = time.perf_counter()
        elapsed = (end_time - start_time) * 1000
        
        cidade = airports[source]['cidade']
        
        report['algorithms'][f'dfs_{source}'] = {
            'source': source,
            'cidade': cidade,
            'nodes_reached': len(result['order']),
            'has_cycle': result['has_cycle'],
            'time_ms': round(elapsed, 3)
        }
    

    
    dijkstra_pairs = []
    top_5_airports = [a for a, _ in top_airports[:5]]
    
    if len(top_5_airports) >= 2:
        dijkstra_pairs.append((top_5_airports[0], top_5_airports[1]))
    
    if len(top_5_airports) >= 5:
        dijkstra_pairs.append((top_5_airports[0], top_5_airports[3]))
        dijkstra_pairs.append((top_5_airports[1], top_5_airports[4]))
        dijkstra_pairs.append((top_5_airports[2], top_5_airports[0]))
        dijkstra_pairs.append((top_5_airports[3], top_5_airports[2]))
    
    for source, target in dijkstra_pairs[:5]:
        start_time = time.perf_counter()
        
        result = dijkstra(weighted_graph, source, target)
        
        end_time = time.perf_counter()
        elapsed = (end_time - start_time) * 1000
        
        cidade_orig = airports[source]['cidade']
        cidade_dest = airports[target]['cidade']

        
        if result['path_to_end']:
            path_str = ' → '.join([f"{a}" for a in result['path_to_end'][:3]])
            if len(result['path_to_end']) > 3:
                path_str += f" → ... ({len(result['path_to_end'])} aeroportos)"

        report['algorithms'][f'dijkstra_{source}_to_{target}'] = {
            'origem': f"{source} ({cidade_orig})",
            'destino': f"{target} ({cidade_dest})",
            'cost': round(result['cost'], 2),
            'path_length': len(result['path_to_end']) if result['path_to_end'] else 0,
            'time_ms': round(elapsed, 3)
        }

    weighted_graph_neg = {k: v.copy() for k, v in weighted_graph.items()}
    
    edges_negativas = []
    if len(top_5_airports) >= 3:
        if top_5_airports[0] in weighted_graph_neg and top_5_airports[1] in weighted_graph_neg[top_5_airports[0]]:
            weighted_graph_neg[top_5_airports[0]][top_5_airports[1]] = -2.0
            edges_negativas.append(f"{top_5_airports[0]} → {top_5_airports[1]} (-2.0)")
        
        if top_5_airports[1] in weighted_graph_neg and len(weighted_graph_neg[top_5_airports[1]]) > 0:
            primeiro_dest = list(weighted_graph_neg[top_5_airports[1]].keys())[0]
            weighted_graph_neg[top_5_airports[1]][primeiro_dest] = -1.5
            edges_negativas.append(f"{top_5_airports[1]} → {primeiro_dest} (-1.5)")
    
    source = top_5_airports[0]
    all_nodes = set(weighted_graph_neg.keys())
    
    start_time = time.perf_counter()
    
    result_neg = bellman_ford(weighted_graph_neg, source, all_nodes)
    
    end_time = time.perf_counter()
    elapsed = (end_time - start_time) * 1000

    report['algorithms']['bellman_ford_negative_weights'] = {
        'source': f"{source} ({airports[source]['cidade']})",
        'negative_edges': edges_negativas,
        'has_negative_cycle': result_neg['has_negative_cycle'],
        'time_ms': round(elapsed, 3)
    }
    
    weighted_graph_cycle = {k: v.copy() for k, v in weighted_graph.items()}
    
    if len(top_5_airports) >= 3:
        a1, a2, a3 = top_5_airports[0], top_5_airports[1], top_5_airports[2]
        
        if a1 not in weighted_graph_cycle:
            weighted_graph_cycle[a1] = {}
        if a2 not in weighted_graph_cycle:
            weighted_graph_cycle[a2] = {}
        if a3 not in weighted_graph_cycle:
            weighted_graph_cycle[a3] = {}
        
        weighted_graph_cycle[a1][a2] = 2.0
        weighted_graph_cycle[a2][a3] = 2.0
        weighted_graph_cycle[a3][a1] = -8.0
        
        all_nodes_cycle = set(weighted_graph_cycle.keys())
        
        start_time = time.perf_counter()
        
        result_cycle = bellman_ford(weighted_graph_cycle, a1, all_nodes_cycle)
        
        end_time = time.perf_counter()
        elapsed = (end_time - start_time) * 1000
        
        report['algorithms']['bellman_ford_negative_cycle'] = {
            'cycle': f"{a1} → {a2} → {a3} → {a1}",
            'weights': "2.0 + 2.0 + (-8.0) = -4.0",
            'has_negative_cycle': result_cycle['has_negative_cycle'],
            'negative_cycle': result_cycle['negative_cycle'],
            'time_ms': round(elapsed, 3)
        }
    
    report_path = out_path / 'parte2_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)



if __name__ == '__main__':
    run_analysis()
