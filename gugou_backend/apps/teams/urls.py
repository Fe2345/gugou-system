from django.urls import path

from .views import (
    MyTeamProjectListView,
    TeamProjectCancelView,
    TeamProjectCheckFailView,
    TeamProjectCreateView,
    TeamProjectDetailView,
    TeamProjectJoinView,
    TeamProjectListView,
)

urlpatterns = [
    path("", TeamProjectListView.as_view(), name="team-list"),
    path("create/", TeamProjectCreateView.as_view(), name="team-create"),
    path("my/", MyTeamProjectListView.as_view(), name="team-my"),
    path("<str:team_id>/", TeamProjectDetailView.as_view(), name="team-detail"),
    path("<str:team_id>/join/", TeamProjectJoinView.as_view(), name="team-join"),
    path("<str:team_id>/cancel/", TeamProjectCancelView.as_view(), name="team-cancel"),
    path("<str:team_id>/check-fail/", TeamProjectCheckFailView.as_view(), name="team-check-fail"),
]
