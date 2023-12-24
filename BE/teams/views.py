from django.http import Http404
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Team, TeamMember
from .serializers import TeamSerializer, TeamMemberSerializer, TeamDetailSerializer, TeamMemberChangeSerializer
from .permissions import IsLeaderOrReadOnly


class TeamPagination(PageNumberPagination):
    '''
    Pagination 커스텀
    '''
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, status, message, data):
        return Response({
            'status': 'success',
            'message': 'Success message',
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
    

class TeamListView(generics.ListAPIView):
    '''
    모임의 목록을 조회하는 View
    로그인 권한 필요
    '''
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''
    모임의 상세 정보를 조회, 업데이트, 삭제하는 View
    로그인 권한 필요, 수정/삭제는 리더 권한 필요
    '''
    queryset = Team.objects.all()
    serializer_class = TeamDetailSerializer
    permission_classes = [IsAuthenticated, IsLeaderOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'user': self.request.user,
            'team_id': self.kwargs['pk'],
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        team_id = self.kwargs['pk']
        try:
            team = Team.objects.get(pk=team_id)
            team.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Team.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class TeamJoinView(generics.UpdateAPIView):
    '''
    모임 가입 신청한 유저를 승인하기 위한 View
    로그인 권한, 리더 권한 필요
    request body: user_id (승인 대상의 user_id)
    '''
    queryset = TeamMember.objects.all()
    # permission_classes = [IsAuthenticated, IsLeaderOrReadOnly]

    def get_object(self):
        team_id = self.kwargs.get('pk')
        team = get_object_or_404(Team, pk=team_id)
        obj = get_object_or_404(self.queryset, team=team, user=self.request.data['user'], is_approved=False)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        team_member = self.get_object()
        team = team_member.team

        if team.current_attendance >= team.max_attendance:
            return Response({'detail': '모임의 인원이 가득 찼기 때문에 더 승인할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        team.current_attendance += 1
        team.save()

        team_member.is_approved = True
        team_member.save()

        return Response({'detail': '참가신청 승인 완료되었습니다.'}, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404

class TeamLeaveView(generics.DestroyAPIView):
    '''
    모임 탈퇴를 위한 View
    로그인 권한 필요
    TeamMember 모델의 속성
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_leader = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    '''
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        team_id = self.kwargs.get('pk')
        return TeamMember.objects.filter(team=team_id)
    
   

    def get_object(self):
        try:
            team_id = self.kwargs.get('pk')
            user_id = self.request.user.id
            print(f"team_id: {team_id}, user_id: {user_id}") 
            instance = TeamMember.objects.get(team_id=team_id, user_id=user_id)
            print(f"instance: {instance}") 
            return instance
        except TeamMember.DoesNotExist:
            raise Http404("TeamMember not found")

    
    def destroy(self, request, *args, **kwargs):
        # 모임 인원 수 조절
        instance = self.get_object()
        team = get_object_or_404(Team, pk=self.kwargs.get('pk'))
        if team.current_attendance == 1:
            return Response({'detail': '모임의 다른 구성원이 없습니다. 모임 삭제를 해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        team.current_attendance -= 1
        team.save()
        if instance.is_leader:
            # 만약 Leader인 경우, 다음 index의 유저를 Leader로 설정
            next_leader = TeamMember.objects.filter(team=team, is_approved=True, is_leader=False).first()
            if next_leader:
                next_leader.is_leader = True
                next_leader.save()
        instance.delete()
        return Response({"detail": "모임 탈퇴 완료되었습니다."}, status=status.HTTP_200_OK)

    

class TeamKickView(generics.DestroyAPIView):
    '''
    모임의 구성원 추방을 위한 View
    로그인 권한, 리더 권한 필요
    request body : user_id (추방 대상의 user_id)
    '''
    queryset = TeamMember.objects.all()
    permission_classes = [IsAuthenticated, IsLeaderOrReadOnly]

    def get_object(self):
        user_id = self.request.data.get('user_id')
        team = get_object_or_404(Team, pk=self.kwargs.get('pk'))
        return get_object_or_404(self.get_queryset(), team=team.id, user=user_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        team = get_object_or_404(Team, pk=self.kwargs.get('pk'))
        team.current_attendance -= 1
        team.save()
        instance.delete()
        return Response({'detail': '구성원 추방 완료되었습니다.'}, status=status.HTTP_200_OK)


class TeamLeaderChangeView(generics.UpdateAPIView):
    '''
    모임의 리더를 변경하기 위한 View
    로그인 권한, 리더 권한 필요
    '''
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberChangeSerializer
    permission_classes = [IsAuthenticated, IsLeaderOrReadOnly]

    def get_object(self):
        team_id = self.kwargs.get('pk')
        return get_object_or_404(TeamMember, team=team_id, is_leader=True)

    def perform_update(self, serializer):
        # 이전 리더를 찾아 리더 권한을 해제
        previous_leader = self.get_object()
        previous_leader.is_leader = False
        previous_leader.save()

        # 새 리더를 찾아 리더 권한 부여
        new_leader = get_object_or_404(TeamMember, team=self.kwargs['pk'], user=self.request.data.get('user'))
        new_leader.is_leader = True
        new_leader.save()

        return Response({"detail": "리더 권한이 변경되었습니다."}, status=status.HTTP_200_OK)


class TeamMembersView(generics.ListAPIView):
    '''
    구성원 목록을 보기 위한 View
    로그인 권한 필요
    '''
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(team_id=self.kwargs['pk'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class TeamMyListView(generics.ListAPIView):
    '''
    유저가 가입한 모임을 보기 위한 View
    로그인 권한 필요
    '''
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = TeamMember.objects.filter(user=user_id, is_approved=True)
        team_ids = queryset.values_list('team_id', flat=True)
        teams = Team.objects.filter(id__in=team_ids)
        return teams
    
    def list(self, request, *args, **kwargs):
        paginator = TeamPagination()
        comments = self.get_queryset().order_by('id')
        page = paginator.paginate_queryset(comments, request)
        serializer = TeamSerializer(page, many=True)
        return paginator.get_paginated_response(status='success', message='Successfully', data=serializer.data)
    

class TeamsMyAppliedListView(generics.ListAPIView):
    '''
    유저가 가입 신청한 모임을 보기 위한 View
    로그인 권한 필요
    '''
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = TeamMember.objects.filter(user=user_id, is_approved=False)
        team_ids = queryset.values_list('team_id', flat=True)
        teams = Team.objects.filter(id__in=team_ids)
        return teams
    
    def list(self, request, *args, **kwargs):
        paginator = TeamPagination()
        comments = self.get_queryset().order_by('id')
        page = paginator.paginate_queryset(comments, request)
        serializer = TeamSerializer(page, many=True)
        return paginator.get_paginated_response(status='success', message='Successfully', data=serializer.data)