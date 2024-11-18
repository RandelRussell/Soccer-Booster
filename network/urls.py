from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_dataset, name='upload'),
    path('visualization/<int:dataset_id>/', views.visualization, name='visualization'),
    path('api/network-data/<int:dataset_id>/', views.get_network_data, name='network-data'),
    path('football-graph/', views.football_graph, name='football-graph'),
]
