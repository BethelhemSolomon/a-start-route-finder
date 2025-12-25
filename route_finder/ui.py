from __future__ import annotations
import tracemalloc
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from .data_loader import load_dataset
from .graph_io import extract_graph, visualize_on_map
from .utils import measure_execution_time
from .algorithms import a_star, greedy_best_first
from .heuristic import get_heuristic

# This function mirrors the original Streamlit UI logic as-is, only moved here.
def main(df=None):

    if "page" not in st.session_state:
        st.session_state.page = "home"
    if df is None:
        df = load_dataset()  # expects Nodes.xlsx with node, latitude, longitude

    unique_places = sorted(df['node'].unique())

    st.title("Route Finding in Addis (A-Star)")

    # Sidebar
    start_place = st.sidebar.selectbox("Select Start City:", unique_places, key="start_place")
    end_place = st.sidebar.selectbox("Select Destination City:", unique_places, key="end_place")

    # just moved it here in case the app running is faster
    graph = extract_graph(df)
    place_coords = {row['node']: (row['latitude'], row['longitude']) for _, row in df.iterrows()}
    
    # Normalize selected values to avoid whitespace mismatches
    if isinstance(start_place, str):
        start_place = start_place.strip()
    if isinstance(end_place, str):
        end_place = end_place.strip()

    # if "results" not in st.session_state:
    #     st.session_state.results = None

    if st.sidebar.button("Calculate"):
        st.session_state.page = "algorithm_run"
    if st.sidebar.button("View Heuristic"):
        st.session_state.page = "view_heuristic"
    if st.sidebar.button("View Adjancency Matrix"):
        st.session_state.page = "view_matrix"



    if st.session_state.page == "view_heuristic":
        st.subheader(f"Heurisitcs to {end_place}(km)")
        with st.spinner("Calculating Heuristic..."):
            heuristic = get_heuristic(df)
            matrix_data = []
            for place in unique_places:

                if place == end_place:
                    h_value = 0.0
                else:
                    h_value = round(heuristic[place][end_place], 3)
                
                matrix_data.append({"Place":place, f"h(n)-> {end_place}":round(h_value, 3)})

            st.dataframe(
                pd.DataFrame(matrix_data).set_index("Place")
            )
            
        
    if st.session_state.page == "view_matrix":
        st.subheader("Adjacency Matrix (Km)")
        with st.spinner("Calculating Adjacency Matrix..."):
            nodes = sorted(graph.keys())
            n = len(nodes)

            matrix = [["inf"] * n for _ in range(n)]

            for i in range(n):
                matrix[i][i] = 0.0
            
            node_index = {node: i for i, node in enumerate(nodes)}
            for u, neighbours in graph.items():
                i = node_index[u]
                for v, weight in neighbours:
                    j = node_index[v]
                    matrix[i][j] = round(weight, 3)
            st.dataframe(pd.DataFrame(matrix, index=nodes, columns=nodes))
        
    if st.session_state.page == "algorithm_run":
        if start_place == end_place:
            st.error("Start and destination cities cannot be the same.")
        else:
            with st.spinner("Running A*..."):
                heuristic = get_heuristic(df)

                # A* Algorithm Execution
                tracemalloc.start()
                a_star_time = measure_execution_time(a_star, graph, start_place, end_place, heuristic)
                a_star_path, a_star_cost, a_star_visited_edges = a_star(graph, start_place, end_place, heuristic)
                current, peak = tracemalloc.get_traced_memory()
                a_star_memory = peak / 1024
                tracemalloc.stop()

                st.subheader(f"Algorithm Result from {start_place} to {end_place}")

                if a_star_path:
                    st.write(f"Path: {' → '.join(a_star_path)}")
                    st.write(f"Total Cost: {a_star_cost} km")
                    st.write(f"Time: {a_star_time:.6f} seconds")
                    st.write(f"Memory Used: {peak / 1024:.2f} KB")
                    a_map = visualize_on_map(df, a_star_path, a_star_visited_edges, place_coords, graph, start_place, end_place, heuristic)
                    
                    st_folium(
                        a_map,
                        use_container_width=True,
                        height=800,
                        key=f"a_star_map_{start_place}_{end_place}"
                    )
                else:
                    st.warning("No path found.")

    