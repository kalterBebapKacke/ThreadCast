#from urls import *
import pagecrawler as extract
import time
from bs4 import BeautifulSoup
from multiprocessing import Pool

if __name__ == "__main__":
    import clean
    import extract as ex
else:
    from . import clean
    from . import extract as ex

url = 'https://www.reddit.com/'
url2 = 'https://www.reddit.com/r/stories/'
url3 = 'https://www.reddit.com/r/relationship_advice/'
url4 = 'https://www.reddit.com/r/Advice/'
url5 = 'https://www.reddit.com/r/AskReddit/'
url6 = 'https://www.reddit.com/r/AmItheAsshole/'
url7 = 'https://www.reddit.com/r/AmIOverreacting/'

url8 = 'https://www.reddit.com/r/nosleep/'

urls = [
    url2,
    url3,
    url6,
    url7,
    url8
]


def liste_aufteilen(ursprungsliste, anzahl_teillisten):
    # Überprüfen, ob die Liste gleichmäßig aufgeteilt werden kann
    if len(ursprungsliste) % anzahl_teillisten != 0:
        raise ValueError(f"Die Liste kann nicht in {anzahl_teillisten} gleichlange Teillisten aufgeteilt werden.")

    # Länge jeder Teilliste berechnen
    teillisten_laenge = len(ursprungsliste) // anzahl_teillisten

    # Liste in Teillisten aufteilen
    return [
        ursprungsliste[i * teillisten_laenge: (i + 1) * teillisten_laenge]
        for i in range(anzahl_teillisten)
    ]


def selenium_func(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(4)
    return extract.return_content(driver, False)

def build_url_list(url_list):
    r_list = list()
    for url in url_list:
        r_list.append(url)
        r_list.append(f'{url}top/')
    return r_list

def scrape(url_:str=url6, dev:bool=False):
    soup = extract.selenium_requests(url_, '', soup=True, dev=dev, func=selenium_func)
    return soup

def scrape_v2():
    results = list()
    for url in urls:
        source = scrape(url)
        clean_txt = clean.clean_html(source)
        soup = BeautifulSoup(clean_txt, 'html.parser')
        articles = soup.find_all('article')
        tmp_result = [ex.extract_story(str(x)) for x in articles]
        results.append(*tmp_result)

    return results

def scrape_v3(process=4, data:int=3):
    results = list()
    u_list = build_url_list(urls)
    #print(u_list)

    p = Pool(process)
    tmp_result = p.map(scrape, u_list)

    # filter text
    tmp_result = [clean.clean_html(x) for x in tmp_result]
    for clean_txt in tmp_result:
        using_tmp_result = list()
        soup = BeautifulSoup(clean_txt, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            using_tmp_result.append(ex.extract_story(str(article)))
        del soup
        del articles
        using_tmp_result = [d for d in using_tmp_result if d['content'] != []]
        #print(using_tmp_result)
        if len(using_tmp_result) != 0:
            using_tmp_result = analyze_posts(using_tmp_result)
            if len(using_tmp_result) < data:
                results.extend(using_tmp_result)
            else:
                results.extend(using_tmp_result[:data])

    return results


def get_top_n_dicts(data, n):
    # Sortieren nach Score und Comment Count (beide absteigend)
    sorted_data = sorted(data, key=lambda d: (d['score'], d['comment_count']), reverse=True)

    return sorted_data[:n]


def analyze_posts(posts, score_weight=2.0, comment_weight=2.0, content_penalty=1.0):
    """
    Analyzes posts to find ones with high engagement (score/comments) but relatively short content.

    Parameters:
    posts (list): List of dictionaries containing 'score', 'comment_count', and 'content'
    score_weight (float): Weight for score in ranking calculation
    comment_weight (float): Weight for comment count in ranking calculation
    content_penalty (float): Penalty factor for content length

    Returns:
    list: Sorted list of tuples (post, ranking_score)
    """

    # Calculate max values for normalization
    max_score = max(int(post['score']) for post in posts)
    max_comments = max(int(post['comment_count']) for post in posts)
    max_content_length = max(len(' '.join(post['content'])) for post in posts)

    # Calculate ranking score for each post
    ranked_posts = []
    for post in posts:
        # Normalize values between 0 and 1
        norm_score = int(post['score']) / max_score
        norm_comments = int(post['comment_count']) / max_comments
        norm_content_length = len(' '.join(post['content'])) / max_content_length

        # Calculate ranking score
        # Higher scores and comments increase ranking, longer content decreases it
        ranking_score = (
                (norm_score * score_weight) +
                (norm_comments * comment_weight) -
                (norm_content_length * content_penalty)
        )

        ranked_posts.append((post, ranking_score))

    # Sort by ranking score, highest first
    return [x[0] for x in sorted(ranked_posts, key=lambda x: x[1], reverse=True)]


if __name__ == "__main__1":
    url = url6 + 'top/'
    soup = scrape(url, True)
    clean_txt = clean.clean_html(soup)
    soup = BeautifulSoup(clean_txt, 'html.parser')
    articles = soup.find_all('article')
    result = [ex.extract_story(str(x)) for x in articles]
    print(result)
    print(len(result))

if __name__ == "__main__":
    r = scrape_v3()
    print(r)
    #print(build_url_list(urls))