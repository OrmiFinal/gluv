from collections import OrderedDict
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status

from posts.models import CommunityPost
from posts.serializers import CommunityPostSerializer, ListResponseSerializer, ResponseSerializer

class CommunityPostPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, status, message, data):
        return Response(OrderedDict([
            ('status', 'success'),
            ('message', 'Success message'),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

class CommunityPostView(viewsets.ViewSet):
    '''
    커뮤니티 게시글 관련 ViewSet
    '''
    pagination_class = pagination.PageNumberPagination

    def get_permissions(self):
        # list 메서드에는 권한 필요 없음
        if self.action == 'list':
            return [AllowAny()]
        
        # notices 메서드에는 권한 필요 없음
        if self.action == 'notices':
            return [AllowAny()]
        
        # hot 메서드에는 권한 필요 없음
        if self.action == 'hot':
            return [AllowAny()]
        
        # retrieve 메서드에는 권한 필요 없음
        if self.action == 'retrieve':
            return [AllowAny()]
        
        # 기타 경우에는 기본 권한 적용
        else:
            return [IsAuthenticated()]

    @action(methods=["get"], detail=False, url_path='notices', url_name="notices")
    def notices(self, request, *args, **kwargs):
        '''
        공지 사항을 조회하는 함수
        '''
        paginator = CommunityPostPagination()
        notices = CommunityPost.objects.filter(category='notice')
        page = paginator.paginate_queryset(notices, request)
        serializer = CommunityPostSerializer(page, many=True)
        return paginator.get_paginated_response(status='success', message='Successfully', data=serializer.data)
    
    def list(self, request, *args, **kwargs):
        '''
        특정 조건에 따라 게시글 목록 조회
        '''

        # 필터링 조건 파싱
        search_query = request.GET.get('search', '')
        category_query = request.GET.getlist('category', [])
        author_query = request.GET.get('author', '')
        order_by_query = request.GET.get('order_by', 'created_at')
        order_query = request.GET.get('order', 'asc')
        
        # 필터링 조건 설정
        filter_conditions = {}

        # 제목 검색
        if search_query:
            filter_conditions['title__icontains'] = search_query

        # 커뮤니티 게시판만 검색
        if 'creation' in category_query:
            filter_conditions['category__startswith'] = 'creation'
        # 커뮤니티 게시판만 검색
        elif 'comm' in category_query:
            filter_conditions['category__startswith'] = 'comm' 
        # 다중 카테고리 선택 검색
        elif category_query:
            filter_conditions['category__in'] = category_query

        # 작성자 검색
        if author_query:
            filter_conditions['author__nickname'] = author_query

        # 정렬 기준
        order = 'created_at'
        if order_by_query.lower() == 'views':
            order = 'view_count'

        # 정렬 순서 
        if order_query.lower() == 'desc':
            order = '-' + order

        paginator = CommunityPostPagination()
        posts = CommunityPost.objects.exclude(category='notice').filter(**filter_conditions).order_by(order)
        page = paginator.paginate_queryset(posts, request)
        serializer = CommunityPostSerializer(page, many=True)
        return paginator.get_paginated_response(status='success', message='Successfully', data=serializer.data)
    
    @action(methods=["get"], detail=False, url_path='hot', url_name="hot")
    def hot(self, request, *args, **kwargs):
        '''
        인기 게시글 검색
        '''
        paginator = CommunityPostPagination()
        post = CommunityPost.objects.exclude(category='notice').order_by('-view_count')
        page = paginator.paginate_queryset(post, request)
        serializer = CommunityPostSerializer(page, many=True)
        return paginator.get_paginated_response(status='success', message='Successfully', data=serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        '''
        게시글 상세 조회
        '''
        post = CommunityPost.objects.get(id=pk)
        response_serializer = ResponseSerializer(data={
            'status': 'success',
            'message': 'Success message',
            'data': CommunityPostSerializer(post, many=False).data
        })
        response_serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=response_serializer.validated_data)