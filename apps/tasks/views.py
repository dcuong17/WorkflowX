from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import TaskSerializer
from .models import Task, Workspace
from apps.workspaces.models import WorkspaceMember
from rest_framework.exceptions import NotFound, PermissionDenied

# Create your views here.


class TaskViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_manager(self, workspace_id, user):
        try:
            member = WorkspaceMember.objects.get(workspace_id=workspace_id, user=user)
            if member.role != "manager":
                raise PermissionDenied("Không có quyền")
            return member
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại Member này trong workspace")

    def get_task(self, workspace_id, pk):
        try:
            task = Task.objects.get(workspace=workspace_id, pk=pk)
            return task
        except Task.DoesNotExist:
            raise NotFound("Không tồn tại Task này")

    def list(self, request, workspace_id=None):
        tasks = Task.objects.filter(workspace=self.kwargs["workspace_id"])
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, workspace_id=None):
        serializer = TaskSerializer(
            data=request.data, context={"workspace_id": self.kwargs["workspace_id"]}
        )
        self.get_manager(self.kwargs["workspace_id"], request.user)
        if serializer.is_valid():
            try:
                workspace = Workspace.objects.get(pk=self.kwargs["workspace_id"])
            except Workspace.DoesNotExist:
                raise NotFound("Không tồn tại Workspace này")
            serializer.save(workspace=workspace, assign_from=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, workspace_id=None, pk=None):
        task = self.get_task(self.kwargs["workspace_id"], pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, workspace_id=None, pk=None):
        self.get_manager(self.kwargs["workspace_id"], request.user)
        task = self.get_task(self.kwargs["workspace_id"], pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, workspace_id=None, pk=None):
        self.get_manager(self.kwargs["workspace_id"], request.user)
        task = self.get_task(self.kwargs["workspace_id"], pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class TaskListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, workspace_id):
#         tasks = Task.objects.filter(workspace=workspace_id)
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, workspace_id):
#         serializer = TaskSerializer(data=request.data)
#         if serializer.is_valid():
#             workspace = Workspace.objects.get(pk=workspace_id)
#             serializer.save(workspace=workspace, assign_from=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request, workspace_id, pk=None):
        try:
            task = Task.objects.get(workspace_id=workspace_id, pk=pk)
            return task
        except Exception:
            raise NotFound("Không có task này")

    def get(self, request, workspace_id, pk=None):
        task = self.get_queryset(request, workspace_id=workspace_id, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, workspace_id, pk=None):
        task = self.get_queryset(request, workspace_id=workspace_id, pk=pk)
        if task.assign_from != request.user:
            return Response(
                {"message": "Không có quyền chỉnh sửa"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, workspace_id, pk=None):
        task = self.get_queryset(request, workspace_id=workspace_id, pk=pk)
        if task.assign_from != request.user:
            return Response(
                {"message": "Không có quyền xóa"}, status=status.HTTP_403_FORBIDDEN
            )
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
