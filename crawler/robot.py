import random
import os
import requests
import json
import textwrap
import asyncio
from tqdm import tqdm
from playwright.async_api import async_playwright
from get_singers import get_singers, get_singer_info
from get_songs import get_song_info

def format_status(label, value):
    text = "" if value is None else str(value)
    text = textwrap.shorten(text, width=48, placeholder="...")
    return f"{label:<{14}}: {text}"


def storage_state_to_cookie_header(storage_state):
    cookies = storage_state.get("cookies", []) if storage_state else []
    cookie_str = "; ".join(f"{cookie.get('name', '')}={cookie.get('value', '')}" for cookie in cookies if cookie.get("name"))
    
    return cookie_str


async def login(config_path="config.json", login_url="https://y.qq.com"):
    with open("UA_list.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(login_url, wait_until="networkidle", timeout=60000)
        await asyncio.to_thread(input, "Please log in in the opened browser window, then press Enter here to save the cookie.")

        storage_state = await context.storage_state()
        config["cookie"] = storage_state
        config["Cookie"] = storage_state_to_cookie_header(storage_state)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        await page.close()
        await browser.close()

    print(f"Cookie saved to {config_path}.")


async def robot(headers):
    folder_path = "data"
    singer_list_url = "https://y.qq.com/n/ryqq_v2/singer_list"
    singer_url = "https://y.qq.com/n/ryqq_v2/singer/"
    song_url = "https://y.qq.com/n/ryqq_v2/songDetail/"
    max_song_concurrency = 4
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(headers["UA_list"]),
            storage_state=headers["cookie"])
        
        # get singers list
        singers_list_content = await get_content_with_scroll(context, singer_list_url)
        
        singers = get_singers(singers_list_content)
        
        os.makedirs(folder_path, exist_ok=True)
        singers_list_path = os.path.join(folder_path, "singers_list.json")
            
        with open(singers_list_path, "w", encoding="utf-8") as f:
            json.dump(singers, f, ensure_ascii=False, indent=4)
        
        print(f"Save {len(singers)} singers.")
        
        singers_path = os.path.join(folder_path, "singers")
        os.makedirs(singers_path, exist_ok=True)
        songs_path = os.path.join(folder_path, "songs")
        os.makedirs(songs_path, exist_ok=True)
          

        
        songs = set()
          
        with tqdm(singers.keys(), desc="Getting singers info", unit="singer", position=0, dynamic_ncols=True) as bar, \
            tqdm(total=0, position=1, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_name, \
            tqdm(total=0, position=2, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_followers, \
            tqdm(total=0, position=3, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_songs, \
            tqdm(total=0, position=4, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_albums, \
            tqdm(total=0, position=5, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_movies:

            line_name.set_description_str(format_status("Name", "waiting to start"))
            line_followers.set_description_str(format_status("Followers", "waiting to start"))
            line_songs.set_description_str(format_status("Songs", "waiting to start"))
            line_albums.set_description_str(format_status("Albums", "waiting to start"))
            line_movies.set_description_str(format_status("MVs", "waiting to start"))

            # get each singer's information
            for mid in bar:
                
                singer_path = os.path.join(singers_path, mid)
                
                os.makedirs(singer_path, exist_ok=True)
                singer_content = await get_content(context, singer_url + mid)
                if singer_content is None:
                    continue
                singer_info, portrait_url = get_singer_info(singer_content, mid, singers)
                
                line_name.set_description_str(format_status("Name", singer_info.get('name', singers.get(mid, mid))))
                line_followers.set_description_str(format_status("Followers", singer_info.get('num_followers', 0)))
                line_songs.set_description_str(format_status("Songs", singer_info.get('num_songs', 0)))
                line_albums.set_description_str(format_status("Albums", singer_info.get('num_albums', 0)))
                line_movies.set_description_str(format_status("MVs", singer_info.get('num_movies', 0)))
                
                if portrait_url:
                    await get_img(
                        portrait_url,
                        {"Cookie": headers["Cookie"], 
                         "User-Agent": random.choice(headers["UA_list"])} ,
                        os.path.join(singer_path, "img.jpg")
                    )
                    
                song_ids = singer_info.get("popular_songs") or []

                with tqdm(total=len(song_ids), desc="Getting songs info", unit="song", position=6, leave=False, dynamic_ncols=True) as song_bar, \
                    tqdm(total=0, position=7, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_title, \
                    tqdm(total=0, position=8, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_singer, \
                    tqdm(total=0, position=9, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_album, \
                    tqdm(total=0, position=10, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_comments, \
                    tqdm(total=0, position=11, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_language, \
                    tqdm(total=0, position=12, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_style, \
                    tqdm(total=0, position=13, bar_format="{desc}", leave=False, dynamic_ncols=True) as line_release_date:

                    line_title.set_description_str(format_status("Title", "waiting to start"))
                    line_singer.set_description_str(format_status("Singer", "waiting to start"))
                    line_album.set_description_str(format_status("Album", "waiting to start"))
                    line_comments.set_description_str(format_status("Comments", "waiting to start"))
                    line_language.set_description_str(format_status("Language", "waiting to start"))
                    line_style.set_description_str(format_status("Style", "waiting to start"))
                    line_release_date.set_description_str(format_status("Release Date", "waiting to start"))

                    valid_songs = []

                    semaphore = asyncio.Semaphore(max_song_concurrency)
                    tasks = [
                        asyncio.create_task(
                            process_song(
                                song_id,
                                context,
                                song_url,
                                songs_path,
                                headers,
                                semaphore,
                            )
                        )
                        for song_id in song_ids
                    ]

                    for task in asyncio.as_completed(tasks):
                        song_mid, song_info, picture_url, is_valid = await task
                        song_bar.update(1)

                        if is_valid:
                            valid_songs.append(song_mid)

                        line_title.set_description_str(format_status("Title", song_info["name"]))
                        line_singer.set_description_str(format_status("Singer", ", ".join(song_info["singer"] or [])))
                        line_album.set_description_str(format_status("Album", song_info["album"]))
                        line_comments.set_description_str(format_status("Comments", song_info["num_comments"]))
                        line_language.set_description_str(format_status("Language", song_info["language"]))
                        line_style.set_description_str(format_status("Style", song_info["style"]))
                        line_release_date.set_description_str(format_status("Release Date", song_info["release_date"]))
                        
                singer_info["popular_songs"] = valid_songs
                songs.update(valid_songs)
            
                with open(os.path.join(singer_path, "info.json"), "w", encoding="utf-8") as f:
                    json.dump(singer_info, f, ensure_ascii=False, indent=4)
                    
        with open(os.path.join(folder_path, "songs_list.json"), "w", encoding="utf-8") as f:
            json.dump(list(songs), f, ensure_ascii=False, indent=4)
            
        print(f"Save {len(songs)} songs.")

        await browser.close()


async def process_song(song_mid, context, song_url, songs_path, headers, semaphore):
    async with semaphore:
        song_content = await get_content(context, song_url + song_mid)

        if song_content is None:
            return song_mid, {"name": None, "singer": [], "album": None, "num_comments": None, "language": None, "style": None, "release_date": None}, None, False

        song_info, picture_url = get_song_info(song_content, song_mid)

        if song_info["name"] is None:
            return song_mid, song_info, picture_url, False

        song_path = os.path.join(songs_path, song_mid)
        os.makedirs(song_path, exist_ok=True)

        if picture_url:
            await get_img(
                picture_url,
                {"Cookie": headers["Cookie"],
                 "User-Agent": random.choice(headers["UA_list"])} ,
                os.path.join(song_path, "picture.jpg")
            )

        with open(os.path.join(song_path, "info.json"), "w", encoding="utf-8") as f:
            json.dump(song_info, f, ensure_ascii=False, indent=4)

        return song_mid, song_info, picture_url, True




async def get_content_with_scroll(context, url, scrolls=2):
    page = await context.new_page()
        
    await page.goto(url=url, wait_until="networkidle", timeout=30000)
        
    await page.wait_for_timeout(random.uniform(500, 1000))
        
    for i in range(scrolls):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
            
    content = await page.content()
    
    await page.close()
        
    return content


async def get_content(context, url):
    page = await context.new_page()
    
    for attempt in range(3):
        try:
            await page.goto(url=url, wait_until="networkidle", timeout=30000)
            break
        except Exception:
            if attempt < 2:
                await page.wait_for_timeout(random.uniform(1000, 2000))
                
            else:
                await page.close()
                with open("error_log.txt", "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                return None
        
    await page.wait_for_timeout(random.uniform(500, 1000))
        
    content = await page.content()
    
    await page.close()

    return content


def _save_binary_file(save_path, data):
    with open(save_path, "wb") as f:
        f.write(data)


async def get_img(img_url, headers, save_path):
    """
    Get the image from img_url and save it to save_path.
    """
    img_content = await asyncio.to_thread(lambda: requests.get(img_url, headers=headers).content)
    await asyncio.to_thread(_save_binary_file, save_path, img_content)
    await asyncio.sleep(random.uniform(1, 2))