import csv
import heapq
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

from pyvis.network import Network


def carregar_voos(csv_path: Path) -> Tuple[Dict[str, Dict[str, float]], Set[str]]:
    adj: Dict[str, Dict[str, float]] = {}
    vertices = set()
    contagem_rotas = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origem = row.get('Aeroporto.Origem', '').strip()
            destino = row.get('Aeroporto.Destino', '').strip()
            
            if not origem or not destino:
                continue
            
            vertices.add(origem)
            vertices.add(destino)
            
            rota_key = (origem, destino)
            contagem_rotas[rota_key] = contagem_rotas.get(rota_key, 0) + 1
    
    for (origem, destino), count in contagem_rotas.items():
        adj.setdefault(origem, {})[destino] = float(count)
    
    return adj, vertices


def calcular_graus(adj: Dict[str, Dict[str, float]], vertices: Set[str]) -> Tuple[Dict[str, int], Dict[str, int]]:
    grau_saida = {v: len(adj.get(v, {})) for v in vertices}
    grau_entrada = {v: 0 for v in vertices}
    
    for origem, destinos in adj.items():
        for destino in destinos:
            grau_entrada[destino] += 1
    
    return grau_saida, grau_entrada


def obter_pais(nome_aeroporto: str) -> str:
    if 'Miami' in nome_aeroporto:
        return 'Estados Unidos'
    else:
        return 'Brasil'


def dijkstra(adj: Dict[str, Dict[str, float]], src: str, dst: str, vertices: Set[str]):
    if src not in vertices or dst not in vertices:
        return float('inf'), []
    
    dist = {n: float('inf') for n in vertices}
    dist[src] = 0.0
    prev = {}
    heap = [(0.0, src)]
    visited = set()
    
    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == dst:
            break
        for v, w in adj.get(u, {}).items():
            nd = d + (1.0 / w if w > 0 else 1.0)  
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    
    if dist.get(dst, float('inf')) == float('inf'):
        return float('inf'), []
    
    path = []
    current = dst
    while current is not None:
        path.append(current)
        current = prev.get(current)
    path.reverse()
    
    return dist[dst], path


def gerar_html_interativo(adj: Dict[str, Dict[str, float]], vertices: Set[str], 
                          out_html: Path, highlight_path: List[str]):
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black',
                  notebook=False, directed=True)
    
    grau_saida, grau_entrada = calcular_graus(adj, vertices)
    
    hub = None
    for v in vertices:
        if 'Miami' in v:
            hub = v
            break
    
    cores_pais = {
        'Estados Unidos': '#F44336',  
        'Brasil': '#2196F3'         
    }
    
    for node in sorted(vertices):
        pais = obter_pais(node)
        grau_total = grau_saida[node] + grau_entrada[node]
        
        tamanho = 20 + grau_total * 5
        
        node_color = cores_pais.get(pais, '#97C2FC')
        
        nome_curto = node.split(',')[0] if ',' in node else node
        nome_curto = nome_curto.replace(' - ', '\n')
        
        title = (f'{node} / '
                f'País: {pais} / '
                f'Grau Total: {grau_total} / '
                f'Grau Entrada: {grau_entrada[node]} / '
                f'Grau Saída: {grau_saida[node]}')
        
        net.add_node(node, 
                    label=nome_curto, 
                    title=title, 
                    color=node_color,
                    size=tamanho,
                    font={'size': 14, 'color': 'black', 'bold': True})
    
    for origem, destinos in adj.items():
        for destino, peso in destinos.items():
            if hub and origem == hub:
                edge_color = '#4CAF50' 
            elif hub and destino == hub:
                edge_color = '#FF5722'  
            else:
                edge_color = '#2196F3'  
            
            width = 2 + (peso / 10)
            
            title_edge = f'{origem} → {destino} / Voos: {int(peso)}'
            
            net.add_edge(origem, destino, 
                        value=peso,
                        title=title_edge,
                        color=edge_color,
                        width=width,
                        arrows='to')
    
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 250,
                "springConstant": 0.04,
                "damping": 0.09,
                "avoidOverlap": 0.1
            },
            "stabilization": {
                "enabled": true,
                "iterations": 2000,
                "updateInterval": 25
            }
        },
        "nodes": {
            "font": {
                "size": 16,
                "face": "arial",
                "bold": true
            },
            "borderWidth": 2,
            "shadow": true
        },
        "edges": {
            "smooth": {
                "enabled": true,
                "type": "dynamic"
            },
            "shadow": true
        }
    }
    """)
    
    html = net.generate_html()
    
    num_vertices = len(vertices)
    num_arestas = sum(len(destinos) for destinos in adj.items())
    total_voos = sum(sum(destinos.values()) for destinos in adj.values())
    
    legenda_html = f"""
<div style="position:fixed;top:10px;left:10px;z-index:999;background:rgba(255,255,255,0.95);padding:15px;border-radius:8px;border:2px solid #ddd;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h3 style="margin:0 0 10px 0;color:#333;font-size:16px;">Rede de Voos Brasil</h3>
    
    <div style="font-size:12px;color:#666;margin-bottom:12px;">
        <div style="margin:3px 0;">✈️ Aeroportos: {num_vertices}</div>
        <div style="margin:3px 0;">🛫 Rotas: {num_arestas}</div>
        <div style="margin:3px 0;">📊 Total de Voos: {int(total_voos)}</div>
    </div>
    
    <div style="border-top:1px solid #ddd;padding-top:10px;font-size:11px;">
        <div style="display:flex;align-items:center;margin:4px 0;">
            <span style="width:18px;height:18px;background:#F44336;border-radius:50%;margin-right:10px;"></span>
            <span>Hub (Miami)</span>
        </div>
        <div style="display:flex;align-items:center;margin:4px 0;">
            <span style="width:18px;height:18px;background:#2196F3;border-radius:50%;margin-right:10px;"></span>
            <span>Aeroportos BR</span>
        </div>
        <div style="display:flex;align-items:center;margin:4px 0;">
            <span style="width:35px;height:4px;background:#4CAF50;margin-right:10px;"></span>
            <span>Saída do Hub</span>
        </div>
        <div style="display:flex;align-items:center;margin:4px 0;">
            <span style="width:35px;height:4px;background:#FF5722;margin-right:10px;"></span>
            <span>Entrada no Hub</span>
        </div>
    </div>
</div>
"""
    
    insert_at = html.find('<body>')
    if insert_at != -1:
        insert_at_end = html.find('\n', insert_at) + 1
        html = html[:insert_at_end] + legenda_html + html[insert_at_end:]
    
    out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nGrafo interativo salvo em: {out_html}")


def main():
    base = Path(__file__).parent.parent.parent
    csv_voos = base / 'data' / 'voos_brasil.csv'
    out_html = base / 'out' / 'grafo_voos_interativo.html'
    
    print("Carregando dados de voos...")
    adj, vertices = carregar_voos(csv_voos)
    
    print(f"Carregados {len(vertices)} aeroportos")
    print(f"Total de rotas diretas: {sum(len(d) for d in adj.values())}")
    print(f"Total de voos registrados: {int(sum(sum(d.values()) for d in adj.values()))}")
    
    aeroportos_br = [v for v in vertices if 'Miami' not in v]
    highlight_path = []
    
    if len(aeroportos_br) >= 2:
        src = aeroportos_br[0]
        dst = aeroportos_br[-1]
        print(f"\nCalculando caminho: {src} → {dst}")
        try:
            cost, path = dijkstra(adj, src, dst, vertices)
            if path:
                highlight_path = path
                print(f"Caminho encontrado: {' → '.join(path)}")
                print(f"Custo: {cost:.2f}")
        except Exception as e:
            print(f"Erro ao calcular caminho: {e}")
    
    print("\nGerando grafo interativo...")
    gerar_html_interativo(adj, vertices, out_html, highlight_path)
    print("\n✅ Concluído! Abra o arquivo HTML em um navegador.")


if __name__ == '__main__':
    main()
