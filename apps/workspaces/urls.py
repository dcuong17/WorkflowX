from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, WorkspaceMemberViewSet
from apps.tasks.views import TaskViewSet

router = DefaultRouter()
router.register("", WorkspaceViewSet, basename="workspace"),

urlpatterns = [
    path(
        "<uuid:workspace_id>/tasks/",
        TaskViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="task-list",
    ),
    path(
        "<uuid:workspace_id>/tasks/<uuid:pk>/",
        TaskViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="task-detail",
    ),
    path(
        "<uuid:workspace_id>/tasks/<uuid:pk>/status/",
        TaskViewSet.as_view({"patch": "task_status"}),
        name="task-status",
    ),
    path(
        "<uuid:workspace_id>/tasks/<uuid:pk>/submission/",
        TaskViewSet.as_view({"post": "submission"}),
        name="task-submission",
    ),
    path(
        "<uuid:workspace_id>/members/",
        WorkspaceMemberViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="member-list",
    ),
    path(
        "<uuid:workspace_id>/members/<uuid:pk>/",
        WorkspaceMemberViewSet.as_view(
            {
                "delete": "destroy",
            }
        ),
        name="member-detail",
    ),
] + router.urls


# from django.urls import path
# from rest_framework.routers import DefaultRouter
# from .views import WorkspaceViewSet


# router = DefaultRouter()
# router.register("", WorkspaceViewSet, basename="workspace")
