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

urls = [
    url,
    url2,
    url3,
    url4,
    url5,
    url6,
    url7
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

def scrape_v3(process=4, data:int=20):
    results = list()

    p = Pool(process)
    args = [*urls]
    tmp_result = p.map(scrape, args)

    # filter text
    tmp_result = [clean.clean_html(x) for x in tmp_result]
    for clean_txt in tmp_result:
        soup = BeautifulSoup(clean_txt, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            results.append(ex.extract_story(str(article)))
        del soup
        del articles

    filtered_results = [d for d in results if d['content'] != []]
    results = get_top_n_dicts(filtered_results, data)
    return results


def get_top_n_dicts(data, n):
    """
    Gibt die besten n Dictionaries zurück, basierend auf score und comment_count.

    :param data: Liste von Dictionaries mit 'score' und 'comment_count'.
    :param n: Anzahl der gewünschten Top-Elemente.
    :return: Liste der Top-n Dictionaries.
    """
    # Sortieren nach Score und Comment Count (beide absteigend)
    sorted_data = sorted(data, key=lambda d: (d['score'], d['comment_count']), reverse=True)

    return sorted_data[:n]


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
    scrape_v3()