import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from graphs.algorithms import bellman_ford


class TestBellmanFord:
    
    def test_pesos_negativos_sem_ciclo_negativo(self):
        graph = {
            'A': {'B': 5.0, 'C': 2.0},
            'B': {'D': 1.0},
            'C': {'B': -3.0, 'D': 4.0},
            'D': {}
        }
        all_nodes = {'A', 'B', 'C', 'D'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == -1.0
        assert result['distances']['C'] == 2.0
        assert result['distances']['D'] == 0.0
    
    def test_detecta_ciclo_negativo(self):
        graph = {
            'A': {'B': 1.0},
            'B': {'C': 2.0},
            'C': {'A': -5.0}
        }
        all_nodes = {'A', 'B', 'C'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == True
        assert result['negative_cycle'] is not None
        assert len(result['negative_cycle']) >= 2
    
    def test_ciclo_negativo_complexo(self):
        graph = {
            'A': {'B': 2.0},
            'B': {'C': 3.0},
            'C': {'D': 1.0},
            'D': {'B': -8.0}
        }
        all_nodes = {'A', 'B', 'C', 'D'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == True
        assert result['negative_cycle'] is not None
    
    def test_todos_pesos_positivos(self):
        graph = {
            'A': {'B': 4.0, 'C': 2.0},
            'B': {'C': 1.0, 'D': 5.0},
            'C': {'D': 3.0},
            'D': {}
        }
        all_nodes = {'A', 'B', 'C', 'D'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == 4.0
        assert result['distances']['C'] == 2.0
        assert result['distances']['D'] == 5.0
    
    def test_pesos_negativos_sem_ciclo(self):
        graph = {
            'A': {'B': -1.0, 'C': 4.0},
            'B': {'C': 3.0, 'D': 2.0},
            'C': {},
            'D': {'C': -5.0}
        }
        all_nodes = {'A', 'B', 'C', 'D'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == -1.0
        assert result['distances']['C'] == -4.0
        assert result['distances']['D'] == 1.0
    
    def test_grafo_desconexo_com_negativos(self):
        graph = {
            'A': {'B': 2.0},
            'B': {},
            'C': {'D': -3.0},
            'D': {}
        }
        all_nodes = {'A', 'B', 'C', 'D'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == 2.0
        assert result['distances']['C'] == float('inf')
        assert result['distances']['D'] == float('inf')
    
    def test_ciclo_negativo_isolado(self):
        graph = {
            'A': {'B': 1.0},
            'B': {},
            'C': {'D': 2.0},
            'D': {'E': 3.0},
            'E': {'C': -6.0}
        }
        all_nodes = {'A', 'B', 'C', 'D', 'E'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
    
    def test_vertice_isolado(self):
        graph = {
            'A': {},
            'B': {'C': 1.0},
            'C': {}
        }
        all_nodes = {'A', 'B', 'C'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == float('inf')
        assert result['distances']['C'] == float('inf')
    
    def test_multiplos_caminhos_negativos(self):
        graph = {
            'A': {'B': 5.0, 'C': 2.0},
            'B': {'D': 1.0},
            'C': {'B': -4.0, 'D': 3.0},
            'D': {'E': 2.0},
            'E': {}
        }
        all_nodes = {'A', 'B', 'C', 'D', 'E'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['B'] == -2.0
        assert result['distances']['D'] == -1.0
        assert result['distances']['E'] == 1.0
    
    def test_caminho_com_peso_zero(self):
        graph = {
            'A': {'B': 0.0},
            'B': {'C': -5.0},
            'C': {'D': 3.0},
            'D': {}
        }
        all_nodes = {'A', 'B', 'C', 'D'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == False
        assert result['distances']['A'] == 0.0
        assert result['distances']['B'] == 0.0
        assert result['distances']['C'] == -5.0
        assert result['distances']['D'] == -2.0
    
    def test_ciclo_negativo_autoloop(self):
        graph = {
            'A': {'A': -1.0, 'B': 1.0},
            'B': {}
        }
        all_nodes = {'A', 'B'}
        
        result = bellman_ford(graph, 'A', all_nodes)
        
        assert result['has_negative_cycle'] == True
    
    def test_vertice_inexistente(self):
        graph = {
            'A': {'B': 1.0},
            'B': {}
        }
        all_nodes = {'A', 'B'}
        
        result = bellman_ford(graph, 'X', all_nodes)
        
        assert result['distances'] == {}
        assert result['has_negative_cycle'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
