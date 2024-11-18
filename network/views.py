import pandas as pd
import networkx as nx
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Dataset, Player
from .forms import DatasetUploadForm

def home(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'network/home.html', {'datasets': datasets})

def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save()
            process_dataset(dataset)
            return redirect('network:visualization', dataset_id=dataset.id)
    else:
        form = DatasetUploadForm()
    return render(request, 'network/upload.html', {'form': form})

def process_dataset(dataset):
    df = pd.read_csv(dataset.file.path)
    for _, row in df.iterrows():
        Player.objects.create(
            dataset=dataset,
            name=row['player_name'],
            team=row['team'],
            goals=row['goals'],
            assists=row['assists'],
            tackles=row['tackles'],
            interceptions=row['interceptions']
        )

def visualization(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)
    return render(request, 'network/visualization.html', {'dataset': dataset})

def football_graph(request):
    return render(request, 'network/football-graph.html')

def get_network_data(request, dataset_id):
    players = Player.objects.filter(dataset_id=dataset_id)

    G = nx.Graph()

    # Add nodes
    for player in players:
        G.add_node(player.name,
                   team=player.team,
                   goals=player.goals,
                   assists=player.assists,
                   tackles=player.tackles,
                   interceptions=player.interceptions)

    # Add edges based on team connections
    teams = {}
    for player in players:
        if player.team not in teams:
            teams[player.team] = []
        teams[player.team].append(player.name)

    for team_players in teams.values():
        for i in range(len(team_players)):
            for j in range(i+1, len(team_players)):
                G.add_edge(team_players[i], team_players[j])

    # Convert to JSON format
    data = {
        'nodes': [{'id': node,
                   'team': G.nodes[node]['team'],
                   'goals': G.nodes[node]['goals'],
                   'assists': G.nodes[node]['assists'],
                   'tackles': G.nodes[node]['tackles'],
                   'interceptions': G.nodes[node]['interceptions']}
                  for node in G.nodes()],
        'links': [{'source': u, 'target': v} for (u, v) in G.edges()]
    }

    return JsonResponse(data)
