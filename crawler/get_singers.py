from bs4 import BeautifulSoup as BS

def get_singers(content):
    """
    Get the information of singers from QQ music.
    """
        
    soup = BS(content, "lxml")
    
    singers = {}
    
    # get item_box
    singer_list__item_box = soup.find_all(class_="singer_list__title")
    
    for h3 in singer_list__item_box:
        a_tag = h3.find("a")
        
        if a_tag:
            name = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            mid = href.split('/')[-1]
            if mid:   
                singers[mid] = name
            
    # get txt_item
    singer_list_txt__item = soup.find_all(class_="singer_list_txt__item")
    
    for li in singer_list_txt__item:
        a_tag = li.find("a")
        
        if a_tag:
            name = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            mid = href.split('/')[-1]
            if mid:
                singers[mid] = name
    
    return singers
    
def get_singer_info(content, mid, all_singers):
    """
    Get the information of a singer from content, including:
        - name
        - portrait
        - introduction
        - singer's mid
        - number of songs included
        - number of albums included
        - number of movies included
        - number of followers
        - some of the singer's popular songs, including song's mid
    """
        
    soup = BS(content, "lxml")
    
    singer_info = {}
    
    # basic information
    singer_info["name"] = soup.find("h1", class_="data__name_txt").get_text(strip=True)
    portrait_url = soup.find("img", class_="data__photo").get("src", "")
    if portrait_url:
        portrait_url = "https:" + portrait_url
    singer_info["intro"] = soup.find("div", class_="data__desc_txt").get_text(strip=True)
    singer_info["mid"] = mid
    
    # statistical information
    statistics = soup.find_all("li", class_="data_statistic__item")
    
    singer_info["num_songs"] = None
    singer_info["num_albums"] = None
    singer_info["num_movies"] = None
    
    for item in statistics:
        tit_tag = item.find(class_='data_statistic__tit')
        num_tag = item.find(class_='data_statistic__number')
        
        if tit_tag and num_tag:
            tit_text = tit_tag.get_text(strip=True)
            num_text = num_tag.get_text(strip=True)
            
            match tit_text:
                case "单曲":
                    singer_info["num_songs"] = int(num_text)
                case "专辑":
                    singer_info["num_albums"] = int(num_text)
                case "MV":
                    singer_info["num_movies"] = int(num_text)
                case _:
                    pass
                
    mod_btn = soup.find("a", class_="mod_btn")
    num_followers = mod_btn.find("span").get_text(strip=True)
    if num_followers[-1] == "万":
        singer_info["num_followers"] = int(float(num_followers[:-1]) * 10000)
    elif num_followers[-1] == "千":
        singer_info["num_followers"] = int(float(num_followers[:-1]) * 1000)
    else:
        singer_info["num_followers"] = int(num_followers)
        
    # popular songs
    popular_songs = []
    songs_list = soup.find_all("span", class_="songlist__songname_txt")
    for span in songs_list:
        a_tag = span.find("a")
        if a_tag:
            href = a_tag.get("href", "")
            song_mid = href.split('/')[-1]
            popular_songs.append(song_mid)
        
    if popular_songs == []:
        singer_info["popular_songs"] = None
    else:
        singer_info["popular_songs"] = popular_songs

    # similiar_singers
    similiar_singers = []
    if soup.find("div", class_="mod_singer_list"):
        mod_singer_list = soup.find("div", class_="mod_singer_list").find_all("h3", class_="singer_list__title")
        for h3 in mod_singer_list:
            a_tag = h3.find("a")
            if a_tag:
                href = a_tag.get("href", "")
                singer_mid = href.split('/')[-1]
                if singer_mid in all_singers:
                    similiar_singers.append(singer_mid)
            
    if similiar_singers == []:
        singer_info["similiar_singers"] = None
    else:
        singer_info["similiar_singers"] = similiar_singers  

    return singer_info, portrait_url
