from __future__ import annotations
import pandas as pd
import folium
import networkx as nx

from typing import Dict, Hashable, List, Tuple
from .data_loader import load_dataset


def visualize_on_map(df: pd.DataFrame, path: List[str], visited_edges: List[Tuple[str, str, int]], city_coords: Dict[str, Tuple[float, float]]):
    """Visualize nodes and edges on a folium map.

    df is expected to have lowercase `latitude` and `longitude` columns.
    """
    avg_lat = df['latitude'].mean()
    avg_lon = df['longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    # Draw all edges (if provided via city_coords) as gray
    # Note: original code assumed an edges list; caller can pass visited_edges and path
    if city_coords:
        nodes = list(city_coords.keys())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                origin = nodes[i]
                destination = nodes[j]
                origin_coords = city_coords[origin]
                dest_coords = city_coords[destination]
                folium.PolyLine([origin_coords, dest_coords], color='gray', weight=1.5, opacity=0.5).add_to(m)

    if visited_edges:
        for edge in visited_edges:
            origin, destination, step = edge
            origin_coords = city_coords[origin]
            dest_coords = city_coords[destination]
            folium.PolyLine([origin_coords, dest_coords], color='blue', weight=2, opacity=0.8).add_to(m)
            mid_point = [(origin_coords[0] + dest_coords[0]) / 2, (origin_coords[1] + dest_coords[1]) / 2]
            folium.Marker(mid_point, icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: blue;">{step}</div>')).add_to(m)

    if path:
        path_coords = [city_coords[city] for city in path]
        folium.PolyLine(path_coords, color='red', weight=4, opacity=0.8).add_to(m)

    for city, coords in city_coords.items():
        folium.Marker(location=coords, popup=city).add_to(m)

    return m


# Load nodes and build a NetworkX graph where edge weights are distances (km)
nodes = load_dataset()


def load_edges(path: str = './Mock_Edges.xlsx') -> pd.DataFrame:
    """Load edge weights from an Excel file and normalize column names.

    Expected columns (case-insensitive): origin/destination or node1/node2 and weight/cost/distance.
    Returns a DataFrame with columns: `origin`, `destination`, `weight`.
    """
    try:
        df_e = pd.read_excel(path)
    except FileNotFoundError:
        return None

    df_e.columns = [c.strip().lower() for c in df_e.columns]

    # normalize synonyms
    mappings = {}
    if 'origin' in df_e.columns and 'destination' in df_e.columns:
        mappings.update({'origin': 'origin', 'destination': 'destination'})
    elif 'from' in df_e.columns and 'to' in df_e.columns:
        mappings.update({'from': 'origin', 'to': 'destination'})
    elif 'node1' in df_e.columns and 'node2' in df_e.columns:
        mappings.update({'node1': 'origin', 'node2': 'destination'})

    if 'weight' in df_e.columns:
        mappings['weight'] = 'weight'


    if mappings:
        df_e = df_e.rename(columns=mappings)

    required = {'origin', 'destination', 'weight'}
    if not required.issubset(set(df_e.columns)):
        # If missing expected columns, return None to signal caller to fallback
        return None

    df_e['origin'] = df_e['origin'].astype(str).str.strip()
    df_e['destination'] = df_e['destination'].astype(str).str.strip()
    df_e['weight'] = pd.to_numeric(df_e['weight'], errors='coerce')
    df_e = df_e.dropna(subset=['weight'])
    
    return df_e


Graph = nx.Graph()
edges = []

# build city_coords for visualization and algorithms
city_coords: Dict[str, Tuple[float, float]] = {}
for _, row in nodes.iterrows():
    node_id = str(row['node']).strip()
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    Graph.add_node(node_id, lat=lat, lon=lon)
    city_coords[node_id] = (lat, lon)

# Load edges from provided Mock_Edges.xlsx if present
edges_df = load_edges()
if edges_df is not None:
    # build graph from provided weights
    for _, row in edges_df.iterrows():
        u = str(row['origin']).strip()
        v = str(row['destination']).strip()
        w = float(row['weight'])
        # only add nodes that exist in nodes list
        if u not in city_coords or v not in city_coords:
            continue
        Graph.add_edge(u, v, weight=w)
        edges.append([u, v, w])
else:
    # fallback: compute straight-line (haversine) distances if no edges file
    from .heuristic import haversine

    node_rows = list(nodes.itertuples(index=False))
    for i in range(len(node_rows)):
        a = node_rows[i]
        a_node = str(getattr(a, 'node')).strip()
        a_lat = float(getattr(a, 'latitude'))
        a_lon = float(getattr(a, 'longitude'))
        for j in range(i + 1, len(node_rows)):
            b = node_rows[j]
            b_node = str(getattr(b, 'node')).strip()
            b_lat = float(getattr(b, 'latitude'))
            b_lon = float(getattr(b, 'longitude'))
            cost = haversine(a_lat, a_lon, b_lat, b_lon)
            Graph.add_edge(a_node, b_node, weight=cost)
            edges.append([a_node, b_node, cost])


def extract_graph(df: pd.DataFrame = None):
    """Return adjacency-list style graph used by algorithms.

    If `df` is provided it is ignored because we build the graph from `edges`.
    """
    graph = {}
    for u, v, w in edges:
        graph.setdefault(u, []).append((v, w))
        graph.setdefault(v, []).append((u, w))
    return graph
