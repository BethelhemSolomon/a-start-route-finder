from __future__ import annotations
import pandas as pd


def load_dataset(path: str = './Nodes.xlsx') -> pd.DataFrame:
    """Load node dataset and normalize column names.

    Expected columns (case-insensitive): `node`, `latitude`, `longitude`.
    Returns a DataFrame with lowercase columns: `node`, `latitude`, `longitude`.
    """
    df = pd.read_excel(path)
    df = df.dropna()

    # normalize column names to lowercase and strip spaces
    df.columns = [c.strip().lower() for c in df.columns]

    # common synonyms
    if 'nodes' in df.columns and 'node' not in df.columns:
        df = df.rename(columns={'nodes': 'node'})
    if 'lat' in df.columns and 'latitude' not in df.columns:
        df = df.rename(columns={'lat': 'latitude'})
    if 'lon' in df.columns and 'longitude' not in df.columns:
        df = df.rename(columns={'lon': 'longitude'})

    required = {'node', 'latitude', 'longitude'}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Dataset must contain columns: {required}, got {set(df.columns)}")

    # Ensure latitude/longitude are numeric and use dot as decimal separator
    df['latitude'] = df['latitude'].astype(str).str.replace(',', '.')
    df['longitude'] = df['longitude'].astype(str).str.replace(',', '.')
    df['latitude'] = pd.to_numeric(df['latitude'])
    df['longitude'] = pd.to_numeric(df['longitude'])

    # Normalize node identifiers (strip whitespace)
    df['node'] = df['node'].astype(str).str.strip()

    return df



