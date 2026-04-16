import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from transformers import pipeline
from pyvis.network import Network

# STEP 1: Initialize NLP Pipeline
# Using a multilingual model for sentiment analysis
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# STEP 2: Raw Data (Example: Geopolitical news snippets)
data = [
    {"text": "Rosneft and Indian Oil Corporation strengthen energy partnership in Delhi.", "source": "Russia",
     "target": "India"},
    {"text": "China's Sinopec signs a major LNG deal with Qatar Energy.", "source": "China", "target": "Qatar"},
    {"text": "Brazil expresses concerns over global supply chain disruptions affecting trade.", "source": "Brazil",
     "target": "Global Markets"},
    {"text": "Saudi Arabia and UAE discuss strategic investment in green hydrogen projects.", "source": "Saudi Arabia",
     "target": "UAE"},
    {"text": "South Africa welcomes new infrastructure technology from Chinese state firms.", "source": "South Africa",
     "target": "China"}
]

# STEP 3: Sentiment & Entity Processing
results = []
for entry in data:
    # Analyze sentiment (scale 1-5 stars converted to pos/neg/neu)
    sentiment = sentiment_analyzer(entry['text'])[0]
    score = int(sentiment['label'].split()[0])

    # Simple mapping for visualization: 1-2 (Neg), 3 (Neu), 4-5 (Pos)
    tone = "positive" if score > 3 else "negative" if score < 3 else "neutral"

    results.append({
        "from": entry['source'],
        "to": entry['target'],
        "tone": tone,
        "weight": score
    })

df = pd.DataFrame(results)

# STEP 4: Build Relationship Network
G = nx.Graph()

for _, row in df.iterrows():
    # Color edges based on sentiment: Green for Positive, Red for Negative
    edge_color = 'green' if row['tone'] == 'positive' else 'gray' if row['tone'] == 'neutral' else 'red'
    G.add_edge(row['from'], row['to'], weight=row['weight'], color=edge_color)

# STEP 5: Interactive Visualization with PyVis
net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white", notebook=False)

# Load NetworkX graph into PyVis
for node in G.nodes():
    net.add_node(node, label=node, title=node, color="#00ffcc")

for edge in G.edges(data=True):
    net.add_edge(edge[0], edge[1], color=edge[2]['color'], width=edge[2]['weight'])

# Save the visualization
net.save_graph("geopolitical_network.html")
print("Analysis complete. View the network in 'geopolitical_network.html'")