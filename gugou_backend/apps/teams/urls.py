from django.urls import path

from .views import (
    AdminTeamCancelView,
    AdminTeamDetailView,
    AdminTeamFailView,
    AdminTeamListView,
    AdminTeamParticipantsView,
    AdminTeamSuccessView,
    MyTeamProjectListView,
    TeamProjectCancelView,
    TeamProjectCheckFailView,
    TeamProjectCreateView,
    TeamProjectDetailView,
    TeamProjectJoinView,
    TeamProjectLeaveView,
    TeamProjectListView,
)

urlpatterns = [
    # 用户端接口
    path("", TeamProjectListView.as_view(), name="team-list"),
    path("create/", TeamProjectCreateView.as_view(), name="team-create"),
    path("my/", MyTeamProjectListView.as_view(), name="team-my"),
    path("<str:team_id>/", TeamProjectDetailView.as_view(), name="team-detail"),
    path("<str:team_id>/join/", TeamProjectJoinView.as_view(), name="team-join"),
    path("<str:team_id>/leave/", TeamProjectLeaveView.as_view(), name="team-leave"),
    path("<str:team_id>/cancel/", TeamProjectCancelView.as_view(), name="team-cancel"),
    path("<str:team_id>/check-fail/", TeamProjectCheckFailView.as_view(), name="team-check-fail"),
    # 管理员端接口
    path("admin/list/", AdminTeamListView.as_view(), name="admin-team-list"),
    path("admin/<str:team_id>/", AdminTeamDetailView.as_view(), name="admin-team-detail"),
    path("admin/<str:team_id>/participants/", AdminTeamParticipantsView.as_view(), name="admin-team-participants"),
    path("admin/<str:team_id>/cancel/", AdminTeamCancelView.as_view(), name="admin-team-cancel"),
    path("admin/<str:team_id>/fail/", AdminTeamFailView.as_view(), name="admin-team-fail"),
    path("admin/<str:team_id>/success/", AdminTeamSuccessView.as_view(), name="admin-team-success"),
]
