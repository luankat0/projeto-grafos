import json
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter


def load_report(report_path: Path) -> dict:
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_degree_distribution_chart():
    base_path = Path(__file__).parent.parent.parent
    report_path = base_path / 'out' / 'voos_report.json'
    out_path = base_path / 'out'
    
    if not report_path.exists():
        print("Erro: voos_report.json não encontrado!")
        print(f"   Execute primeiro: python src/utils/voos_analysis.py")
        return
    
    report = load_report(report_path)
    
    out_degree_dist = report['dataset']['out_degree']['distribution']
    in_degree_dist = report['dataset']['in_degree']['distribution']
    
    out_degrees = {int(k): v for k, v in out_degree_dist.items()}
    in_degrees = {int(k): v for k, v in in_degree_dist.items()}
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    degrees_out = sorted(out_degrees.keys())
    counts_out = [out_degrees[d] for d in degrees_out]
    
    bars1 = ax1.bar(degrees_out, counts_out, color='#3498db', 
                    alpha=0.8, edgecolor='black', linewidth=1.5, width=0.6)
    
    for bar, count in zip(bars1, counts_out):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_xlabel('Grau de Saída (Out-Degree)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Número de Aeroportos', fontsize=12, fontweight='bold')
    ax1.set_title('Distribuição de Grau de Saída\n(Voos Partindo)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax1.set_axisbelow(True)
    ax1.set_xticks(degrees_out)
    
    avg_out = report['dataset']['out_degree']['avg']
    min_out = report['dataset']['out_degree']['min']
    max_out = report['dataset']['out_degree']['max']
    
    stats_text_out = f"Média: {avg_out:.2f}\nMín: {min_out}  Máx: {max_out}"
    ax1.text(0.02, 0.98, stats_text_out, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    degrees_in = sorted(in_degrees.keys())
    counts_in = [in_degrees[d] for d in degrees_in]
    
    bars2 = ax2.bar(degrees_in, counts_in, color='#e74c3c',
                    alpha=0.8, edgecolor='black', linewidth=1.5, width=0.6)
    
    for bar, count in zip(bars2, counts_in):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_xlabel('Grau de Entrada (In-Degree)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Número de Aeroportos', fontsize=12, fontweight='bold')
    ax2.set_title('Distribuição de Grau de Entrada\n(Voos Chegando)', 
                  fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.set_axisbelow(True)
    ax2.set_xticks(degrees_in)
    
    avg_in = report['dataset']['in_degree']['avg']
    min_in = report['dataset']['in_degree']['min']
    max_in = report['dataset']['in_degree']['max']
    
    stats_text_in = f"Média: {avg_in:.2f}\nMín: {min_in}  Máx: {max_in}"
    ax2.text(0.02, 0.98, stats_text_in, transform=ax2.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#ffcccc', alpha=0.7))
    
    dataset_info = report['dataset']
    fig.suptitle(f'Distribuição de Graus - Rede de Voos Brasil\n' +
                 f'|V| = {dataset_info["vertices"]} aeroportos  |  ' +
                 f'|E| = {dataset_info["edges"]} rotas  |  ' +
                 f'Densidade = {dataset_info["density"]:.2%}',
                 fontsize=13, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    output_file = out_path / 'degree_distribution.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')

    max_out_degree = max(out_degrees.keys())
    hubs_out = [d for d, c in out_degrees.items() if d == max_out_degree]

    plt.close()


if __name__ == '__main__':
    create_degree_distribution_chart()
