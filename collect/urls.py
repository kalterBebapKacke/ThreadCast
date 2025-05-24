import pyextract_here.webscraping as extract

def save(soup):
    out = str(soup)
    with open('test.html', 'w') as file:
        file.write(out)

url = 'https://www.reddit.com/'
url2 = 'https://www.reddit.com/r/stories/'
url3 = 'https://www.reddit.com/r/relationship_advice/'
url4 = 'https://www.reddit.com/r/Advice/'
url5 = 'https://www.reddit.com/r/AskReddit/'
url6 = 'https://www.reddit.com/r/AmItheAsshole/'
url7 = 'https://www.reddit.com/r/AmIOverreacting/'

def scrape(url_:str=url6):
    soup = extract.selenium_requests(url_, '', soup=True)
    t = soup.find_all('article')
    return str(t)

