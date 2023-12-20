from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RecruitmentPost
from .serializers import RecruitmentPostSerializer, RecruitmentPostCreateSerializer
from teams.serializers import TeamSerializer, TeamMemberSerializer
from teams.models import Team, TeamMember
from schedules.models import Schedule

class RecruitmentPostViewSet(viewsets.ModelViewSet):
    '''
    모집 게시글 ViewSet

    '''
    queryset = RecruitmentPost.objects.all()
    serializer_class = RecruitmentPostSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        '''
        게시글 조회 시 조회수 증가
        '''
        instance = self.get_object()
        instance.view_count += 1 
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = RecruitmentPostCreateSerializer(data=request.data)

        if serializer.is_valid():
            # 원하는 필드를 validated_data에 추가
            validated_data = serializer.validated_data
            validated_data['frequency'] = request.data.get('frequency')
            validated_data['day'] = request.data.get('day')
            validated_data['week'] = request.data.get('week')
            validated_data['category'] = request.data.get('category')
            validated_data['max_attendance'] = request.data.get('max_attendance')

            author = self.request.user
            team = validated_data.get('team')

            if not team:
                team_category = validated_data.get('category')
                team_max_attendance = validated_data.get('max_attendance')
                team = Team.objects.create(category=team_category, max_attendance=team_max_attendance, current_attendance=1, name=f'{author.nickname}의 모임')

            team_member = TeamMember.objects.create(user=author, team=team, is_approved=True, is_leader=True)
            team_member.save()

            schedule_data = {
                'frequency': validated_data.get('frequency'),
                'day': validated_data.get('day'),
                'week': validated_data.get('week'),
            }
            schedule = Schedule.objects.create(team=team, **schedule_data)
            schedule.save()

            recruit_post = RecruitmentPost.objects.create(
                team=team,
                author=author,
                title=validated_data.get('title'),
                content=validated_data.get('content'),
                region=validated_data.get('region')
            )
            recruit_post.save()

            return Response(recruit_post.id, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=False, methods=['get'], url_path='hot', url_name='hot')
    def hot_list(self, request):
        '''
        인기 모집목록 조회 기능
        정렬 기준 : view_count
        모집 개수 : count 변수

        페이지네이션 적용 필요
        '''
        count = 5
        queryset = RecruitmentPost.objects.order_by('-view_count')[:count]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post', 'delete'], url_path='apply', url_name='apply')
    def apply(self, request, pk=None):
        '''
        GET : 모집 게시글에 가입 신청을 넣은 유저들의 목록 반환
        POST : 로그인 한 유저가 모집게시글에 가입 신청
        DELETE : 모집게시글에 가입 신청한 유저가 신청을 취소
        '''
        post = self.get_object()
        user = request.user.pk
        team = post.team 

        if request.method == 'GET':
            queryset = TeamMember.objects.filter(team=team, is_approved=False)
            serializer = TeamMemberSerializer(queryset, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            member = TeamMember.objects.filter(user=user, team=team).exists()
            # 이미 신청한 member인지 판별
            if member:
                return Response({'detail': '이미 신청한 멤버입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            data = {'user': user, 'team': team.id, 'is_leader': False, 'is_approved': False}
            serializer = TeamMemberSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail': '신청이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            member = TeamMember.objects.filter(user=user, team=team, is_approved=False).first()
            if not member:
                return Response({'detail': '취소할 신청이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            member.delete()
            return Response({'detail': '신청이 취소되었습니다.'}, status=status.HTTP_200_OK)
