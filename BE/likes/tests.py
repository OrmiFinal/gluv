from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from likes.models import Like
from posts.models import CommunityPost
from teams.models import Team
from recruits.models import RecruitmentPost


class TestLikeModel(TestCase):
    '''
    좋아요 모델 테스트

    Detail:
        커뮤니티 게시글, 모집 게시글에 대한 좋아요 요청 테스트
        1~2. 각각 요청시 성공했는지 확인
        3. 오류로 인해 커뮤니티 게시글, 모집 게시글 id가 동시에 들어갔을 때에 대한 오류 확인
        4. 이미 좋아요 된 게시글에 대한 post 요청 오류 확인
        5. 같은 게시글에 두 번 post 요청 시도 시 중복 에러 확인
        6. 좋아요 해제 확인
        7. 내가 해당 포스트에 좋아요했는지 여부 확인
        8. 해당 포스트의 좋아요 수 확인
    '''
    def setUp(self) -> None:
        self.client = APIClient()

        self.users = []
        for i in range(1, 6):
            user = get_user_model().objects.create_user(
                email=f'testuserfor{i}@example.com',
                password=f'testpwfor{i}',
                region=f'testfor{i}',
                nickname=f'TestUserfor{i}'
            )
            self.users.append(user)

        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpw111',
            region='test',
            nickname='TestUser'
        )
        self.user2 = get_user_model().objects.create_user(
            email='testuser22@example.com',
            password='testpw222',
            region='test',
            nickname='TestUser2'
        )
        self.community_post = CommunityPost.objects.create(
            author=self.user2,
            title='Community Test',
            category='notice',
            content='CommunityPost Test'
        )
        self.community_post2 = CommunityPost.objects.create(
            author=self.user2,
            title='Community Test2',
            category='notice2',
            content='CommunityPost Test2'
        )
        self.team = Team.objects.create(
            name='TestTeam',
            category='독서모임',
            is_closed=False,
            location='Test',
            max_attendance=10,
            current_attendance=0,
            introduce='Test',
            image=None
        )
        self.recruitment_post = RecruitmentPost.objects.create(
            team=self.team,
            author=self.user2,
            title='Recruitment Test',
            content='RecruitmentPost Test'
        )

    
        self.like1 = Like.objects.create(user=self.user, community_post=self.community_post2)
        self.like2 = Like.objects.create(user=self.user2, community_post=self.community_post2)

        self.client.force_authenticate(user=self.user)


    def tearDown(self) -> None:
        return super().tearDown()

    def test_like_community_post(self):
        # 1. 커뮤니티 게시글에 대한 좋아요 성공 확인
        url = '/likes/api/like_post/'
        data = {'post_id': self.community_post.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # like가 생성되었는지 확인
        like = Like.objects.get(user=self.user, community_post=self.community_post)
        self.assertIsNotNone(like)
        self.assertEqual(like.recruitment_post, None)

    def test_like_recruitment_post(self):
        # 2. 모집 게시글에 대한 좋아요 성공 확인
        url = '/likes/api/like_post/'
        data = {'recruit_id': self.recruitment_post.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # like가 생성되었는지 확인
        like = Like.objects.get(user=self.user, recruitment_post=self.recruitment_post)
        self.assertIsNotNone(like)
        self.assertEqual(like.community_post, None)

    def test_like_both_post(self):
        # 3. 오류로 인해 커뮤니티 게시글, 모집 게시글 id가 동시에 들어갔을 때에 대한 오류 확인
        url = '/likes/api/like_post/'
        data = {'recruit_id': self.recruitment_post.id, 'post_id': self.community_post.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        
        # 4. 이미 좋아요 된 게시글에 대한 post 요청 오류 확인
        # 잘못된 요청에 대해 like객체가 생성되지 않았음을 확인
        with self.assertRaises(Like.DoesNotExist):
            Like.objects.get(user=self.user, recruitment_post=self.recruitment_post)
        with self.assertRaises(Like.DoesNotExist):
            Like.objects.get(user=self.user, community_post=self.community_post)

    def test_like_double_post(self):
        # 5. 같은 게시글에 두 번 post 요청 시도 시 중복 에러 확인
        url = '/likes/api/like_post/'
        data = {'post_id': self.community_post.id}
        
        # 첫 번째 좋아요
        response1 = self.client.post(url, data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # 두 번째 좋아요 시도
        response2 = self.client.post(url, data)
        # 중복해서 좋아요를 누르면 에러 반환
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 해당 게시글에 대한 like가 추가로 생성된 것은 아닌지 확인
        like_count = Like.objects.filter(user=self.user, community_post=self.community_post).count()
        self.assertEqual(like_count, 1)

    def test_unlike_post(self):
        # 6. 좋아요 해제 확인
        # 내가 해당 포스트에 좋아요했는지 여부 확인
        url_is_liked = f'/likes/api/is_liked/?post_id={self.community_post.id}'
        response_is_liked = self.client.get(url_is_liked)
        self.assertEqual(response_is_liked.status_code, status.HTTP_200_OK)
        self.assertEqual(response_is_liked.data['is_liked'], False)  # 초기에는 좋아요를 누르지 않았으므로 False로 확인

        # 좋아요 누르기
        url_like_post = '/likes/api/like_post/'
        data_like_post = {'post_id': self.community_post.id}
        response_like_post = self.client.post(url_like_post, data_like_post)
        self.assertEqual(response_like_post.status_code, status.HTTP_200_OK)

        # 내가 해당 포스트에 좋아요했는지 여부 확인
        url_is_liked = f'/likes/api/is_liked/?post_id={self.community_post.id}'
        response_is_liked2 = self.client.get(url_is_liked)
        self.assertEqual(response_is_liked2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_is_liked2.data['is_liked'], True)  # 초기에는 좋아요를 누르지 않았으므로 False로 확인

        # 좋아요가 제거
        url_unlike_post = '/likes/api/unlike_post/'
        data_unlike_post = {'post_id': self.community_post.id}
        response_unlike_post = self.client.post(url_unlike_post, data_unlike_post)
        self.assertEqual(response_unlike_post.status_code, status.HTTP_200_OK)

        # 좋아요가 제거되었는지 확인
        url_is_liked = f'/likes/api/is_liked/?post_id={self.community_post.id}'
        response_is_liked3 = self.client.get(url_is_liked)
        self.assertEqual(response_is_liked3.status_code, status.HTTP_200_OK)
        self.assertEqual(response_is_liked3.data['is_liked'], False) 


    def test_is_liked(self):
        # 7. 내가 해당 포스트에 좋아요했는지 여부 확인
        url = f'/likes/api/is_liked/?post_id={self.community_post.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_liked'], False)  # 초기에는 좋아요를 누르지 않았으므로 False로 확인

        # 좋아요 누르기
        self.client.post('/likes/api/like_post/', {'post_id': self.community_post.id})

        # 확인
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_liked'], True)

    

    def test_like_count(self):
        # 8. 해당 포스트의 좋아요 수 확인
        url = f'/likes/api/like_count/?post_id={self.community_post.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 0)  # 초기에는 좋아요를 누르지 않았으므로 0으로 확인

        # 좋아요 누르기
        self.client.post('/likes/api/like_post/', {'post_id': self.community_post.id})

        # 확인
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

      
        # 다시 확인
        url = f'/likes/api/like_count/?post_id={self.community_post2.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 2)  # 초기에는 좋아요 5개 확인
