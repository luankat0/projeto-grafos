import heapq
from collections import deque, defaultdict
from typing import Dict, List, Tuple, Set


def bfs(graph: Dict[str, List[str]], start: str) -> Dict:
    if start not in graph:
        return {'order': [], 'layers': {}, 'distances': {}}
    
    visited = {start}
    queue = deque([(start, 0)])
    order = [start]
    layers = defaultdict(list)
    distances = {start: 0}
    
    layers[0].append(start)
    
    while queue:
        node, layer = queue.popleft()
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, layer + 1))
                order.append(neighbor)
                layers[layer + 1].append(neighbor)
                distances[neighbor] = layer + 1
    
    return {
        'order': order,
        'layers': dict(layers),
        'distances': distances
    }


def dfs(graph: Dict[str, List[str]], start: str) -> Dict:
    if start not in graph:
        return {'order': [], 'has_cycle': False}
    
    visited = set()
    order = []
    has_cycle = [False]
    in_stack = set()
    
    def dfs_visit(node):
        visited.add(node)
        in_stack.add(node)
        order.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs_visit(neighbor)
            elif neighbor in in_stack:
                has_cycle[0] = True
        
        in_stack.remove(node)
    
    dfs_visit(start)
    
    return {
        'order': order,
        'has_cycle': has_cycle[0]
    }


def dijkstra(graph: Dict[str, Dict[str, float]], start: str, end: str = None) -> Dict:
    if start not in graph:
        return {'distances': {}, 'path_to_end': None, 'cost': float('inf')}
    
    distances = {start: 0.0}
    parents = {start: None}
    pq = [(0.0, start)]
    visited = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if end and current == end:
            break
        
        if current_dist > distances.get(current, float('inf')):
            continue
        
        for neighbor, weight in graph.get(current, {}).items():
            distance = current_dist + weight
            
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                parents[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))
    
    result = {
        'distances': distances,
        'path_to_end': None,
        'cost': float('inf')
    }

    if end and end in parents:
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = parents[node]
        path.reverse()
        result['path_to_end'] = path
        result['cost'] = distances[end]
    
    return result


def bellman_ford(graph: Dict[str, Dict[str, float]], start: str, 
                  all_nodes: Set[str]) -> Dict:
    if start not in all_nodes:
        return {'distances': {}, 'has_negative_cycle': False, 'negative_cycle': None}
    
    distances = {node: float('inf') for node in all_nodes}
    distances[start] = 0.0
    parents = {node: None for node in all_nodes}
    
    for _ in range(len(all_nodes) - 1):
        for node in graph:
            if distances[node] == float('inf'):
                continue
            
            for neighbor, weight in graph.get(node, {}).items():
                if distances[node] + weight < distances[neighbor]:
                    distances[neighbor] = distances[node] + weight
                    parents[neighbor] = node
    
    has_negative_cycle = False
    negative_cycle = None
    
    for node in graph:
        if distances[node] == float('inf'):
            continue
        
        for neighbor, weight in graph.get(node, {}).items():
            if distances[node] + weight < distances[neighbor]:
                has_negative_cycle = True
                
                cycle_node = neighbor
                visited = set()
                while cycle_node not in visited and cycle_node is not None:
                    visited.add(cycle_node)
                    cycle_node = parents.get(cycle_node)
                
                if cycle_node:
                    cycle = [cycle_node]
                    current = parents[cycle_node]
                    while current != cycle_node and current is not None:
                        cycle.append(current)
                        current = parents.get(current)
                    cycle.reverse()
                    negative_cycle = cycle
                break
        
        if has_negative_cycle:
            break
    
    return {
        'distances': distances,
        'has_negative_cycle': has_negative_cycle,
        'negative_cycle': negative_cycle
    }
