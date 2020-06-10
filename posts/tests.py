from time import sleep
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from .models import User, Post, Group


class ProfileTest(TestCase):
    def setUp(self):
        # создание тестового клиента
        self.client = Client()
        # создание первого пользователя
        self.user = User.objects.create_user(
            username='crackle',
            email='crackle@crackle.com',
            password='s12crac##kle345'
        )
        # создание второго пользователя.
        self.user2 = User.objects.create_user(
            username='crackle2',
            email='crackle2@crackle.com',
            password='s12crac##kle3452'
        )
        # создание группы
        self.group = Group.objects.create(
            title='Test group title',
            slug='group_test',
            description='Test group description'
        )

        # создаём пост от имени пользователя
        self.post = Post.objects.create(
            text='Django is a high-level Python Web framework',
            group=self.group,
            author=self.user
        )

    def test_new_post_in_home_page(self):
        """
        Проверка видимости нового поста на главной странице
        """
        url = reverse('index')
        cache.clear()
        response = self.client.get(url)
        self.assertEqual(
            response.context['page'][0].text,
            self.post.text
        )

    def test_new_post_in_post_page(self):
        """
        Проверка видимости нового поста на странице поста
        """
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        response = self.client.get(url)
        self.assertEqual(
            response.context['article'].text,
            self.post.text
        )

    def test_new_post_in_user_page(self):
        """
        Проверка видимости нового поста на странице пользователя
        """
        url = reverse(
            'profile_view',
            kwargs={'username': self.user.username}
        )
        response = self.client.get(url)
        self.assertEqual(
            response.context['page'][0].text,
            self.post.text
        )

    def test_create_login(self):
        """
        Проверка создания нового поста залогиненным пользователем
        и видимость этого поста на разных страницах сайта
        """
        self.client.force_login(self.user)
        url = reverse('new_post')
        new_post = 'This is a new post'
        response = self.client.post(
            url,
            data={'text': new_post},
            follow=True
        )
        # видно на главной странице
        url = reverse('index')
        response = self.client.get(url)
        self.assertContains(response, new_post)
        # создалась новая страница поста
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 2}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # видно на странице поста
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 2}
        )
        response = self.client.get(url)
        self.assertEqual(
            response.context['article'].text,
            new_post
        )
        # видно на странице пользователя
        url = reverse(
            'profile_view',
            kwargs={'username': self.user.username}
        )
        response = self.client.get(url)
        self.assertEqual(
            response.context['page'][0].text,
            new_post
        )

    def test_edit_posts(self):
        """
        Проверка изменения поста залогиненным пользователем
        и видимость этого изменения на разных страницах сайта
        """
        self.client.force_login(self.user)
        url = reverse(
            'post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        new_text = 'Modified text'
        response = self.client.post(
            url,
            data={'text': new_text},
            follow=True
        )
        # изменения видны на главной странице
        url = reverse('index')
        cache.clear()
        response = self.client.get(url)
        self.assertEqual(
            response.context['page'][0].text,
            new_text
        )
        # изменения видны на странице поста
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        response = self.client.get(url)
        self.assertEqual(
            response.context['article'].text,
            new_text
        )
        # изменения видны на странице профайла
        url = reverse(
            'profile_view',
            kwargs={'username': self.user.username}
        )
        response = self.client.get(url)
        self.assertEqual(
            response.context['page'][0].text,
            new_text
        )

    def test_edit_posts_another_user(self):
        """
        Проверка попытки изменения поста не его автором
        и реакция программы на такую попытку
        """
        # не автор поста при попытке редактировать пост
        # редиректится на страницу показа этого поста
        self.client.force_login(self.user2)
        url = reverse(
            'post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        response = self.client.get(url, follow=True)
        target_url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        self.assertRedirects(
            response,
            target_url
        )

    # проверка редиректа fake pages на 404
    def test_impossible_page(self):
        url = reverse(
            'profile_view',
            kwargs={'username': 'ffffff'}
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_is_image(self):
        """
        Проверка создания нового поста с картинкой залогиненным пользователем
        и видимость картинки разных страницах сайта
        """
        self.client.force_login(self.user)
        url = reverse(
            'post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        new_text = 'Here is the picture now'
        path_img = 'media/posts/la1_2.jpg'
        with open(path_img, 'rb') as img:
            response = self.client.post(
                url,
                data={
                    'text': new_text,
                    'group': 1,
                    'image': img
                },
                follow=True
            )
        # картинка видна на странице записи
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        response = self.client.get(url)
        self.assertContains(response, 'img class="card-img"')
        # картинка видна на главной странице
        url = reverse('index')
        cache.clear()
        response = self.client.get(url)
        self.assertContains(response, 'img class="card-img"')
        # картинка видна на странице профайла
        url = reverse(
            'profile_view',
            kwargs={'username': self.user.username}
        )
        response = self.client.get(url)
        self.assertContains(response, 'img class="card-img"')
        # картинка видна на странице группы
        url = reverse(
            'group_posts',
            kwargs={'slug': self.group.slug}
        )
        response = self.client.get(url)
        self.assertContains(response, 'img class="card-img"')

    def test_load_non_image(self):
        """
        Проверка создания нового поста с картинкой залогиненным
        пользователем при том, что картинка не является графическим
        файлом, хоть и имеет расширение jpg. Проверка, на загрузку этого файла
        и появление тега изображения на странице.
        """
        self.client.force_login(self.user)
        url = reverse(
            'post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        new_text = 'Here loaded non picture file'
        # возьмем неграфический файл и переименуем его
        # расширение в jpg чтобы обмануть систему
        path_img = 'media/posts/f_la1.jpg'
        with open(path_img, 'rb') as img:
            response = self.client.post(
                url,
                data={
                    'text': new_text,
                    'group': 1,
                    'image': img
                },
                follow=True
            )
        # в случае удачной загрузки файла происходит
        # редирект на страницу поста. Если загрузка не
        # удалась, мы останемся на странице редактирования
        self.assertEqual(url, response.request['PATH_INFO'])
        # и никаких изображений в записи не появится
        self.assertNotContains(response, 'img class="card-img"')

    def test_kache_new_posts(self):
        """
        Проверка видимости нового поста на главной странце
        до и после чистки кэша
        """
        self.client.force_login(self.user)
        url = reverse('new_post')
        new_post = 'JCu9K^W1sM75dM9*@'
        response = self.client.post(
            url,
            data={'text': new_post},
            follow=True
        )
        # не видно на главной странице
        url = reverse('index')
        response = self.client.get(url)
        self.assertNotContains(response, new_post)
        # почистим кэш и новый текст станет виден на главной странице
        cache.clear()
        response = self.client.get(url)
        self.assertContains(response, new_post)

    def test_kache_time(self):
        """
        Проверка видимости нового поста на главной странце
        до и после прохождения времени кэширования
        """
        self.client.force_login(self.user)
        url = reverse('new_post')
        new_post = 'DR#4x@X97$7^kFr!l'
        response = self.client.post(
            url,
            data={'text': new_post},
            follow=True
        )
        # не видно на главной странице
        url = reverse('index')
        response = self.client.get(url)
        self.assertNotContains(response, new_post)
        # дадим время и новый текст станет виден на главной странице
        sleep(20)
        response = self.client.get(url)
        self.assertContains(response, new_post)

    def test_comments_one(self):
        """
        Проверка создания комментария залогиненным пользователем и
        невозможность создания комментария разлогиеннным пользователем
        """
        self.client.force_login(self.user)
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        new_comment = 'This is a new comment'
        url += 'comment/'
        response = self.client.post(
            url,
            data={'text': new_comment},
            follow=True
        )
        # снова формируем url поста
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        response = self.client.get(url)
        # и видим, что комментарий появился
        self.assertContains(response, new_comment)
        # разлогинимся
        self.client.logout()
        # после разлогинивания кнопка 'Отправить' отсутствует
        response = self.client.get(url)
        self.assertNotContains(
            response,
            '<button type="submit" class="btn btn-primary">Отправить</button>'
        )
        # при попытке сделать POST запрос со страницы
        # комментариев попадаем на страницу авторизации
        new_comment_logout = 'This is a new comment by logout'
        url += 'comment/'
        response = self.client.post(
            url,
            data={'text': new_comment},
            follow=True
        )
        self.assertTemplateUsed(response, 'registration/login.html')
        # нового коммента на страние нет
        url = reverse(
            'post_view',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            }
        )
        response = self.client.get(url)
        self.assertNotContains(response, new_comment_logout)
