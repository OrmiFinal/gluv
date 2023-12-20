from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from books.models import Book
from books.serializers import BookSerializer, ListResponseSerializer

class RecentBookView(viewsets.ViewSet):
    '''
    신간 도서 정보를 조회하는 ViewSet

    Attributes:
        DEFAULT_BOOK_COUNT (int): 기본 신간 도서 수
    '''
    DEFAULT_BOOK_COUNT = 10
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]
    
    @action(methods=["get"], detail=False, url_path='recent', url_name="recent", permission_classes=[permissions.AllowAny])
    def recent(self, request, *args, **kwargs):
        '''
        신간 도서 정보를 반환하는 Endpoint

        Args:
            count (int, optional): 조회할 도서 수 (Default: DEFAULT_BOOK_COUNT)
        '''
        count = self.request.query_params.get('count', None)
        if count is None:
            count = self.DEFAULT_BOOK_COUNT

        # 신간 정보 요청
        recent_books = Book.objects.order_by('-published_date')[:int(count)]
        response_serializer = ListResponseSerializer(data={
            'status': 'success',
            'message': 'Success message',
            'data': BookSerializer(recent_books, many=True).data
        })
        response_serializer.is_valid(raise_exception=True)
        # 신간 정보 반환
        return Response(status=status.HTTP_200_OK, data=response_serializer.validated_data)
