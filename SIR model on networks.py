import networkx as nx
import numpy as np
import plotly.graph_objects as go
import random


def create_sir_timeline_app(n_nodes=60, p_edge=0.1, beta=0.2, gamma=0.05, steps=20):
    # 1. Генерация графа и позиций (фиксируем для всех кадров)
    G = nx.erdos_renyi_graph(n=n_nodes, p=p_edge)
    pos = nx.spring_layout(G, seed=42)

    # Подготовка ребер (они не меняются)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # 2. Симуляция с сохранением каждого шага
    status = {node: 0 for node in G.nodes()}
    status[random.choice(list(G.nodes()))] = 1  # Patient Zero

    history = [status.copy()]
    for _ in range(steps):
        new_status = status.copy()
        for node in G.nodes():
            if status[node] == 1:
                for neighbor in G.neighbors(node):
                    if status[neighbor] == 0 and random.random() < beta:
                        new_status[neighbor] = 1
                if random.random() < gamma:
                    new_status[node] = 2
        status = new_status
        history.append(status.copy())

    # 3. Создание кадров для Plotly
    colors_map = {0: '#3498db', 1: '#e74c3c', 2: '#2ecc71'}
    frames = []
    for t, step_status in enumerate(history):
        node_colors = [colors_map[step_status[n]] for n in G.nodes()]

        frames.append(go.Frame(
            data=[go.Scatter(x=edge_x, y=edge_y, mode='lines'),  # Ребра
                  go.Scatter(x=[pos[n][0] for n in G.nodes()],
                             y=[pos[n][1] for n in G.nodes()],
                             mode='markers',
                             marker=dict(size=12, color=node_colors, line_width=2),
                             text=[f"Node {n} Status: {step_status[n]}" for n in G.nodes()],
                             hoverinfo='text')],
            name=str(t)
        ))

    # 4. Сборка интерфейса со слайдером
    fig = go.Figure(
        data=frames[0].data,
        layout=go.Layout(
            title="Spatiotemporal Epidemic Dynamics (SIR Model)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            hovermode='closest',
            updatemenus=[{
                "buttons": [
                    {"args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                     "label": "Play", "method": "animate"},
                    {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate",
                                       "transition": {"duration": 0}}],
                     "label": "Pause", "method": "animate"}
                ],
                "type": "buttons", "showactive": False, "x": 0.1, "y": 0
            }],
            sliders=[{
                "active": 0,
                "yanchor": "top", "xanchor": "left",
                "currentvalue": {"font": {"size": 16}, "prefix": "Step: ", "visible": True, "xanchor": "right"},
                "steps": [{"args": [[f.name], {"frame": {"duration": 300, "redraw": True}, "mode": "immediate"}],
                           "label": f.name, "method": "animate"} for f in frames]
            }]
        ),
        frames=frames
    )

    fig.write_html("sir_simulation_final.html")
    print("Interactive Timeline Dashboard saved to sir_simulation_final.html")


if __name__ == "__main__":
    create_sir_timeline_app()