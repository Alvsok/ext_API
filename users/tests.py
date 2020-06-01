from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User, Post, Follow
from posts import views


class ProfileTest(TestCase):
    def setUp(self):
        # создание тестового клиента
        self.client = Client()
        # создание пользователя
        self.user = User.objects.create_user(
            username="crackle",
            email="crackle@crackle.com",
            password="s12crac##kle345"
        )
        # создание второго пользователя
        self.user2 = User.objects.create_user(
            username="crackle2",
            email="crackle2@crackle.com",
            password="s12crac##kle3452"
        )

        '''
        self.follow = Follow.objects.create(
            user=self.user2,
            author=self.user
        )
        '''

    def test_new_profile(self):
        url = reverse(
            "profile_view",
            kwargs={'username': self.user.username}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_redirect_logout(self):
        self.client.logout()
        url = reverse("new_post")
        response = self.client.get(url)
        # разлогиненый при попытке создать пост
        # попадает на страницу авторизации
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')
'''
    def test_following_login(self):
        self.client.force_login(self.user)
        #url = reverse(
        #    "profile_follow",
        #    kwargs={'username': self.user.username,}
        #)

        url = reverse(
            "profile_view",
            kwargs={'username': self.user2.username}
            )
        response = self.client.get(url, follow=True)
        
        #for elem in response:
        #    print(elem)

        self.assertEqual(response.status_code, 200)



        # проверить наличие пдписок - должрно быть 0
        # нажал на кнопку подписаться  -- вот это пока не ясно!!!
        # на самом деле = это вызов функции profile_follow с параметром "profile.username" !!!!!!!!
        # проверить наличие пдписок - должрна быть 1
        # ДОП ВАРИАНТ у user2 пявился подписчик
        # нажал на кнопку отписаться
        # проверить наличие пдписок - должрна быть 0
        # ДОП ВАРИАНТ у user2 подписчиков стало 0


'''































