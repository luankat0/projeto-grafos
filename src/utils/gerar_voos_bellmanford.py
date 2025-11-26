import csv
from pathlib import Path
from collections import Counter
import random


def main():
    base_path = Path(__file__).parent.parent.parent
    input_csv = base_path / 'data' / 'dataset_parte2' / 'voos_brasil.csv'
    output_csv = base_path / 'data' / 'dataset_parte2' / 'voos_bellmanford.csv'
    
    aeroportos_info = {}
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            aeroporto_origem = row.get('Aeroporto.Origem', '').strip()
            cidade_origem = row.get('Cidade.Origem', '').strip()
            pais_origem = row.get('Pais.Origem', '').strip()
            
            aeroporto_destino = row.get('Aeroporto.Destino', '').strip()
            cidade_destino = row.get('Cidade.Destino', '').strip()
            pais_destino = row.get('Pais.Destino', '').strip()
            
            if aeroporto_origem and cidade_origem:
                key_origem = f"{aeroporto_origem} - {cidade_origem}"
                aeroportos_info[key_origem] = pais_origem
            
            if aeroporto_destino and cidade_destino:
                key_destino = f"{aeroporto_destino} - {cidade_destino}"
                aeroportos_info[key_destino] = pais_destino
    
    aeroportos_lista = sorted(list(aeroportos_info.keys()))
    
    conexoes = []
    conexoes_geradas = set()
    
    for i in range(len(aeroportos_lista) - 1):
        origem = aeroportos_lista[i]
        destino = aeroportos_lista[i + 1]
        conexao_key = (origem, destino)
        
        if conexao_key not in conexoes_geradas:
            conexoes_geradas.add(conexao_key)
            conexoes.append({
                'origem': origem,
                'destino': destino,
                'pais_origem': aeroportos_info[origem],
                'pais_destino': aeroportos_info[destino]
            })
    
    num_conexoes_extras = len(aeroportos_lista) // 3
    
    for _ in range(num_conexoes_extras):
        origem = random.choice(aeroportos_lista)
        
        idx_origem = aeroportos_lista.index(origem)
        opcoes_destino = [a for i, a in enumerate(aeroportos_lista) 
                         if abs(i - idx_origem) > 2 and a != origem]
        
        if opcoes_destino:
            destino = random.choice(opcoes_destino)
            conexao_key = (origem, destino)
            
            if conexao_key not in conexoes_geradas:
                conexoes_geradas.add(conexao_key)
                conexoes.append({
                    'origem': origem,
                    'destino': destino,
                    'pais_origem': aeroportos_info[origem],
                    'pais_destino': aeroportos_info[destino]
                })
    
    num_negativas = max(3, len(conexoes) // 5)
    indices_negativos = random.sample(range(len(conexoes)), min(num_negativas, len(conexoes)))
    
    dados_voos = []
    for i, conexao in enumerate(conexoes):
        if i in indices_negativos:
            voos = random.randint(-80, -10)
        else:
            voos = random.randint(5, 150)
        
        dados_voos.append({
            'aeroporto_origem': conexao['origem'],
            'pais_origem': conexao['pais_origem'],
            'aeroporto_destino': conexao['destino'],
            'pais_destino': conexao['pais_destino'],
            'voos': voos
        })
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['aeroporto_origem', 'pais_origem', 'aeroporto_destino', 'pais_destino', 'voos'])
        writer.writeheader()
        writer.writerows(dados_voos)
    
    print(f"Arquivo criado: {output_csv}")
    print(f"Total de aeroportos: {len(aeroportos_lista)}")
    print(f"Total de conexões: {len(conexoes)}")
    print(f"  - Caminho principal: {len(aeroportos_lista) - 1}")
    print(f"  - Conexões extras: {len(conexoes) - (len(aeroportos_lista) - 1)}")
    print(f"Conexões com voos negativos: {len(indices_negativos)}")
    print(f"\nPrimeiras conexões negativas:")
    for i, idx in enumerate(sorted(indices_negativos)[:5]):
        conexao = dados_voos[idx]
        origem_curto = conexao['aeroporto_origem'].split(' - ')[0]
        destino_curto = conexao['aeroporto_destino'].split(' - ')[0]
        print(f"  {i+1}. {origem_curto} → {destino_curto}: {conexao['voos']} voos")


if __name__ == '__main__':
    main()
