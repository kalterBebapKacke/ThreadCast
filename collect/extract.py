from bs4 import BeautifulSoup
import json
import re
from datetime import datetime


def extract_story(html_content):
    """
    Extracts story content from Reddit-style HTML articles.

    Args:
        html_content (str): HTML content containing the article

    Returns:
        dict: Dictionary containing the story metadata and content
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main article element
    article = soup.find('article')
    if not article:
        return None

    # Extract post attributes
    post = soup.find('shreddit-post')
    post_attrs = post.attrs if post else {}

    # Extract title (trying multiple possible locations)
    title = None
    title_elem = soup.find('a', id=lambda x: x and x.startswith('post-title-'))
    if title_elem:
        title = title_elem.text.strip()

    # Extract author (handling the nested structure)
    author = None
    author_elem = soup.find('a', {'class': 'flex items-center text-neutral-content'})
    if author_elem:
        author = author_elem.text.strip().replace('u/', '')

    # Extract timestamp
    timestamp = None
    time_elem = soup.find('time')
    if time_elem and 'datetime' in time_elem.attrs:
        timestamp = time_elem['datetime']

    # Extract story content
    content = []
    story_div = soup.find('div', {'class': 'md feed-card-text-preview text-ellipsis line-clamp-3 xs:line-clamp-6 text-14'})
    #print(story_div)
    if story_div:
        paragraphs = story_div.find_all('p')
        content = [p.text.strip() for p in paragraphs if p.text.strip()]

    # Extract flair if present
    flair = None
    flair_elem = soup.find('div', {'class': 'flair-content'})
    if flair_elem:
        flair = flair_elem.text.strip()

    # Create result dictionary
    result = {
        'title': title,
        'author': author,
        'timestamp': timestamp,
        'flair': flair,
        'content': content,
        'subreddit': post_attrs.get('subreddit-prefixed-name', ''),
        'score': post_attrs.get('score', ''),
        'comment_count': post_attrs.get('comment-count', '')
    }

    return result


def save_to_json(data, filename='story_output.json'):
    """
    Saves the extracted data to a JSON file with proper formatting.

    Args:
        data (dict): The extracted story data
        filename (str): Name of the output JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main(data:str):
    # Read the HTML file
    try:
        with open('test.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Extract the story data
        story_data = extract_story(html_content)

        if story_data:
            # Save to JSON file
            save_to_json(story_data)
            print(f"Successfully extracted story and saved to story_output.json")

            # Print a preview of the extracted data
            print("\nExtracted Data Preview:")
            print(f"Title: {story_data['title']}")
            print(f"Author: {story_data['author']}")
            print(f"Subreddit: {story_data['subreddit']}")
            print(f"Content paragraphs: {len(story_data['content'])}")
        else:
            print("Failed to extract story data from the HTML content")

    except FileNotFoundError:
        print("Error: article.html file not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")





if __name__ == "__main__":
    main()
