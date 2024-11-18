import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import defaultdict

class FootballPlayerAnalysis:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
        self.graph = nx.Graph()
        self.components = []

    def create_graph(self, goal_threshold=10, assist_threshold=5):
        # Añadir nodos
        for _, row in self.df.iterrows():
            self.graph.add_node(row['Player'], **row.to_dict())

        # Conectar jugadores basado en goles y asistencias
        top_players = self.df[(self.df['Total_Goals'] > goal_threshold) | (self.df['Assists'] > assist_threshold)]
        for i, player1 in top_players.iterrows():
            for j, player2 in top_players.iterrows():
                if i < j:
                    similarity = 1 / (1 + abs(player1['Total_Goals'] - player2['Total_Goals']) +
                                      abs(player1['Assists'] - player2['Assists']))
                    self.graph.add_edge(player1['Player'], player2['Player'], weight=similarity)

    def analyze_components(self):
        self.components = list(nx.connected_components(self.graph))
        print(f"Número de componentes conexos: {len(self.components)}")
        for i, component in enumerate(self.components[:5], 1):  # Mostrar solo los primeros 5 componentes
            print(f"\nComponente {i}: {len(component)} jugadores")
            top_players = sorted(component, key=lambda x: self.graph.nodes[x]['Total_Goals'], reverse=True)[:3]
            print("Top 3 jugadores por goles:")
            for player in top_players:
                node = self.graph.nodes[player]
                print(f"  {player} - {node['Squad']} - {node['Total_Goals']} goles, {node['Assists']} asistencias")

    def find_most_similar_players(self, player_name, top_n=5):
        if player_name not in self.graph:
            print(f"Jugador {player_name} no encontrado en el grafo.")
            return

        similarities = []
        for neighbor in self.graph.neighbors(player_name):
            similarity = self.graph[player_name][neighbor]['weight']
            similarities.append((neighbor, similarity))

        print(f"\nJugadores más similares a {player_name}:")
        for player, similarity in sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]:
            node = self.graph.nodes[player]
            print(f"  {player} - {node['Squad']} - Similitud: {similarity:.2f}")

    def create_interactive_graph(self):
        net = Network(notebook=True, cdn_resources='remote')

        # Añadir nodos
        for node in self.graph.nodes(data=True):
            net.add_node(node[0],
                         label=node[0],
                         title=f"Equipo: {node[1]['Squad']}, Goles: {node[1]['Total_Goals']}, Asistencias: {node[1]['Assists']}")

        # Añadir aristas
        for edge in self.graph.edges(data=True):
            net.add_edge(edge[0], edge[1], value=edge[2]['weight']*10, title=f"Similitud: {edge[2]['weight']:.2f}")

        return net

    def save_interactive_graph(self, filename="football_graph.html"):
        net = self.create_interactive_graph()
        net.show(filename)
        print(f"Grafo interactivo guardado como {filename}")

# Uso del código
analysis = FootballPlayerAnalysis('/content/drive/MyDrive/Complejidad/2021-2022_Football_Player_Stats.csv')
analysis.create_graph(goal_threshold=15, assist_threshold=10)
analysis.analyze_components()
analysis.find_most_similar_players("Kylian Mbappé")
analysis.save_interactive_graph()