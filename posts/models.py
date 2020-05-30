from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField("Group name", max_length=200, unique=True)
    slug = models.SlugField("Link", unique=True)
    description = models.TextField("Group description")

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="author_posts")
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="group_posts")
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author_comments"
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    
    

