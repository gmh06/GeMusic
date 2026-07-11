from bs4 import BeautifulSoup as BS
import re
        
def get_song_info(content, mid):
    """
    Get the information of a song from QQ music by mid, including:
        - name
        - picture of the song
        - song's mid
        - singer
        - singer's mid
        - introduction
        - album
        - language
        - style
        - release date
        - lyrics
        - number of comments
    """
    
    soup = BS(content, "lxml")
    
    song_info = {}
    
    if soup.find("div", class_="none_txt"):
        song_info["name"] = None
        song_info["mid"] = mid
        song_info["singer"] = None
        song_info["singer_mid"] = None
        song_info["intro"] = None
        song_info["album"] = None
        song_info["language"] = None
        song_info["style"] = None
        song_info["release_date"] = None
        song_info["lyrics"] = None
        song_info["num_comments"] = None
        
        return song_info, None
    
    # basic information
    song_info["name"] = soup.find("h1", class_="data__name_txt").get_text(strip=True)
    picture_url = soup.find("img", class_="data__photo").get("src", "")
    if picture_url:
        picture_url = "https:" + picture_url
    song_info["mid"] = mid
    song_singer = soup.find_all("a", class_="data__singer_txt")
    song_info["singer"] = [s.get_text(strip=True) for s in song_singer]
    song_info["singer_mid"] = [s.get("href", "").split("/")[-1] for s in song_singer]
    if soup.find("div", class_="about__cont"):
        song_info["intro"] = soup.find("div", class_="about__cont").get_text(strip=True)
    else:
        song_info["intro"] = None
    
    # details
    details = soup.find_all("li", class_="data_info__item_song")
    
    song_info["album"] = None
    song_info["language"] = None
    song_info["style"] = None
    song_info["release_date"] = None
    
    for item in details:
        k, v = item.get_text(strip=True).split("：", 1)
        match k:
            case "专辑":
                song_info["album"] = v
            case "语种":
                song_info["language"] = v
            case "流派":
                song_info["style"] = v
            case "发行时间":
                song_info["release_date"] = v
            case _:
                pass
            
    # lyrics
    lyrics = []
    lyric__cont_box = soup.find("div", class_="lyric__cont_box")
    if lyric__cont_box:
        for p in lyric__cont_box.find_all("p")[1:]:
            if "：" in p.get_text(strip=True):
                continue
            lyrics.append(p.get_text(strip=True))
            
    if lyrics == []:
        song_info["lyrics"] = None
    else:
        song_info["lyrics"] = lyrics

    # number of comments
    song_info["num_comments"] = None
    mod_btn__icon_comment = soup.find("i", class_="mod_btn__icon_comment")
    btn__txt = mod_btn__icon_comment.find_next_sibling("span", class_="btn__txt")
    text =   (btn__txt.get_text(strip=True))
    num_comments = re.search(r'\d+', text)
    if num_comments:
        song_info["num_comments"] = int(num_comments.group())

    return song_info, picture_url