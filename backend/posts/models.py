from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


User = settings.AUTH_USER_MODEL
# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    

class Post(models.Model):
    title = models.CharField(max_length=45)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_tags(self):
        return self.tags.count()


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts_liked')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'post')
        
    def __str__(self) -> str:
        return f'{self.user} liked the {self.post} post'  


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f'Comment | {self.author} -> {self.post}'


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_liked')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    class Meta:
        unique_together = ('user', 'comment')
            
    def __str__(self) -> str:
        return f'{self.user} liked the {self.comment} comment'

