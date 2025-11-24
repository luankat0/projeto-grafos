import csv
from pathlib import Path


def atribuir_peso(logradouro):
    if not isinstance(logradouro, str):
        return ""
    
    logradouro_limpo = logradouro.strip()
    
    if logradouro_limpo.startswith("R."):
        return 1
    elif logradouro_limpo.startswith("Estr."):
        return 1
    elif logradouro_limpo.startswith("Pte."):
        return 2
    elif logradouro_limpo.startswith("Psa."):
        return 2
    elif logradouro_limpo.startswith("Av."):
        return 3
    elif logradouro_limpo.startswith("Rod. "):
        return 3
    else:
        return ""


def main():
    base_path = Path(__file__).parent.parent.parent
    arquivo_entrada = base_path / 'data' / 'Conexões - adjacencias_bairros.csv'
    arquivo_saida = base_path / 'data' / 'adjacencias_bairros.csv'

    with open(arquivo_entrada, mode='r', encoding='utf-8') as f_entrada:
        leitor_csv = csv.DictReader(f_entrada)
        
        colunas = leitor_csv.fieldnames
        
        if 'peso' not in colunas:
            colunas.append('peso')
            
        linhas_atualizadas = []

        for linha in leitor_csv:
            logradouro_atual = linha.get('logradouro', '')
            
            novo_peso = atribuir_peso(logradouro_atual)
            
            linha['peso'] = novo_peso
            
            linhas_atualizadas.append(linha)

    with open(arquivo_saida, mode='w', encoding='utf-8', newline='') as f_saida:
        escritor_csv = csv.DictWriter(f_saida, fieldnames=colunas)
        
        escritor_csv.writeheader()
        
        escritor_csv.writerows(linhas_atualizadas)

    print(f"Arquivo '{arquivo_saida}' criado")


if __name__ == '__main__':
    main()
