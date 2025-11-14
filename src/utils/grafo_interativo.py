import csv
import heapq
import json
from pathlib import Path
from typing import Dict, List

from pyvis.network import Network


def carregar_adjacencias(csv_path: Path) -> Dict[str, Dict[str, float]]:
    adj: Dict[str, Dict[str, float]] = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origem = row.get('bairro_origem', '').strip()
            destino = row.get('bairro_destino', '').strip()
            if not origem or not destino:
                continue
            try:
                w = float((row.get('peso') or '').strip() or 1.0)
            except Exception:
                w = 1.0
            adj.setdefault(origem, {})[destino] = w
            adj.setdefault(destino, {})[origem] = w
    return adj


def carregar_microrregiao(csv_path: Path) -> Dict[str, List[str]]:
    micror = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for header in headers:
            if header.strip():
                micror[header] = []
        for row in reader:
            for i, value in enumerate(row):
                if i < len(headers) and value.strip():
                    micror[headers[i]].append(value.strip())
    return micror


def calcular_graus(adj: Dict[str, Dict[str, float]]) -> Dict[str, int]:
    return {v: len(neigh) for v, neigh in adj.items()}


def calcular_ego_metrics(adj: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    dens = {}
    for destino in adj:
        neigh = set(adj[destino].keys())
        S = {destino} | neigh
        ordem = len(S)
        arestas_in = 0
        for a in S:
            for b in adj.get(a, {}).keys():
                if b in S and a < b:
                    arestas_in += 1
        if ordem < 2:
            dens[destino] = 0.0
        else:
            dens[destino] = (2 * arestas_in) / (ordem * (ordem - 1))
    return dens


def dijkstra(adj: Dict[str, Dict[str, float]], src: str, dst: str):
    dist = {n: float('inf') for n in adj}
    dist[src] = 0.0
    prev = {}
    heap = [(0.0, src)]
    visited = set()
    while heap:
        d, origem = heapq.heappop(heap)
        if origem in visited:
            continue
        visited.add(origem)
        if origem == dst:
            break
        for destino, w in adj.get(origem, {}).items():
            nd = d + (w or 1.0)
            if nd < dist.get(destino, float('inf')):
                dist[destino] = nd
                prev[destino] = origem
                heapq.heappush(heap, (nd, destino))
    if dist.get(dst, float('inf')) == float('inf'):
        return float('inf'), []
    path = []
    caminho_temp = dst
    while caminho_temp is not None:
        path.append(caminho_temp)
        caminho_temp = prev.get(caminho_temp)
    path.reverse()
    return dist[dst], path


def gerar_html(adj, micror_map, out_html: Path, highlight_path: List[str]):
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
    graus = calcular_graus(adj)
    dens_ego = calcular_ego_metrics(adj)

    bairro_to_micror = {}
    for region, bairros in micror_map.items():
        for b in bairros:
            bairro_to_micror[b] = region

    for node in sorted(adj.keys()):
        grau = graus.get(node, 0)
        micror = bairro_to_micror.get(node, '')
        dens = dens_ego.get(node, 0.0)
        title = f'Grau: {grau} / Microrregiao: {micror} / Densidade ego: {dens:.3f}'
        net.add_node(node, label=node, title=title)

    added = set()
    for origem, nbrs in adj.items():
        for destino, peso in nbrs.items():
            ekey = tuple(sorted([origem, destino]))
            if ekey in added:
                continue
            added.add(ekey)
            net.add_edge(origem, destino, value=peso, title=f'peso: {peso}')

    net.toggle_physics(True)

    html = net.generate_html()

    path_js = json.dumps(highlight_path)

    controls_html = """
<div style="position:fixed;top:10px;left:10px;z-index:999;background:white;padding:8px;border-radius:6px;border:1px solid #ccc;">
    <div>
        <input id="search_input" type="text" placeholder="Buscar bairro" style="width:180px; " />
        <button onclick="searchNode()" style="border:none;border-radius:4px;" >Buscar</button>
    </div>
    <div style="margin-top:6px;">
        <button onclick="highlightPath()" style="border:none;border-radius:4px;">Realçar: Nova Descoberta → Boa Viagem(Setubal)</button>
    </div>
</div>

<script>
function searchNode(){
    var q = document.getElementById('search_input').value;
    if(!q) return;
    try{ network.selectNodes([q]); network.focus(q); }catch(e){ alert('No node: '+q); }
}

function highlightPath(){
    var path = __PATH_JS__;
    var allNodes = nodes.get();
    allNodes.forEach(function(n){ nodes.update({id:n.id, color:{background:'lightblue'}}); });
    var allEdges = edges.get();
    allEdges.forEach(function(e){ edges.update({id:e.id, color:{color:'#97c2fc'}, width:1}); });
    for(var i=0;i<path.length;i++){
        var nid = path[i];
        var col = (i==0)?'green':(i==path.length-1)?'red':'orange';
        nodes.update({id:nid, color:{background:col}});
        if(i<path.length-1){
            var a = path[i]; var b = path[i+1];
            // find edges between a and b
            var matched = edges.get().filter(function(e){ return (e.from==a && e.to==b) || (e.from==b && e.to==a); });
            matched.forEach(function(e){ edges.update({id:e.id, color:{color:'red'}, width:3}); });
        }
    }
    if(path.length>0) network.focus(path[0]);
}
</script>
"""

    controls_html = controls_html.replace('__PATH_JS__', path_js)

    insert_at = html.find('<body>')
    if insert_at != -1:
        insert_at_end = html.find('\n', insert_at) + 1
        html = html[:insert_at_end] + controls_html + html[insert_at_end:]

    out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    base = Path(__file__).parent.parent.parent
    csv_adj = base / 'data' / 'adjacencias_bairros.csv'
    csv_bairros = base / 'data' / 'bairros_recife.csv'
    out_html = base / 'out' / 'grafo_interativo.html'

    adj = carregar_adjacencias(csv_adj)
    micror = carregar_microrregiao(csv_bairros)

    src = 'Nova Descoberta'
    dst = 'Boa Viagem(Setubal)'
    if src in adj and dst in adj:
        try:
            cost, path = dijkstra(adj, src, dst)
        except Exception:
            path = []
    else:
        path = []

    gerar_html(adj, micror, out_html, path)

main()
