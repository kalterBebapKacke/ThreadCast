from bs4 import BeautifulSoup


def clean_html(html_content):
    # BeautifulSoup initialisieren
    soup = BeautifulSoup(html_content, 'html.parser')

    # Entfernt alle <style>-Tags
    for style_tag in soup.find_all('style'):
        style_tag.decompose()

    # Entfernt alle <script>-Tags
    for script_tag in soup.find_all('script'):
        script_tag.decompose()

    # Gibt das bereinigte HTML zurück
    return str(soup)


# Beispiel zur Verwendung:
if __name__ == "__main__":
    with open('page.html', 'r') as file:
        html = file.read()
    cleaned_html = clean_html(html)
    print("\nBereinigtes HTML:")
    new_html = cleaned_html.replace('\n', '').strip()
    with open('page.html', 'w') as file:
        file.write(new_html)
