from django.db import models

# Create your models here.

class Singer(models.Model):
    """歌手模型"""
    mid = models.CharField(max_length=100, primary_key=True, verbose_name='mid')
    name = models.CharField(max_length=100, verbose_name='name')
    intro = models.TextField(null=True, blank=True, verbose_name='intro')
    num_songs = models.IntegerField(null=True, verbose_name='num_songs')
    num_albums = models.IntegerField(null=True, verbose_name='num_albums')
    num_movies = models.IntegerField(null=True, verbose_name='num_movies')
    num_followers = models.BigIntegerField(null=True, verbose_name='num_followers')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'singer'
        verbose_name_plural = 'singers'

class Song(models.Model):
    """歌曲模型"""
    mid = models.CharField(max_length=100, primary_key=True, verbose_name='mid')
    name = models.CharField(max_length=200, verbose_name='name')
    intro = models.TextField(null=True, blank=True, verbose_name='intro')
    album = models.CharField(max_length=200, null=True, blank=True, verbose_name='album')
    language = models.CharField(max_length=50, null=True, blank=True, verbose_name='language')
    style = models.CharField(max_length=100, null=True, blank=True, verbose_name='style')
    release_date = models.DateField(null=True, verbose_name='release_date')
    lyrics = models.TextField(null=True, blank=True, verbose_name='lyrics')
    num_comments = models.IntegerField(null=True, verbose_name='num_comments')

    # 多对多关系：一首歌曲可以有多个歌手（合唱），一个歌手有多首歌曲
    singers = models.ManyToManyField(Singer, through='SingerSong', related_name='songs')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'song'
        verbose_name_plural = 'songs'

class SingerSong(models.Model):
    """歌手-歌曲关联表（用于支持合唱场景）"""
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, verbose_name='singer')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name='song')
    
    class Meta:
        unique_together = ('singer', 'song')
        verbose_name = 'singer_song_association'
        verbose_name_plural = 'singer_song_associations'

class Comment(models.Model):
    """歌曲评论模型"""
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name='comment_content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    
    def __str__(self):
        return f"Comment on {self.song.name}"
    
    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ['-created_at']