from Cython.Build.Dependencies import join_path

from . import options

def display_text_with_confirmation(title, text:str):
    # Terminal Breite
    terminal_width = 80

    text = format_text(text, terminal_width)
    # Trennlinie erstellen
    separator = "=" * terminal_width

    # Ausgabe formatieren
    print("\n" + separator)
    print(f"{title.center(terminal_width)}")
    print(separator + "\n")
    print(text)
    print("\n" + separator)

    # Benutzerabfrage
    while True:
        choice = input("\nDo you want to use this? (y/n): ").lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("Invalid input")

def display_all(content):
    valid_ids = list()
    for x in content:
        options.clear_screen()
        output = display_text_with_confirmation(x[1], x[0])
        if output is True:
            valid_ids.append(x[2])
    options.clear_screen()
    return valid_ids


def format_text(text:str, max_length):
    # Teile den Text zunächst in vorhandene Zeilen
    paragraphs = [text.replace('\n', ' ')]
    formatted_paragraphs = []

    for paragraph in paragraphs:
        # Überspringe leere Zeilen
        if not paragraph.strip():
            formatted_paragraphs.append('')
            continue

        words = paragraph.split()
        current_line = []
        current_length = 0

        for word in words:
            # Prüfe, ob das Wort in die aktuelle Zeile passt
            word_length = len(word)

            # Wenn das Wort länger als max_length ist, wird es in eine eigene Zeile gesetzt
            if word_length > max_length:
                if current_line:
                    formatted_paragraphs.append(' '.join(current_line))
                    current_line = []
                    current_length = 0
                formatted_paragraphs.append(word)
                continue

            # Füge Leerzeichen hinzu, wenn die Zeile nicht leer ist
            space_needed = 1 if current_line else 0

            # Wenn das Wort nicht in die aktuelle Zeile passt
            if current_length + space_needed + word_length > max_length:
                formatted_paragraphs.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                if current_line:
                    current_length += space_needed
                current_line.append(word)
                current_length += word_length

        # Füge die letzte Zeile hinzu, wenn sie nicht leer ist
        if current_line:
            formatted_paragraphs.append(' '.join(current_line))

    return '\n'.join(formatted_paragraphs)

def display_shipping(id:int, path:str, title:str):
    # Terminal Breite
    terminal_width = 80

    # Trennlinie erstellen
    separator = "=" * terminal_width

    # Ausgabe formatieren
    print("\n" + separator)
    print(f"{str(id).center(terminal_width)}")
    print(separator + "\n")
    print(f'Path: {path}')
    print(f'Title: {title}')
    print("\n" + separator)

    # Benutzerabfrage
    while True:
        choice = input("\n1=entry before; 2=next entry; 3=marked shipped; 4=exit: ").lower()
        choice = str(choice)
        if choice in ['1']:
            return '1'
        elif choice in ['2']:
            return '2'
        elif choice in ['3']:
            return '3'
        elif choice in ['4']:
            return '4'
        else:
            print("Invalid input")

