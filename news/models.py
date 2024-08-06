from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.urls import reverse

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


    def update_rating(self):
        posts_rating = self.posts.aggregate(pr=Coalesce(Sum('rating'), 0)).get('pr')
        comments_rating = self.user.comments.aggregate(cr=Coalesce(Sum('rating'), 0)).get('cr')
        posts_comments_rating = self.posts.aggregate(pcr=Coalesce(Sum('comment__rating'), 0)).get('pcr')

        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating
        self.save()


class Category (models.Model):
    duels = 'DUEL'
    poetry = 'POET'
    prose = 'PROS'
    culture = 'CULT'
    CatTheme = [
        (duels, 'Дуэли'),
        (poetry, 'Поэзия'),
        (prose, 'Проза'),
        (culture, 'Культура')
    ]
    theme = models.CharField(
        max_length=4,
        choices=CatTheme,
        unique=True)
    subscribers = models.ManyToManyField(User, blank = True, related_name='categories')


    def __str__(self):
        return self.theme.title()


class Post (models.Model):
    news = 'NE'
    article = 'AR'
    Positions = [
        (news, 'Новости'),
        (article, 'Публикации')
    ]
    head = models.CharField(max_length=200)
    text = models.TextField()
    position = models.CharField(
        max_length=2,
        choices=Positions,
        default=news)
    timing_post = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_category = models.ManyToManyField(Category, through='PostCategory')
    rating = models.IntegerField(default=0)

    def dislike(self):
        self.rating -= 1
        self.save()

    def like(self):
        self.rating += 1
        self.save()


    def preview(self):
        prev = self.text[0:125] + "..."
        return prev

    def __str__(self):
        return f'{self.head.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory (models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    head = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    head = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text_comment = models.TextField()
    timing_comment = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def dislike(self):
        self.rating -= 1
        self.save()

    def like(self):
        self.rating += 1
        self.save()