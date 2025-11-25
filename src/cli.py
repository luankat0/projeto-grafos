import sys
from pathlib import Path
import subprocess


def executar_script(script_path: Path, descricao: str):
    try:
        resultado = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent
        )
        
        if resultado.returncode == 0:
            return True
        else:
            print(f"Falhou com código {resultado.returncode}")
            return False
            
    except Exception as e:
        print(f"Erro ao executar: {str(e)}")
        return False


def main():
    base_path = Path(__file__).parent
    
    scripts = [
        (base_path / "graphs" / "io.py", "Gerar grafo de bairros e CSV de microrregiões"),
        (base_path / "utils" / "peso.py", "Atribuir pesos às conexões"),
        (base_path / "utils" / "calcular_graus.py", "Calcular graus dos bairros"),
        (base_path / "utils" / "calcular_metricas.py", "Calcular métricas do grafo"),
        (base_path / "utils" / "calcular_distancias.py", "Calcular distâncias com Dijkstra"),
        (base_path / "utils" / "voos_analise.py", "Analisar rede de voos"),
        (base_path / "viz.py", "Gerar visualizações interativas"),
    ]
    
    sucessos = 0
    falhas = 0
    
    for script_path, descricao in scripts:
        if not script_path.exists():
            falhas += 1
            continue
        
        if executar_script(script_path, descricao):
            sucessos += 1
        else:
            falhas += 1
    
    print(f"Scripts executados com sucesso: {sucessos}")
    print(f"Scripts com falhas: {falhas}")

    
    if falhas == 0:
        print("\nTodos os scripts foram executados com sucesso, arquivos gerados na pasta 'out'")
    else:
        print(f"\n{falhas} scripts falharam.")
    
    return 0 if falhas == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
