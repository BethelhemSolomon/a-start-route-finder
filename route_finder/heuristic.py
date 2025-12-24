import math
from typing import Dict
from .data_loader import load_dataset


def haversine(lat1, lon1, lat2, lon2):
    """Return great-circle distance between two points in kilometers."""
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def get_heuristic(df) -> Dict[str, Dict[str, float]]:
    """Return heuristic dict: heuristic[a][b] = straight-line distance (km) between nodes a and b.

    If `df` is provided it will be used; otherwise the default dataset is loaded.
    """
    if df is None:
        df = load_dataset()

    heuristic: Dict[str, Dict[str, float]] = {}
    for _, node_a in df.iterrows():
        a_id = str(node_a['node']).strip()
        heuristic[a_id] = {}
        for _, node_b in df.iterrows():
            b_id = str(node_b['node']).strip()
            if a_id == b_id:
                heuristic[a_id][b_id] = 0.0
            distance = haversine(
                float(node_a['latitude']), float(node_a['longitude']),
                float(node_b['latitude']), float(node_b['longitude'])
            )
            heuristic[a_id][b_id] = distance

    return heuristic