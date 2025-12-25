# Addis Ababa Route Finder (Streamlit)

This repository customizes the reorganized repo into doing a star and greedy search algorithms for a school project. 
All UI behavior are preserved. The structure of the data set has changed. Heuristics is computed using havestine whereas distance is manually added to the dataset.

## Preview UI
<img src="./assets/image.png">

## How to run

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```


## Project layout
```
app/
  streamlit_app.py
route_finder/
  __init__.py
  data_loader.py
  graph_io.py
  heuristic.py
  utils.py
  ui.py
  algorithms/
    __init__.py
    algorithms.py
Nodes.xlsx
Edges.xlsx
requirements.txt
README.md
```
