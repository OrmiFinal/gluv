# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Like
from posts.models import CommunityPost
from recruits.models import RecruitmentPost
from .serializers import LikeSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @action(detail=False, methods=['post'])
    def like_post(self, request):
        post_id = request.data.get('post_id')
        recruit_id = request.data.get('recruit_id')

        if not post_id and not recruit_id:
            return Response({'error': '게시글 ID가 필요합니다.'}, status=400)

        if post_id:
            post = get_object_or_404(CommunityPost, pk=post_id)
            like, created = Like.objects.get_or_create(user=request.user, community_post=post)
        elif recruit_id:
            recruit_post = get_object_or_404(RecruitmentPost, pk=recruit_id)
            like, created = Like.objects.get_or_create(user=request.user, recruitment_post=recruit_post)

        if not created:
            return Response({'error': '이미 좋아요를 눌렀습니다.'}, status=400)

        serializer = self.get_serializer(like)
        return Response(serializer.data)
