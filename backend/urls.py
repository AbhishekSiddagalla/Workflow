from django.urls import path

from backend.views import (
    DashboardView,
    FetchAllWorkflowsView,
    SendWorkflowView,
    FetchWorkflowView,
    DeleteWorkflowView,
    FetchTemplatesView,
    SyncTemplatesView,

)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path("workflows/", FetchAllWorkflowsView.as_view(), name="all-workflows"),

    path("workflows/<int:id>/send/", SendWorkflowView.as_view(), name="send-workflow"),
    path("workflows/<int:id>/update/", FetchWorkflowView.as_view(), name="update-workflow"),
    path("workflows/<int:id>/delete/",DeleteWorkflowView.as_view(), name="delete-workflow"),

    path("templates/", FetchTemplatesView.as_view(), name="fetch-templates"),
    path("templates/sync/", SyncTemplatesView.as_view(), name="sync-templates"),
]