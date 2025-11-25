from pyvis.network import Network
from pathlib import Path
import csv
import os


def _criar_menu_navegacao():
    """Cria o HTML/CSS/JS do menu hamburguer para navegação entre páginas."""
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


def _inserir_menu_em_html(html_content: str, menu_html: str) -> str:
    """Insere o menu de navegação no HTML após a tag <body>."""
    body_pos = html_content.find('<body>')
    if body_pos != -1:
        body_end = html_content.find('>', body_pos) + 1
        return html_content[:body_end] + '\n' + menu_html + html_content[body_end:]
    return html_content


def gerar_grafo_bairros(base_path: Path = None):
    """Gera o grafo HTML simples de todos os bairros de Recife."""
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent
    
    bairros = [
        "Aflitos", "Afogados", "Agua Fria", "Alto Jose Bonifacio", "Alto Jose do Pinho",
        "Alto Santa Teresinha", "Alto do Mandu", "Apipucos", "Areias", "Arruda",
        "Barro", "Beberibe", "Boa Viagem", "Boa Vista", "Bomba do Hemeterio",
        "Bongi", "Brasilia Teimosa", "Brejo da Guabiraba", "Brejo de Beberibe",
        "Cabanga", "Cacote", "Cajueiro", "Campina do Barreto", "Campo Grande",
        "Casa Amarela", "Casa Forte", "Caxanga", "Cidade Universitaria", "Coelhos",
        "Cohab", "Coqueiral", "Cordeiro", "Corrego do Jenipapo", "Curado", "Derby",
        "Dois Irmaos", "Dois Unidos", "Encruzilhada", "Engenho do Meio", "Espinheiro",
        "Estancia", "Fundao", "Gracas", "Guabiraba", "Hipodromo", "Ibura",
        "Ilha Joana Bezerra", "Ilha do Leite", "Ilha do Retiro", "Imbiribeira",
        "Ipsep", "Iputinga", "Jaqueira", "Jardim Sao Paulo", "Jiquia", "Jordao",
        "Linha do Tiro", "Macaxeira", "Madalena", "Mangabeira", "Mangueira",
        "Monteiro", "Morro da Conceicao", "Mustardinha", "Nova Descoberta", "Paissandu",
        "Parnamirim", "Passarinho", "Pau-Ferro", "Peixinhos", "Pina", "Poco",
        "Ponto de Parada", "Porto da Madeira", "Prado", "Recife", "Rosarinho",
        "San Martin", "Sancho", "Santana", "Santo Amaro", "Santo Antonio", "Sao Jose",
        "Sitio dos Pintos", "Soledade", "Tamarineira", "Tejipio", "Torre", "Torreao",
        "Torroes", "Toto", "Varzea", "Vasco da Gama", "Zumbi"
    ]

    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

    for bairro in bairros:
        net.add_node(bairro, label=bairro)

    output_html = base_path / 'out' / 'grafo_bairros.html'
    output_html.parent.mkdir(parents=True, exist_ok=True)

    html_content = net.generate_html()
    menu_html = _criar_menu_navegacao()
    html_final = _inserir_menu_em_html(html_content, menu_html)
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    print(f"Arquivo criado: {output_html}")


def gerar_csv_bairros_microrregiao(base_path: Path = None):
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent
    
    input_csv = base_path / 'data' / 'bairros_recife.csv'
    output_csv = base_path / 'data' / 'bairros_unique.csv'
    
    bairros_data = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        for row in reader:
            for i, bairro in enumerate(row):
                if bairro.strip():
                    microrregiao = headers[i] if i < len(headers) else ''
                    bairros_data.append({
                        'bairro': bairro.strip(),
                        'microrregiao': microrregiao.strip()
                    })
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['bairro', 'microrregiao'])
        writer.writeheader()
        writer.writerows(bairros_data)
    
    print(f"CSV de bairros criado: {output_csv}")


if __name__ == '__main__':
    gerar_grafo_bairros()
    gerar_csv_bairros_microrregiao()
