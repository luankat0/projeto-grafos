import csv
from pathlib import Path
from collections import defaultdict

def calculate_grau(csv_path):
    conexoes = defaultdict(set)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for linha in reader:
            origem = linha['bairro_origem'].strip()
            destino = linha['bairro_destino'].strip()
            
            conexoes[origem].add(destino)
            conexoes[destino].add(origem)
    
    grau = {}
    for bairro, vizinhos in conexoes.items():
        grau[bairro] = len(vizinhos)
    
    return grau

def main():
    base_path = Path(__file__).parent.parent.parent
    input_path = base_path / "data" / "adjacencias_bairros.csv"
    output_path = base_path / "out" / "graus.csv"
    
    grau = calculate_grau(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['bairro', 'grau'])
        for bairro in sorted(grau.keys()):
            writer.writerow([bairro, grau[bairro]])

main()