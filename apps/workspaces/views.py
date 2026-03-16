from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import CustomUser
from apps.workspaces.models import Workspace, WorkspaceMember
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

# Create your views here.


class WorkspaceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer

    def list(self, request):
        workspace = Workspace.objects.filter(created_by=request.user)
        serializer = self.get_serializer(workspace, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk):

        workspace = self.get_object()
        if workspace.created_by != request.user:
            raise PermissionDenied("Không có quyền truy cập")
        return super().update(request, pk)

    def destroy(self, request, pk):

        workspace = self.get_object()
        if workspace.created_by != request.user:
            raise PermissionDenied("Không có quyền truy cập")
        return super().destroy(request, pk)

    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)
        WorkspaceMember.objects.create(
            workspace=workspace, user=self.request.user, role="manager"
        )


class WorkspaceMemberViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, workspace_id=None):
        print(
            f">>> workspace_id = {self.kwargs['workspace_id']}, type = {type(self.kwargs['workspace_id'])}"
        )
        workspace_members = WorkspaceMember.objects.filter(
            workspace=self.kwargs["workspace_id"]
        )
        serializer = WorkspaceMemberSerializer(workspace_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, workspace_id=None):
        serializer = WorkspaceMemberSerializer(data=request.data)
        try:
            member = WorkspaceMember.objects.get(
                workspace=self.kwargs["workspace_id"], user=request.user
            )
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại member này")
        if member.role != "manager":
            raise PermissionDenied("Không có quyền thêm thành viên mới")
        if serializer.is_valid():
            try:
                workspace = Workspace.objects.get(pk=self.kwargs["workspace_id"])
            except Workspace.DoesNotExist:
                raise NotFound("Không tồn tại workspace này")
            serializer.save(workspace=workspace, role="member")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, workspace_id=None, pk=None):
        try:
            is_manager = WorkspaceMember.objects.get(
                workspace=self.kwargs["workspace_id"], user=request.user
            )
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại member này")
        if is_manager.role != "manager":
            raise PermissionDenied("Không có quyền xóa member này")

        try:
            member = WorkspaceMember.objects.get(
                workspace=self.kwargs["workspace_id"], pk=pk
            )
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại member này")
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class WorkspaceViewSet(ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         workspace = Workspace.objects.filter(created_by=request.user)
#         serializer = WorkspaceSerializer(workspace, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def retrieve(self, request, pk):
#         try:
#             workspace = Workspace.objects.get(pk=pk)
#         except Workspace.DoesNotExist:
#             raise NotFound("Không có workspace này")
#         serializer = WorkspaceSerializer(workspace)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def create(self, request):
#         serializer = WorkspaceSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(created_by=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def update(self, request, pk):
#         workspace = Workspace.objects.get(pk=pk)
#         serializer = WorkspaceSerializer(workspace, data=request.data)
#         if workspace.created_by != request.user:
#             return Response(
#                 "Không có quyền cập nhật", status=status.HTTP_400_BAD_REQUEST
#             )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)

#     def destroy(self, request, pk):
#         workspace = Workspace.objects.get(pk=pk)
#         if workspace.created_by != request.user:
#             return Response("Không có quyền xóa", status=status.HTTP_400_BAD_REQUEST)
#         workspace.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class WorkspaceListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):

#         workspace = Workspace.objects.filter(created_by=request.user)
#         serializer = WorkspaceSerializer(workspace, many=True)
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK,
#         )

#     def post(self, request):

#         serializer = WorkspaceSerializer(data=request.data)
#         if serializer.is_valid():
#             workspace = serializer.save(created_by=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)


# class WorkspaceDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self, request, pk=None):
#         try:
#             print(f">>> get_queryset được gọi với pk = {pk}")
#             object = Workspace.objects.get(pk=pk)
#             return object
#         except Workspace.DoesNotExist:
#             raise NotFound("Không thấy gì cả")

#     def get(self, request, pk=None):
#         workspace = self.get_queryset(request, pk=pk)
#         serializer = WorkspaceSerializer(workspace)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, pk=None):
#         workspace = self.get_queryset(request, pk=pk)
#         serializer = WorkspaceSerializer(workspace, data=request.data)
#         if workspace.created_by != request.user:
#             return Response(
#                 {"message": "Không có quyền"}, status=status.HTTP_403_FORBIDDEN
#             )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)

#     def delete(self, request, pk=None):
#         workspace = self.get_queryset(request, pk=pk)
#         if workspace.created_by != request.user:
#             return Response(
#                 {"message": "Không có quyền"}, status=status.HTTP_403_FORBIDDEN
#             )
#         workspace.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
