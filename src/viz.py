import csv
import json
import math
import unicodedata
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))
from graphs.algorithms import dijkstra as dijkstra_base, bellman_ford
from graphs.io import gerar_grafo_bairros

from pyvis.network import Network
import matplotlib.pyplot as plt


def criar_menu_navegacao():
    return """
<style>
.menu-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10001;
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border: none;
    border-radius: 8px;
    width: 50px;
    height: 50px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 5px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}
.menu-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
}
.menu-btn span {
    display: block;
    width: 25px;
    height: 3px;
    background: white;
    border-radius: 2px;
    transition: all 0.3s ease;
}
.menu-btn.active span:nth-child(1) {
    transform: rotate(45deg) translate(7px, 7px);
}
.menu-btn.active span:nth-child(2) {
    opacity: 0;
}
.menu-btn.active span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -7px);
}
.menu-sidebar {
    position: fixed;
    top: 0;
    right: -300px;
    width: 300px;
    height: 100vh;
    background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
    box-shadow: -4px 0 20px rgba(0,0,0,0.4);
    z-index: 10000;
    transition: right 0.4s ease;
    overflow-y: auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.menu-sidebar.active {
    right: 0;
}
.menu-header {
    padding: 30px 20px;
    color: white;
    border-bottom: 2px solid rgba(255,255,255,0.2);
}
.menu-header h2 {
    margin: 0;
    font-size: 22px;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
.menu-header p {
    margin: 8px 0 0 0;
    font-size: 13px;
    opacity: 0.9;
}
.menu-links {
    padding: 20px 0;
}
.menu-link {
    display: flex;
    align-items: center;
    padding: 15px 25px;
    color: white;
    text-decoration: none;
    transition: all 0.3s ease;
    border-left: 4px solid transparent;
    gap: 12px;
    font-size: 15px;
}
.menu-link:hover {
    background: rgba(255,255,255,0.2);
    border-left-color: white;
    padding-left: 30px;
}
.menu-link.active {
    background: rgba(255,255,255,0.25);
    border-left-color: white;
    font-weight: bold;
}
.menu-link .icon {
    font-size: 20px;
    width: 24px;
    text-align: center;
}
.menu-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 9999;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}
.menu-overlay.active {
    opacity: 1;
    visibility: visible;
}
</style>

<button class="menu-btn" id="menuBtn">
    <span></span>
    <span></span>
    <span></span>
</button>

<div class="menu-overlay" id="menuOverlay"></div>

<nav class="menu-sidebar" id="menuSidebar">
    <div class="menu-header">
        <h2>📊 Projeto Grafos</h2>
        <p>Visualizações Interativas</p>
    </div>
    <div class="menu-links">
        <a href="grafo_bairros.html" class="menu-link">
            <span class="icon">🗺️</span>
            <span>Grafo de Bairros</span>
        </a>
        <a href="arvore_percurso.html" class="menu-link">
            <span class="icon">🌳</span>
            <span>Árvore de Percurso</span>
        </a>
        <a href="grafo_interativo.html" class="menu-link">
            <span class="icon">🏘️</span>
            <span>Grafo Interativo Bairros</span>
        </a>
        <a href="grafo_voos_interativo.html" class="menu-link">
            <span class="icon">✈️</span>
            <span>Grafo de Voos</span>
        </a>
        <a href="caminho_bellmanford.html" class="menu-link">
            <span class="icon">🔄</span>
            <span>Caminho Bellman-Ford</span>
        </a>
    </div>
</nav>

<script>
(function() {
    const menuBtn = document.getElementById('menuBtn');
    const menuSidebar = document.getElementById('menuSidebar');
    const menuOverlay = document.getElementById('menuOverlay');
    
    function toggleMenu() {
        menuBtn.classList.toggle('active');
        menuSidebar.classList.toggle('active');
        menuOverlay.classList.toggle('active');
    }
    
    menuBtn.addEventListener('click', toggleMenu);
    menuOverlay.addEventListener('click', toggleMenu);
    
    // Destacar página atual
    const currentPage = window.location.pathname.split('/').pop();
    document.querySelectorAll('.menu-link').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
    
    // Fechar menu ao clicar em um link
    document.querySelectorAll('.menu-link').forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(toggleMenu, 200);
        });
    });
})();
</script>
"""


def inserir_menu_em_html(html_content: str, menu_html: str) -> str:
    body_pos = html_content.find('<body>')
    if body_pos != -1:
        body_end = html_content.find('>', body_pos) + 1
        return html_content[:body_end] + '\n' + menu_html + html_content[body_end:]
    return html_content


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
    csv_path = base_path / 'data' / 'adjacencias_bairros.csv'
    out_html = base_path / 'out' / 'arvore_percurso.html'

    origem = 'Nova Descoberta'
    destino = 'Boa Viagem(Setubal)'

    try:
        adj = gerar_grafo_adjacencias(csv_path)
    except Exception as e:
        return

    if origem not in adj or destino not in adj:
        return

    custo, caminho = dijkstra_wrapper(adj, origem, destino)
    if not caminho:
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
    
    html_content = net.generate_html()
    menu_html = criar_menu_navegacao()
    html_final = inserir_menu_em_html(html_content, menu_html)
    
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    print(f"Arquivo criado: {out_html}")


def gerar_grafo_interativo_bairros(base_path: Path):
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

    menu_html = criar_menu_navegacao()
    html = inserir_menu_em_html(html, menu_html)

    out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Arquivo criado: {out_html}")


def gerar_grafo_voos_interativo(base_path: Path):
    csv_voos = base_path / 'data' / 'dataset_parte2' / 'voos_brasil.csv'
    out_html = base_path / 'out' / 'grafo_voos_interativo.html'
    
    adj, vertices = carregar_voos(csv_voos)
    
    grau_saida = {v: len(adj.get(v, {})) for v in vertices}
    grau_entrada = {v: 0 for v in vertices}
    for origem, destinos in adj.items():
        for destino in destinos:
            grau_entrada[destino] += 1
    
    tamanho_fixo = 25
    cores_pais = {'Estados Unidos': '#FF6B6B', 'Brasil': '#4ECDC4'}
    
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black',
                  notebook=False, directed=True)
    
    for node in sorted(vertices):
        pais = 'Estados Unidos' if 'Miami' in node else 'Brasil'
        grau_total = grau_saida[node] + grau_entrada[node]
        node_color = cores_pais.get(pais, '#97C2FC')
        nome_curto = node.split(',')[0] if ',' in node else node
        nome_curto = nome_curto.replace(' - ', '\n')
        title = (f'{node}\nPaís: {pais}\n'
                f'Grau Total: {grau_total}\n'
                f'Grau Entrada: {grau_entrada[node]}\n'
                f'Grau Saída: {grau_saida[node]}')
        net.add_node(node, label=nome_curto, title=title, color=node_color,
                    size=tamanho_fixo, font={'size': 12, 'color': 'black'})
    
    for origem, destinos in adj.items():
        for destino, peso in destinos.items():
            width = 1 + (peso / 5)
            title_edge = f'{origem} → {destino}\nVoos: {int(peso)}'
            net.add_edge(origem, destino, value=peso, title=title_edge,
                        color='#95a5a6', width=width, arrows='to')
    
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": -15000,
                "centralGravity": 0.1,
                "springLength": 400,
                "springConstant": 0.02,
                "damping": 0.15,
                "avoidOverlap": 0.5
            },
            "stabilization": {"enabled": true, "iterations": 2000, "updateInterval": 25}
        },
        "nodes": {"font": {"size": 14, "face": "arial"}, "borderWidth": 2, "shadow": true},
        "edges": {"smooth": {"enabled": true, "type": "continuous"}, "shadow": false}
    }
    """)
    
    html = net.generate_html()
    num_vertices = len(vertices)
    num_arestas = sum(len(destinos) for destinos in adj.values())
    total_voos = sum(sum(destinos.values()) for destinos in adj.values())
    
    legenda_html = f"""
<div style="position:fixed;top:10px;left:10px;z-index:999;background:rgba(255,255,255,0.95);padding:15px;border-radius:8px;border:2px solid #ddd;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h3 style="margin:0 0 10px 0;color:#333;font-size:16px;">Rede de Voos - Aeroportos</h3>
    <div style="border-top:1px solid #ddd;padding-top:10px;font-size:12px;">
        <div style="margin:6px 0;">
            <strong>Estatísticas:</strong>
        </div>
        <div style="margin:4px 0;">
            • Aeroportos: {num_vertices}
        </div>
        <div style="margin:4px 0;">
            • Rotas: {num_arestas}
        </div>
        <div style="margin:4px 0;">
            • Total de Voos: {int(total_voos)}
        </div>
        <div style="margin-top:10px;padding-top:10px;border-top:1px solid #ddd;">
            <div style="display:flex;align-items:center;margin:4px 0;">
                <span style="width:20px;height:20px;background:#FF6B6B;border-radius:50%;margin-right:10px;border:2px solid #333;"></span>
                <span>Miami (EUA)</span>
            </div>
            <div style="display:flex;align-items:center;margin:4px 0;">
                <span style="width:20px;height:20px;background:#4ECDC4;border-radius:50%;margin-right:10px;border:2px solid #333;"></span>
                <span>Aeroportos Brasil</span>
            </div>
        </div>
        <div style="margin-top:10px;font-size:10px;color:#666;">
            * Largura da aresta = quantidade de voos
        </div>
    </div>
</div>
"""
    
    insert_at = html.find('<body>')
    if insert_at != -1:
        insert_at_end = html.find('\n', insert_at) + 1
        html = html[:insert_at_end] + legenda_html + html[insert_at_end:]
    
    menu_html = criar_menu_navegacao()
    html = inserir_menu_em_html(html, menu_html)
    
    out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Arquivo criado: {out_html}")


def gerar_visualizacoes_graficos(base_path: Path):
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


def gerar_grafico_voos_por_cidade(base_path: Path):
    csv_voos = base_path / 'data' / 'dataset_parte2' / 'voos_brasil.csv'
    out_dir = base_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    contagem_voos = {}
    
    with open(csv_voos, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cidade_origem = row.get('Cidade.Origem', '').strip()
            cidade_destino = row.get('Cidade.Destino', '').strip()
            
            if cidade_origem:
                contagem_voos[cidade_origem] = contagem_voos.get(cidade_origem, 0) + 1
            if cidade_destino:
                contagem_voos[cidade_destino] = contagem_voos.get(cidade_destino, 0) + 1
    
    cidades_ordenadas = sorted(contagem_voos.items(), key=lambda x: x[1], reverse=True)
    cidades = [c[0] for c in cidades_ordenadas]
    voos = [c[1] for c in cidades_ordenadas]
    
    plt.figure(figsize=(14, 8))
    plt.bar(range(len(cidades)), voos, color='#4ECDC4', edgecolor='black')
    plt.xlabel('Cidade', fontsize=12)
    plt.ylabel('Quantidade de Voos', fontsize=12)
    plt.title('Quantidade de Voos por Cidade', fontsize=14, fontweight='bold')
    plt.xticks(range(len(cidades)), cidades, rotation=90, ha='right', fontsize=9)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / 'voos_por_cidade.png', dpi=150)
    plt.close()
    
    print(f"Arquivo criado: {out_dir / 'voos_por_cidade.png'}")


def gerar_caminho_bellmanford_html(base_path: Path):
    csv_bellmanford = base_path / 'data' / 'dataset_parte2' / 'voos_bellmanford.csv'
    out_html = base_path / 'out' / 'caminho_bellmanford.html'
    
    grafo = {}
    aeroportos = set()
    info_aeroportos = {}
    arestas_negativas = []
    
    with open(csv_bellmanford, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origem = row.get('aeroporto_origem', '').strip()
            destino = row.get('aeroporto_destino', '').strip()
            pais_origem = row.get('pais_origem', '').strip()
            pais_destino = row.get('pais_destino', '').strip()
            voos = float(row.get('voos', 0))
            
            if origem and destino:
                aeroportos.add(origem)
                aeroportos.add(destino)
                info_aeroportos[origem] = pais_origem
                info_aeroportos[destino] = pais_destino
                
                grafo.setdefault(origem, {})[destino] = voos
                
                if voos < 0:
                    arestas_negativas.append((origem, destino, voos))
    
    if not grafo or len(aeroportos) < 2:
        print("Grafo insuficiente para Bellman-Ford")
        return
    
    aeroportos_lista = sorted(list(aeroportos))
    origem = aeroportos_lista[0]
    
    resultado = bellman_ford(grafo, origem, aeroportos)
    
    if resultado['has_negative_cycle']:
        print(f"⚠️  Ciclo negativo detectado no grafo!")
        if resultado['negative_cycle']:
            caminho = resultado['negative_cycle']
            titulo = f"Ciclo Negativo Detectado"
        else:
            caminho = [origem]
            titulo = "Ciclo Negativo (caminho não recuperável)"
    else:
        distancias = resultado['distances']
        aeroportos_alcancaveis = [a for a in aeroportos_lista if distancias[a] != float('inf')]
        
        if len(aeroportos_alcancaveis) > 1:
            destino = max(aeroportos_alcancaveis, key=lambda a: abs(distancias[a]))
            
            parents = {}
            for node in aeroportos:
                parents[node] = None
            
            distances_calc = {node: float('inf') for node in aeroportos}
            distances_calc[origem] = 0.0
            
            for _ in range(len(aeroportos) - 1):
                for node in grafo:
                    if distances_calc[node] == float('inf'):
                        continue
                    for neighbor, weight in grafo.get(node, {}).items():
                        if distances_calc[node] + weight < distances_calc[neighbor]:
                            distances_calc[neighbor] = distances_calc[node] + weight
                            parents[neighbor] = node
            
            caminho = []
            current = destino
            visited = set()
            while current is not None and current not in visited:
                caminho.append(current)
                visited.add(current)
                current = parents.get(current)
            caminho.reverse()
            
            if not caminho or caminho[0] != origem:
                caminho = [origem, destino] if destino in grafo.get(origem, {}) else [origem]
            
            custo_total = distances_calc.get(destino, 0)
            titulo = f"Bellman-Ford: {origem.split(' - ')[0]} → {destino.split(' - ')[0]} (Custo: {custo_total:.1f})"
        else:
            caminho = [origem]
            titulo = f"Bellman-Ford: Apenas origem alcançável"
    
    net = Network(height='800px', width='100%', directed=True, bgcolor='#ffffff')
    
    for i, node in enumerate(caminho):
        pais = info_aeroportos.get(node, 'Desconhecido')
        nome_curto = node.split(' - ')[0]
        
        if i == 0:
            color = '#2ecc71'
            size = 35
        elif i == len(caminho) - 1:
            color = '#3498db'
            size = 35
        else:
            color = '#95a5a6'
            size = 25
        
        title = f'{node}\nPaís: {pais}'
        net.add_node(node, label=nome_curto, color=color, size=size, 
                    title=title, font={'size': 14, 'color': 'black'})
    
    for i in range(len(caminho) - 1):
        origem_edge = caminho[i]
        destino_edge = caminho[i + 1]
        peso = grafo.get(origem_edge, {}).get(destino_edge, 0)
        
        if peso < 0:
            cor_aresta = '#e74c3c'
            width = 4
        else:
            cor_aresta = '#34495e'
            width = 2
        
        net.add_edge(origem_edge, destino_edge, value=abs(peso), 
                    title=f'Voos: {int(peso)}', color=cor_aresta, 
                    arrows='to', width=width)
    
    net.toggle_physics(False)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    
    html_content = net.generate_html()
    
    num_arestas_negativas = len(arestas_negativas)
    
    legenda = f"""
<div style="position:fixed;top:10px;left:10px;z-index:999;background:rgba(255,255,255,0.95);padding:15px;border-radius:8px;border:2px solid #ddd;box-shadow:0 4px 8px rgba(0,0,0,0.2);">
    <h3 style="margin:0 0 10px 0;color:#333;font-size:16px;border-bottom:2px solid #ddd;padding-bottom:8px;">{titulo}</h3>
    <div style="font-size:12px;">
        <div style="margin:8px 0;">
            <strong>Legenda dos Nós:</strong>
        </div>
        <div style="margin:5px 0;display:flex;align-items:center;">
            <span style="display:inline-block;width:18px;height:18px;background:#2ecc71;border-radius:50%;margin-right:8px;border:2px solid #27ae60;"></span>
            <span>Origem</span>
        </div>
        <div style="margin:5px 0;display:flex;align-items:center;">
            <span style="display:inline-block;width:18px;height:18px;background:#3498db;border-radius:50%;margin-right:8px;border:2px solid #2980b9;"></span>
            <span>Destino</span>
        </div>
        <div style="margin:5px 0;display:flex;align-items:center;">
            <span style="display:inline-block;width:18px;height:18px;background:#95a5a6;border-radius:50%;margin-right:8px;border:2px solid #7f8c8d;"></span>
            <span>Caminho intermediário</span>
        </div>
        <div style="margin-top:12px;padding-top:8px;border-top:1px solid #ddd;">
            <strong>Legenda das Arestas:</strong>
        </div>
        <div style="margin:5px 0;display:flex;align-items:center;">
            <span style="display:inline-block;width:30px;height:3px;background:#e74c3c;margin-right:8px;"></span>
            <span>Peso negativo (voos negativos)</span>
        </div>
        <div style="margin:5px 0;display:flex;align-items:center;">
            <span style="display:inline-block;width:30px;height:3px;background:#34495e;margin-right:8px;"></span>
            <span>Peso positivo (voos normais)</span>
        </div>
        <div style="margin-top:12px;padding-top:8px;border-top:1px solid #ddd;">
            <strong>Estatísticas:</strong>
        </div>
        <div style="margin:4px 0;font-size:11px;">
            • Algoritmo: <strong>Bellman-Ford</strong>
        </div>
        <div style="margin:4px 0;font-size:11px;">
            • Aeroportos no grafo: <strong>{len(aeroportos)}</strong>
        </div>
        <div style="margin:4px 0;font-size:11px;">
            • Aeroportos no caminho: <strong>{len(caminho)}</strong>
        </div>
        <div style="margin:4px 0;font-size:11px;">
            • Arestas negativas: <strong>{num_arestas_negativas}</strong>
        </div>
        <div style="margin:4px 0;font-size:11px;">
            • Ciclo negativo: <strong>{'Sim' if resultado['has_negative_cycle'] else 'Não'}</strong>
        </div>
    </div>
</div>
"""
    
    body_pos = html_content.find('<body>')
    if body_pos != -1:
        insert_at_end = html_content.find('\n', body_pos) + 1
        html_content = html_content[:insert_at_end] + legenda + html_content[insert_at_end:]
    
    menu_html = criar_menu_navegacao()
    html_final = inserir_menu_em_html(html_content, menu_html)
    
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    print(f"Arquivo criado: {out_html}")
    if resultado['has_negative_cycle']:
        print(f"⚠️  AVISO: Ciclo negativo detectado no grafo!")


def main():
    base_path = Path(__file__).parent.parent
    
    gerar_grafo_bairros(base_path)
    gerar_caminho_html(base_path)
    gerar_grafo_interativo_bairros(base_path)
    gerar_grafo_voos_interativo(base_path)
    gerar_visualizacoes_graficos(base_path)
    gerar_grafico_voos_por_cidade(base_path)
    gerar_caminho_bellmanford_html(base_path)


if __name__ == '__main__':
    main()
