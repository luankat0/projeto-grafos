import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from graphs.algorithms import dfs


class TestDFS:
    
    def test_deteccao_ciclo_grafo_com_ciclo(self):
        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['A']
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == True
        assert 'A' in result['order']
        assert 'B' in result['order']
        assert 'C' in result['order']
    
    def test_deteccao_ciclo_grafo_sem_ciclo(self):
        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['E'],
            'D': [],
            'E': []
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == False
        assert len(result['order']) == 5
    
    def test_grafo_linear_sem_ciclo(self):
        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['D'],
            'D': []
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == False
        assert result['order'][0] == 'A'
        assert len(result['order']) == 4
    
    def test_ciclo_autoloop(self):
        graph = {
            'A': ['A']
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == True
    
    def test_ciclo_complexo(self):
        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['D'],
            'D': ['E'],
            'E': ['B']
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == True
    
    def test_arvore_sem_ciclo(self):
        graph = {
            'A': ['B', 'C'],
            'B': ['D', 'E'],
            'C': ['F', 'G'],
            'D': [],
            'E': [],
            'F': [],
            'G': []
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == False
        assert len(result['order']) == 7
    
    def test_ordem_profundidade(self):
        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['E'],
            'D': [],
            'E': []
        }
        
        result = dfs(graph, 'A')
        
        order = result['order']
        assert order[0] == 'A'
        assert order.index('D') < order.index('C')
    
    def test_vertice_inexistente(self):
        graph = {
            'A': ['B'],
            'B': []
        }
        
        result = dfs(graph, 'C')
        
        assert result['order'] == []
        assert result['has_cycle'] == False
    
    def test_grafo_desconexo(self):
        graph = {
            'A': ['B'],
            'B': [],
            'C': ['D'],
            'D': []
        }
        
        result = dfs(graph, 'A')
        
        assert 'A' in result['order']
        assert 'B' in result['order']
        assert 'C' not in result['order']
        assert 'D' not in result['order']
    
    def test_multiplos_ciclos(self):
        graph = {
            'A': ['B'],
            'B': ['C', 'D'],
            'C': ['A'],
            'D': ['E'],
            'E': ['D']
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == True
    
    def test_grafo_diamante(self):
        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['D'],
            'D': []
        }
        
        result = dfs(graph, 'A')
        
        assert result['has_cycle'] == False
        assert len(result['order']) == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
