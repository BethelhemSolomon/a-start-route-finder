from __future__ import annotations
import heapq
from typing import Dict, Hashable, List, Tuple

# Graph type alias (adjacency list with costs)
Graph = Dict[Hashable, List[Tuple[Hashable, float]]]

# === A* Algorithm ===
def a_star(graph: Graph, start, goal, heuristic: Dict[Hashable, Dict[Hashable, float]]):
    open = []
    heapq.heappush(open, (heuristic[start][goal], 0, start))  # (f = g+h, g, node)
    closed = set()
    parent ={start:None}
    
    g_score = {node:float('inf') for node in graph}
    g_score[start] = 0
    g_cost = []
    step_counter = 1

    while open:
        f_cost, g, current_node = heapq.heappop(open)

        if current_node == goal:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = parent[current_node]     
            path.reverse()
            return path, g_score[goal], g_cost

        if current_node not in closed:
            closed.add(current_node)
            for neighbor, cost in graph.get(current_node, []):
                if neighbor in closed:
                    continue
                tentative_g = g_score[current_node] + cost
                if tentative_g < g_score.get(neighbor, float('inf')):
                    parent[neighbor] = current_node
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic[neighbor][goal]
                    heapq.heappush(open, (f_score, tentative_g, neighbor))
                    g_cost.append((current_node, neighbor, step_counter))
                    step_counter += 1

    return None, float('inf'), g_cost  # No path found


# === Greedy Best-First Search ===
def greedy_best_first(graph: Graph, start, goal, heuristic: Dict[Hashable, Dict[Hashable, float]]):
    open = [(heuristic[start][goal], start)]  # (h, node)
    closed = set()
    path = {}
    g_cost = []
    step_counter = 1

    while open:
        h_cost, current_node = heapq.heappop(open)

        if current_node == goal:
            path_result = []
            node = current_node
            while node != start:
                path_result.append(node)
                node = path[node]
            path_result.append(start)
            path_result.reverse()
            # Greedy does not accumulate real cost, set total cost as sum of edges traversed
            total_cost = sum(
                cost for u, v, cost in [
                    (u, v, next(c for n, c in graph[u] if n == v))
                    for u, v, _ in g_cost
                ]
            )
            return path_result, total_cost, g_cost

        if current_node not in closed:
            closed.add(current_node)
            for neighbor, cost in graph.get(current_node, []):
                heapq.heappush(open, (heuristic[neighbor][goal], neighbor))
                path[neighbor] = current_node
                g_cost.append((current_node, neighbor, step_counter))
                step_counter += 1

    return None, float('inf'), g_cost  # No path found
