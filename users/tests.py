from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User, Post
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
