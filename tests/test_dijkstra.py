import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.voos_analysis import dijkstra


class TestDijkstra:
    
    def test_caminho_simples_correto(self):
        graph = {
            'A': {'B': 1.0, 'C': 4.0},
            'B': {'C': 2.0, 'D': 5.0},
            'C': {'D': 1.0},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == 4.0
        assert result['path_to_end'] == ['A', 'B', 'C', 'D']
    
    def test_caminho_direto_vs_indireto(self):
        graph = {
            'A': {'B': 10.0, 'C': 3.0},
            'B': {'D': 2.0},
            'C': {'B': 1.0, 'D': 8.0},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == 6.0
        assert result['path_to_end'] == ['A', 'C', 'B', 'D']
    
    def test_todos_pesos_positivos(self):
        graph = {
            'A': {'B': 2.5, 'C': 1.0},
            'B': {'D': 3.5},
            'C': {'D': 4.0},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == 5.0
        assert result['path_to_end'][0] == 'A'
        assert result['path_to_end'][-1] == 'D'
    
    def test_pesos_zero(self):
        graph = {
            'A': {'B': 0.0, 'C': 5.0},
            'B': {'D': 0.0},
            'C': {'D': 1.0},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == 0.0
        assert result['path_to_end'] == ['A', 'B', 'D']
    
    def test_grafo_com_peso_negativo_deve_funcionar(self):
        graph = {
            'A': {'B': 5.0},
            'B': {'C': -2.0},
            'C': {}
        }
        
        result = dijkstra(graph, 'A', 'C')
        
        assert result['path_to_end'] == ['A', 'B', 'C']
        assert result['cost'] == 3.0
    
    def test_destino_inalcancavel(self):
        graph = {
            'A': {'B': 1.0},
            'B': {},
            'C': {'D': 1.0},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == float('inf')
        assert result['path_to_end'] is None
    
    def test_origem_igual_destino(self):
        graph = {
            'A': {'B': 1.0},
            'B': {}
        }
        
        result = dijkstra(graph, 'A', 'A')
        
        assert result['cost'] == 0.0
        assert result['path_to_end'] == ['A']
    
    def test_multiplos_caminhos_escolhe_menor(self):
        graph = {
            'A': {'B': 2.0, 'C': 5.0},
            'B': {'D': 3.0},
            'C': {'D': 1.0},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == 5.0
        assert result['path_to_end'] == ['A', 'B', 'D']
    
    def test_grafo_denso(self):
        graph = {
            'A': {'B': 4.0, 'C': 2.0},
            'B': {'C': 1.0, 'D': 5.0},
            'C': {'B': 1.0, 'D': 8.0, 'E': 10.0},
            'D': {'E': 2.0},
            'E': {}
        }
        
        result = dijkstra(graph, 'A', 'E')
        
        assert result['cost'] == 10.0
        assert 'A' in result['path_to_end']
        assert 'E' in result['path_to_end']
    
    def test_sem_destino_calcula_todos(self):
        graph = {
            'A': {'B': 1.0, 'C': 4.0},
            'B': {'C': 2.0},
            'C': {}
        }
        
        result = dijkstra(graph, 'A')
        
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == 1.0
        assert result['distances']['C'] == 3.0
    
    def test_vertice_inexistente(self):
        graph = {
            'A': {'B': 1.0},
            'B': {}
        }
        
        result = dijkstra(graph, 'X', 'B')
        
        assert result['distances'] == {}
        assert result['cost'] == float('inf')
    
    def test_pesos_decimais_precisao(self):
        graph = {
            'A': {'B': 0.1, 'C': 0.3},
            'B': {'D': 0.2},
            'C': {'D': 0.1},
            'D': {}
        }
        
        result = dijkstra(graph, 'A', 'D')
        
        assert result['cost'] == pytest.approx(0.3, rel=1e-9)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
