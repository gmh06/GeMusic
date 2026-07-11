import os
import json
import sys
import shutil
from datetime import datetime
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), 'GeMusic_site'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GeMusic_site.settings')

import django
django.setup()

from GeMusic.models import Singer, Song, SingerSong


def import_singers(data_dir):
    singers_dir = os.path.join(data_dir, 'singers')
    if not os.path.exists(singers_dir):
        print(f"Error: Singer data directory not found: {singers_dir}")
        return 0
    
    singer_mids = [mid for mid in os.listdir(singers_dir) if os.path.isdir(os.path.join(singers_dir, mid))]
    count = 0
    
    for mid in tqdm(singer_mids, desc="Importing singers data", unit="singers"):
        info_path = os.path.join(singers_dir, mid, 'info.json')
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                singer, created = Singer.objects.update_or_create(
                    mid=mid,
                    defaults={
                        'name': data.get('name', ''),
                        'intro': data.get('intro'),
                        'num_songs': data.get('num_songs'),
                        'num_albums': data.get('num_albums'),
                        'num_movies': data.get('num_movies'),
                        'num_followers': data.get('num_followers')
                    }
                )
                
                if created:
                    count += 1
            
            except Exception as e:
                tqdm.write(f"Error importing singer {mid}: {str(e)}")
    
    print(f"\n Loaded {count} singers")
    return count


def import_songs(data_dir):
    """Import song data"""
    songs_dir = os.path.join(data_dir, 'songs')
    if not os.path.exists(songs_dir):
        print(f"Error: Song data directory not found: {songs_dir}")
        return 0
    
    song_mids = [mid for mid in os.listdir(songs_dir) if os.path.isdir(os.path.join(songs_dir, mid))]
    count = 0
    
    for mid in tqdm(song_mids, desc="Importing songs data", unit="songs"):
        info_path = os.path.join(songs_dir, mid, 'info.json')
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 处理发行日期
                release_date = None
                if data.get('release_date'):
                    try:
                        release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                # 创建或更新歌曲记录
                song, created = Song.objects.update_or_create(
                    mid=mid,
                    defaults={
                        'name': data.get('name', ''),
                        'intro': data.get('intro'),
                        'album': data.get('album'),
                        'language': data.get('language'),
                        'style': data.get('style'),
                        'release_date': release_date,
                        'lyrics': json.dumps(data.get('lyrics', [])),
                        'num_comments': data.get('num_comments')
                    }
                )
                
                # 建立歌手-歌曲关联
                if data.get('singer_mid'):
                    for singer_mid in data['singer_mid']:
                        try:
                            singer = Singer.objects.get(mid=singer_mid)
                            SingerSong.objects.get_or_create(singer=singer, song=song)
                        except Singer.DoesNotExist:
                            pass
                
                if created:
                    count += 1
            
            except Exception as e:
                tqdm.write(f"Error importing song {mid}: {str(e)}")
    
    print(f"\n Loaded {count} songs")
    return count


def import_singer_images(data_dir, static_dir):
    """Import singer profile images"""
    singers_dir = os.path.join(data_dir, 'singers')
    target_dir = os.path.join(static_dir, 'singers')
    
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)
    
    if not os.path.exists(singers_dir):
        print(f"Error: Singer data directory not found: {singers_dir}")
        return 0
    
    singer_mids = [mid for mid in os.listdir(singers_dir) if os.path.isdir(os.path.join(singers_dir, mid))]
    count = 0
    
    for mid in tqdm(singer_mids, desc="Importing singer images", unit="images"):
        src_path = os.path.join(singers_dir, mid, 'img.jpg')
        dst_path = os.path.join(target_dir, f'{mid}.jpg')
        
        if os.path.exists(src_path):
            try:
                shutil.copy2(src_path, dst_path)
                count += 1
            except Exception as e:
                tqdm.write(f"Error copying singer image {mid}: {str(e)}")
    
    print(f"\n Loaded {count} images")
    return count


def import_song_images(data_dir, static_dir):
    """Import song cover images"""
    songs_dir = os.path.join(data_dir, 'songs')
    target_dir = os.path.join(static_dir, 'songs')
    
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)
    
    if not os.path.exists(songs_dir):
        print(f"Error: Song data directory not found: {songs_dir}")
        return 0
    
    song_mids = [mid for mid in os.listdir(songs_dir) if os.path.isdir(os.path.join(songs_dir, mid))]
    count = 0
    
    for mid in tqdm(song_mids, desc="Importing song cover images", unit="images"):
        src_path = os.path.join(songs_dir, mid, 'picture.jpg')
        dst_path = os.path.join(target_dir, f'{mid}.jpg')
        
        if os.path.exists(src_path):
            try:
                shutil.copy2(src_path, dst_path)
                count += 1
            except Exception as e:
                tqdm.write(f"Error copying song cover image {mid}: {str(e)}")
    
    print(f"\n Loaded {count} images")
    return count


def main():
    data_dir = "crawler/data"
    static_dir = os.path.join(os.path.dirname(__file__), 'GeMusic_site', 'GeMusic', 'static')
    
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found: {data_dir}")
        return
    
    print("=" * 60)
    print("GeMusic Data migration script - Importing crawler/data into Django database")
    print("=" * 60)
    print(f"GeMusic Data directory path: {data_dir}")
    print(f"GeMusic Static resource directory path: {static_dir}")
    print()
    
    # 导入歌手数据
    print("📥 Importing singer data...")
    singer_count = import_singers(data_dir)
    
    # 导入歌曲数据
    print("\n📥 Importing song data...")
    song_count = import_songs(data_dir)
    
    # 导入歌手头像
    print("\n📷 Importing singer images...")
    singer_img_count = import_singer_images(data_dir, static_dir)
    
    # 导入歌曲封面
    print("\n📷 Importing song cover images...")
    song_img_count = import_song_images(data_dir, static_dir)
    
    print()
    print("=" * 60)
    print("GeMusic Data Migration completed!")
    print("GeMusic Data statistics:")
    print(f"  - Singers: {singer_count}")
    print(f"  - Songs: {song_count}")
    print(f"  - Singer Images: {singer_img_count}")
    print(f"  - Song Covers: {song_img_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()