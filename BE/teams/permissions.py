from teams.models import TeamMember
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsLeaderOrReadOnly(permissions.BasePermission):
    """
    리더 권한 설정
    """

    def has_permission(self, request, view):
        # 모든 사용자에 대한 읽기 권한 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # PUT 및 DELETE 메서드에 대한 권한
        team_id = view.kwargs.get('pk')
        leader = TeamMember.objects.filter(team_id=team_id, user=request.user.id, is_leader=True).exists()
        return request.user.is_authenticated and leader
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'DELETE']:
            team_id = obj.team.id
            user = request.user
            leader = TeamMember.objects.filter(team_id=team_id, user=user.id, is_leader=True).exists()
            if not leader:
                return False
        return True