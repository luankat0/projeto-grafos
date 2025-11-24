import csv
import json
import math
import unicodedata
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))
from graphs.algorithms import dijkstra as dijkstra_base

from pyvis.network import Network
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


def normalizar_nome_unicode(nome: str) -> str:
    nome_sem_acento = unicodedata.normalize('NFD', nome)
    nome_sem_acento = ''.join(char for char in nome_sem_acento if unicodedata.category(char) != 'Mn')
    return nome_sem_acento.strip().lower()


def calcular_densidade(num_vertices: int, num_arestas: int) -> float:
    if num_vertices < 2:
        return 0.0
    return (2 * num_arestas) / (num_vertices * (num_vertices - 1))


def dijkstra_wrapper(adj: Dict[str, Dict[str, float]], src: str, dst: str) -> Tuple[float, List[str]]:
    result = dijkstra_base(adj, src, dst)
    if result['path_to_end'] is None:
        return float('inf'), []
    return result['cost'], result['path_to_end']


def gerar_grafo_adjacencias(csv_path: Path) -> Dict[str, Dict[str, float]]:
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


def carregar_adjacencias_set(csv_path: Path):
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
            vertices.add(origem)
            vertices.add(destino)
            grafo.setdefault(origem, set()).add(destino)
            grafo.setdefault(destino, set()).add(origem)
            arestas.add(tuple(sorted([origem, destino])))
    return grafo, vertices, arestas


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


def gerar_caminho_html(base_path: Path):
    print("\n=== Gerando visualização: Árvore de Percurso ===")
    csv_path = base_path / 'data' / 'adjacencias_bairros.csv'
    out_html = base_path / 'out' / 'arvore_percurso.html'

    origem = 'Nova Descoberta'
    destino = 'Boa Viagem(Setubal)'

    try:
        adj = gerar_grafo_adjacencias(csv_path)
    except Exception as e:
        print(f"Erro ao carregar grafo: {e}")
        return

    if origem not in adj or destino not in adj:
        print(f"Origem ou destino não encontrados no grafo")
        return

    custo, caminho = dijkstra_wrapper(adj, origem, destino)
    if not caminho:
        print("Nenhum caminho encontrado")
        return

    net = Network(height='800px', width='100%', directed=False)
    for i, node in enumerate(caminho):
        if i == 0:
            net.add_node(node, label=node, color='green', size=30, title=node)
        elif i == len(caminho) - 1:
            net.add_node(node, label=node, color='red', size=30, title=node)
        else:
            net.add_node(node, label=node, color='lightblue', size=20, title=node)

    for origem_edge, destino_edge in zip(caminho, caminho[1:]):
        peso = adj.get(origem_edge, {}).get(destino_edge, 1.0)
        net.add_edge(origem_edge, destino_edge, value=peso, title=f'peso={peso}')

    net.toggle_physics(False)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(out_html), notebook=False)
    print(f"✓ Arquivo criado: {out_html}")


def gerar_grafo_interativo_bairros(base_path: Path):
    print("\n=== Gerando visualização: Grafo Interativo de Bairros ===")
    csv_adj = base_path / 'data' / 'adjacencias_bairros.csv'
    csv_bairros = base_path / 'data' / 'bairros_recife.csv'
    out_html = base_path / 'out' / 'grafo_interativo.html'

    adj = gerar_grafo_adjacencias(csv_adj)
    micror = carregar_microrregiao(csv_bairros)

    src = 'Nova Descoberta'
    dst = 'Boa Viagem(Setubal)'
    path = []
    if src in adj and dst in adj:
        try:
            cost, path = dijkstra_wrapper(adj, src, dst)
        except Exception:
            pass

    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
    
    graus = {v: len(neigh) for v, neigh in adj.items()}
    
    dens_ego = {}
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
            dens_ego[destino] = 0.0
        else:
            dens_ego[destino] = (2 * arestas_in) / (ordem * (ordem - 1))

    excecoes_nomes = {
        'boa viagem(setubal)': 'Boa Viagem',
        'alto santa terezinha': 'Alto Santa Teresinha'
    }

    bairro_to_micror = {}
    for region, bairros in micror.items():
        for b in bairros:
            bairro_to_micror[b] = region
            bairro_to_micror[normalizar_nome_unicode(b)] = region

    micror_colors = {
        '1.1': '#FF6B6B', '1.2': '#FF6B6B', '1.3': '#FF6B6B',
        '2.1': '#4ECDC4', '2.2': '#4ECDC4', '2.3': '#4ECDC4',
        '3.1': '#95E1D3', '3.2': '#95E1D3', '3.3': '#95E1D3',
        '4.1': '#FFE66D', '4.2': '#FFE66D', '4.3': '#FFE66D',
        '5.1': '#C77DFF', '5.2': '#C77DFF', '5.3': '#C77DFF',
        '6.1': '#FF9FF3', '6.2': '#FF9FF3', '6.3': '#FF9FF3'
    }

    for node in sorted(adj.keys()):
        grau = graus.get(node, 0)
        node_norm = normalizar_nome_unicode(node)
        if node_norm in excecoes_nomes:
            nome_correto = excecoes_nomes[node_norm]
            micror_val = bairro_to_micror.get(nome_correto, '') or bairro_to_micror.get(normalizar_nome_unicode(nome_correto), '')
        else:
            micror_val = bairro_to_micror.get(node, '') or bairro_to_micror.get(node_norm, '')
        
        dens = dens_ego.get(node, 0.0)
        node_color = micror_colors.get(micror_val, '#97C2FC')
        title = f'Bairro: {node} / Grau: {grau} / Microrregiao: {micror_val} / Densidade ego: {dens:.3f}'
        net.add_node(node, label=node, title=title, color=node_color)

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

    path_js = json.dumps(path)
    controls_html = f"""
<div style="position:fixed;top:10px;left:10px;z-index:999;background:white;padding:8px;border-radius:6px;border:1px solid #ccc;">
    <div>
        <input id="search_input" type="text" placeholder="Buscar bairro" style="width:180px;" />
        <button onclick="searchNode()" style="border:none;border-radius:4px;">Buscar</button>
    </div>
    <div style="margin-top:6px;">
        <button onclick="highlightPath()" style="border:none;border-radius:4px;">Realçar: Nova Descoberta → Boa Viagem(Setubal)</button>
    </div>
</div>

<script>
var pathData = {path_js};
function searchNode(){{
    var q = document.getElementById('search_input').value;
    if(!q) return;
    try{{ network.selectNodes([q]); network.focus(q); }}catch(e){{ alert('No node: '+q); }}
}}

function highlightPath(){{
    var path = pathData;
    var allNodes = nodes.get();
    allNodes.forEach(function(n){{ nodes.update({{id:n.id, color:{{background:'lightblue'}}}}); }});
    var allEdges = edges.get();
    allEdges.forEach(function(e){{ edges.update({{id:e.id, color:{{color:'#97c2fc'}}, width:1}}); }});
    for(var i=0;i<path.length;i++){{
        var nid = path[i];
        var col = (i==0)?'green':(i==path.length-1)?'red':'orange';
        nodes.update({{id:nid, color:{{background:col}}}});
        if(i<path.length-1){{
            var a = path[i]; var b = path[i+1];
            var matched = edges.get().filter(function(e){{ return (e.from==a && e.to==b) || (e.from==b && e.to==a); }});
            matched.forEach(function(e){{ edges.update({{id:e.id, color:{{color:'red'}}, width:3}}); }});
        }}
    }}
    if(path.length>0) network.focus(path[0]);
}}
</script>
"""

    insert_at = html.find('<body>')
    if insert_at != -1:
        insert_at_end = html.find('\n', insert_at) + 1
        html = html[:insert_at_end] + controls_html + html[insert_at_end:]

    out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Arquivo criado: {out_html}")


def gerar_grafo_voos_interativo(base_path: Path):
    print("\n=== Gerando visualização: Grafo Interativo de Voos ===")
    csv_voos = base_path / 'data' / 'dataset_parte2' / 'voos_brasil.csv'
    out_html = base_path / 'out' / 'grafo_voos_interativo.html'
    
    adj, vertices = carregar_voos(csv_voos)
    
    grau_saida = {v: len(adj.get(v, {})) for v in vertices}
    grau_entrada = {v: 0 for v in vertices}
    for origem, destinos in adj.items():
        for destino in destinos:
            grau_entrada[destino] += 1
    
    hub = None
    for v in vertices:
        if 'Miami' in v:
            hub = v
            break
    
    cores_pais = {'Estados Unidos': '#F44336', 'Brasil': '#2196F3'}
    
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black',
                  notebook=False, directed=True)
    
    for node in sorted(vertices):
        pais = 'Estados Unidos' if 'Miami' in node else 'Brasil'
        grau_total = grau_saida[node] + grau_entrada[node]
        tamanho = 20 + grau_total * 5
        node_color = cores_pais.get(pais, '#97C2FC')
        nome_curto = node.split(',')[0] if ',' in node else node
        nome_curto = nome_curto.replace(' - ', '\n')
        title = (f'{node} / País: {pais} / Grau Total: {grau_total} / '
                f'Grau Entrada: {grau_entrada[node]} / Grau Saída: {grau_saida[node]}')
        net.add_node(node, label=nome_curto, title=title, color=node_color,
                    size=tamanho, font={'size': 14, 'color': 'black', 'bold': True})
    
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
            net.add_edge(origem, destino, value=peso, title=title_edge,
                        color=edge_color, width=width, arrows='to')
    
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
            "stabilization": {"enabled": true, "iterations": 2000, "updateInterval": 25}
        },
        "nodes": {"font": {"size": 16, "face": "arial", "bold": true}, "borderWidth": 2, "shadow": true},
        "edges": {"smooth": {"enabled": true, "type": "dynamic"}, "shadow": true}
    }
    """)
    
    html = net.generate_html()
    num_vertices = len(vertices)
    num_arestas = sum(len(destinos) for destinos in adj.items())
    total_voos = sum(sum(destinos.values()) for destinos in adj.values())
    
    legenda_html = f"""
<div style="position:fixed;top:10px;left:10px;z-index:999;background:rgba(255,255,255,0.95);padding:15px;border-radius:8px;border:2px solid #ddd;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h3 style="margin:0 0 10px 0;color:#333;font-size:16px;">Rede de Voos Brasil</h3>
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
    print(f"✓ Arquivo criado: {out_html}")


def gerar_visualizacoes_graficos(base_path: Path):
    print("\n=== Gerando visualizações: Gráficos e Análises ===")
    csv_adj = base_path / 'data' / 'adjacencias_bairros.csv'
    csv_bairros = base_path / 'data' / 'bairros_recife.csv'
    out_dir = base_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    grafo, vertices, arestas = carregar_adjacencias_set(csv_adj)

    graus = {v: len(neigh) for v, neigh in grafo.items()}

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
        print(f"✓ Arquivo criado: {out_dir / 'grau_bairro_histograma.png'}")

    micror = {}
    with open(csv_bairros, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for header in headers:
            if header.strip():
                micror[header] = []
        for row in reader:
            for i, value in enumerate(row):
                if i < len(headers) and value.strip():
                    nome_regiao = headers[i]
                    bairro = normalizar_nome(value)
                    if nome_regiao in micror:
                        micror[nome_regiao].append(bairro)

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
        print(f"✓ Arquivo criado: {out_dir / 'microrregioes_distancia_heatmap.png'}")

    micror_data = []
    for nome, bairros in micror.items():
        bairros_set = set(bairros) & vertices
        arestas_in = 0
        for a, b in arestas:
            if a in bairros_set and b in bairros_set:
                arestas_in += 1
        ordem = len(bairros_set)
        tamanho = arestas_in
        dens = calcular_densidade(ordem, tamanho)
        micror_data.append({'microrregiao': nome, 'ordem': ordem, 'tamanho': tamanho, 'densidade': dens})

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
        print(f"✓ Arquivo criado: {out_dir / 'piechart_microrregioes.png'}")


def main():
    base_path = Path(__file__).parent.parent
    
    print("="*70)
    print(" GERADOR DE VISUALIZAÇÕES - PROJETO GRAFOS")
    print("="*70)
    
    gerar_caminho_html(base_path)
    gerar_grafo_interativo_bairros(base_path)
    gerar_grafo_voos_interativo(base_path)
    gerar_visualizacoes_graficos(base_path)
    
    print("\n" + "="*70)
    print("✅ TODAS AS VISUALIZAÇÕES FORAM GERADAS COM SUCESSO!")
    print("="*70)
    print(f"\nArquivos salvos em: {base_path / 'out'}")
    print("\nVisualizações HTML:")
    print("  • arvore_percurso.html")
    print("  • grafo_interativo.html")
    print("  • grafo_voos_interativo.html")
    print("\nVisualizações PNG:")
    print("  • grau_bairro_histograma.png")
    print("  • microrregioes_distancia_heatmap.png")
    print("  • piechart_microrregioes.png")
    print()


if __name__ == '__main__':
    main()
