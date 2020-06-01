from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User, Post


class ProfileTest(TestCase):
    def setUp(self):
        # создание тестового клиента
        self.client = Client()
        # создание первого пользователя
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
        # создание третьего пользователя
        self.user3 = User.objects.create_user(
            username="crackle3",
            email="crackle3@crackle.com",
            password="s12crac##kle3453"
        )
        # создаём пост от имени первого пользователя
        self.post = Post.objects.create(
            text="user: 7oB@!lcntidF%9$^Y",
            author=self.user
        )
        # создаём пост от имени второго пользователя
        self.post = Post.objects.create(
            text="user2: IY#$7Sa0@55Q5M1Kv",
            author=self.user2
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

    def test_following_login(self):
        # у авторизованного пользователя при просмотре
        # чужого профиля до подписания есть кнопка "Подписаться"
        self.client.force_login(self.user)
        url = reverse(
            "profile_view",
            kwargs={'username': self.user2.username}
            )
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'Подписаться')
        # при нажатии на кнопку "Подписаться"
        url = reverse(
            "profile_follow",
            kwargs={'username': self.user2}
        )
        # попадаем на страницу избранного
        page_text = "Последние обновления авторов, на которые вы подписаны"
        response = self.client.get(url, follow=True)
        self.assertContains(response, page_text)
        # и на этой странице опубликован текст поста user2
        page_text = "user2: IY#$7Sa0@55Q5M1Kv"
        self.assertContains(response, page_text)
        # и нет текста поста первого user'а
        page_text = "user: 7oB@!lcntidF%9$^Y"
        self.assertNotContains(response, page_text)
        # проверм состояние подписок
        # первый пользователь подписался на второго
        # у первого подписчиков нет
        self.assertEqual(self.user.following.count(), 0)
        # у первого подписок одна
        self.assertEqual(self.user.follower.count(), 1)
        # у второго подписчик один
        self.assertEqual(self.user2.following.count(), 1)
        # у второго подписок нет
        self.assertEqual(self.user2.follower.count(), 0)

    def test_unfollowing_login(self):
        self.client.force_login(self.user)
        # при нажатии на кнопку "Отписаться"
        url = reverse(
            "profile_unfollow",
            kwargs={'username': self.user2}
        )
        # попадаем на страницу избранного
        # поскольку активых подписок нет
        page_text = "Вы пока ни на кого не подписаны"
        response = self.client.get(url, follow=True)
        self.assertContains(response, page_text)
        # на этой странице уже не опубликован пост user2
        page_text = "user2: IY#$7Sa0@55Q5M1Kv"
        self.assertNotContains(response, page_text)
        # и по прежнему нет текста поста первого user'а
        page_text = "user: 7oB@!lcntidF%9$^Y"
        self.assertNotContains(response, page_text)
        # проверм состояние подписок
        # первый пользователь отписался от второго
        # у первого подписчиков нет
        self.assertEqual(self.user.following.count(), 0)
        # у первого нет подписок
        self.assertEqual(self.user.follower.count(), 0)
        # у второго подписчиков нет
        self.assertEqual(self.user2.following.count(), 0)
        # у второго подписок нет
        self.assertEqual(self.user2.follower.count(), 0)

    def test_third_user(self):
        # третий подписался на первого и не подписаля не второго
        self.client.force_login(self.user3)
        url = reverse(
            "profile_follow",
            kwargs={'username': self.user}
        )
        response = self.client.get(url, follow=True)
        # он видит в своей ленте пост первого
        page_text = "user: 7oB@!lcntidF%9$^Y"
        self.assertContains(response, page_text)
        # и не видит в своей ленте пост второго
        page_text = "user2: IY#$7Sa0@55Q5M1Kv"
        self.assertNotContains(response, page_text)
        # первый создал новый пост
        self.client.force_login(self.user)
        url = reverse("new_post")
        new_post_user = "user: new post by user"
        response = self.client.post(
            url,
            data={'text': new_post_user},
            follow=True
        )
        # и второй создал новый пост
        self.client.force_login(self.user2)
        url = reverse("new_post")
        new_post_user2 = "user2: new post by user2"
        response = self.client.post(
            url,
            data={'text': new_post_user2},
            follow=True
        )
        # на странице избранного третьего пользователя
        self.client.force_login(self.user3)
        url = reverse("follow_index")
        response = self.client.get(url, follow=True)
        # виден новый пост первого
        self.assertContains(response, new_post_user)
        # и не виден новый пост второго
        self.assertNotContains(response, new_post_user2)

    def test_following_logout(self):
        # у неавторизованного пользователя отсутствуют
        # кнопки "Подписаться" или "Отписаться"
        self.client.logout()
        url = reverse(
            "profile_view",
            kwargs={'username': self.user2.username}
            )
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, 'Подписаться')
        self.assertNotContains(response, 'Отписаться')
        # при попытке перейти на страницу /follow/
        # неаторизованный попадает на страницу авторизации
        url = '/follow/'
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')
