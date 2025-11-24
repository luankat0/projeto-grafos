import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from graphs.algorithms import bfs


class TestBFS:
    
    def test_grafo_pequeno_niveis_corretos(self):
        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['D', 'E'],
            'D': ['E'],
            'E': []
        }
        
        result = bfs(graph, 'A')
        
        assert result['order'] == ['A', 'B', 'C', 'D', 'E']
        assert result['layers'][0] == ['A']
        assert result['layers'][1] == ['B', 'C']
        assert result['layers'][2] == ['D', 'E']
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 1
        assert result['distances']['C'] == 1
        assert result['distances']['D'] == 2
        assert result['distances']['E'] == 2
    
    def test_grafo_linear(self):
        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['D'],
            'D': []
        }
        
        result = bfs(graph, 'A')
        
        assert result['order'] == ['A', 'B', 'C', 'D']
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 1
        assert result['distances']['C'] == 2
        assert result['distances']['D'] == 3
        assert len(result['layers']) == 4
    
    def test_grafo_com_ciclo(self):
        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['A', 'D'],
            'D': []
        }
        
        result = bfs(graph, 'A')
        
        assert 'A' in result['order']
        assert 'B' in result['order']
        assert 'C' in result['order']
        assert 'D' in result['order']
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 1
        assert result['distances']['C'] == 2
        assert result['distances']['D'] == 3
    
    def test_grafo_desconexo(self):
        graph = {
            'A': ['B'],
            'B': [],
            'C': ['D'],
            'D': []
        }
        
        result = bfs(graph, 'A')
        
        assert 'A' in result['order']
        assert 'B' in result['order']
        assert 'C' not in result['order']
        assert 'D' not in result['order']
    
    def test_vertice_isolado(self):
        graph = {
            'A': []
        }
        
        result = bfs(graph, 'A')
        
        assert result['order'] == ['A']
        assert result['distances']['A'] == 0
        assert len(result['layers']) == 1
    
    def test_vertice_inexistente(self):
        graph = {
            'A': ['B'],
            'B': []
        }
        
        result = bfs(graph, 'C')
        
        assert result['order'] == []
        assert result['layers'] == {}
        assert result['distances'] == {}
    
    def test_grafo_completo(self):
        graph = {
            'A': ['B', 'C', 'D'],
            'B': ['A', 'C', 'D'],
            'C': ['A', 'B', 'D'],
            'D': ['A', 'B', 'C']
        }
        
        result = bfs(graph, 'A')
        
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 1
        assert result['distances']['C'] == 1
        assert result['distances']['D'] == 1
        assert len(result['layers']) == 2
    
    def test_caminho_longo(self):
        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['D'],
            'D': ['E'],
            'E': ['F'],
            'F': []
        }
        
        result = bfs(graph, 'A')
        
        assert len(result['order']) == 6
        assert result['distances']['F'] == 5
        assert len(result['layers']) == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
