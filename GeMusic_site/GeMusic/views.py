from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Value
from django.db.models.functions import Concat
import json
import time

from .models import Singer, Song, Comment

def index(request):
    """系统主页 - 歌曲列表页"""
    songs_list = Song.objects.all().order_by('-num_comments')
    paginator = Paginator(songs_list, 8)
    
    page = request.GET.get('page', 1)
    
    try:
        page_num = int(page)
        if page_num < 1:
            page_num = 1
        songs = paginator.page(page_num)
    except (PageNotAnInteger, ValueError):
        songs = paginator.page(1)
    except EmptyPage:
        songs = paginator.page(paginator.num_pages)
    
    return render(request, 'index.html', {
        'songs': songs,
        'paginator': paginator
    })


def song_detail(request, mid):
    """歌曲详情页"""
    song = get_object_or_404(Song, mid=mid)
    singers = song.singers.all()
    lyrics = json.loads(song.lyrics) if song.lyrics else []
    
    if request.method == 'POST':
        if 'comment_content' in request.POST:
            content = request.POST['comment_content'].strip()
            if content:
                Comment.objects.create(song=song, content=content)
                return redirect('song_detail', mid=mid)
        elif 'delete_comment' in request.POST:
            comment_id = request.POST['delete_comment']
            Comment.objects.filter(id=comment_id).delete()
            return redirect('song_detail', mid=mid)
    
    comments = song.comments.all()
    
    return render(request, 'song_detail.html', {
        'song': song,
        'singers': singers,
        'lyrics': lyrics,
        'comments': comments
    })


def singer_list(request):
    """歌手列表页"""
    sort_by = request.GET.get('sort', 'num_followers')
    sort_dir = request.GET.get('dir', 'desc')
    
    valid_fields = ['num_followers', 'num_songs', 'num_albums', 'name']
    if sort_by not in valid_fields:
        sort_by = 'num_followers'
    
    order_prefix = '-' if sort_dir == 'desc' else ''
    singers_list = Singer.objects.all().order_by(order_prefix + sort_by)
    paginator = Paginator(singers_list, 8)
    
    page = request.GET.get('page', 1)
    
    try:
        page_num = int(page)
        if page_num < 1:
            page_num = 1
        singers = paginator.page(page_num)
    except (PageNotAnInteger, ValueError):
        singers = paginator.page(1)
    except EmptyPage:
        singers = paginator.page(paginator.num_pages)
    
    sort_labels = {
        'num_followers': '粉丝数',
        'num_songs': '歌曲数',
        'num_albums': '专辑数',
        'name': '歌手名'
    }
    
    return render(request, 'singer_list.html', {
        'singers': singers,
        'paginator': paginator,
        'sort_by': sort_by,
        'sort_dir': sort_dir,
        'sort_label': sort_labels[sort_by]
    })


def singer_detail(request, mid):
    """歌手详情页"""
    singer = get_object_or_404(Singer, mid=mid)
    songs = singer.songs.all()
    
    return render(request, 'singer_detail.html', {
        'singer': singer,
        'songs': songs
    })


def search(request):
    """搜索页"""
    return render(request, 'search.html')


def search_results(request):
    """搜索结果页"""
    keyword = request.GET.get('keyword', '').strip()
    search_type = request.GET.get('search_type', 'song')
    
    start_time = time.time()
    
    results = []
    result_count = 0
    
    if keyword:
        if search_type == 'song':
            songs_by_name_singer = Song.objects.filter(
                Q(name__icontains=keyword) | Q(singers__name__icontains=keyword)
            ).distinct()

            songs_by_lyrics_ids = set()
            songs_with_lyrics = Song.objects.exclude(lyrics__isnull=True).exclude(lyrics='')
            for song in songs_with_lyrics:
                try:
                    lyrics_list = json.loads(song.lyrics)
                    if isinstance(lyrics_list, list):
                        lyrics_text = '\n'.join(str(line) for line in lyrics_list)
                        if keyword.lower() in lyrics_text.lower():
                            songs_by_lyrics_ids.add(song.mid)
                except (json.JSONDecodeError, TypeError):
                    if song.lyrics and keyword.lower() in song.lyrics.lower():
                        songs_by_lyrics_ids.add(song.mid)

            matched_mids = set(song.mid for song in songs_by_name_singer)
            matched_mids.update(songs_by_lyrics_ids)

            if matched_mids:
                songs = Song.objects.filter(mid__in=matched_mids).order_by('-num_comments')
                results = list(songs)
            else:
                results = []
            result_count = len(results)
        elif search_type == 'singer':
            singers = Singer.objects.filter(
                Q(name__icontains=keyword) | Q(intro__icontains=keyword)
            ).distinct()
            results = list(singers)
            result_count = len(results)
    
    end_time = time.time()
    search_time = round((end_time - start_time) * 1000, 2)
    
    paginator = Paginator(results, 10)
    page = request.GET.get('page', 1)
    
    try:
        page_num = int(page)
        if page_num < 1:
            page_num = 1
        page_results = paginator.page(page_num)
    except (PageNotAnInteger, ValueError):
        page_results = paginator.page(1)
    except EmptyPage:
        page_results = paginator.page(paginator.num_pages)
    
    return render(request, 'search_results.html', {
        'keyword': keyword,
        'search_type': search_type,
        'results': page_results,
        'result_count': result_count,
        'search_time': search_time,
        'paginator': paginator
    })