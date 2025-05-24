import re


def expand_abbreviations(text, abbreviation_dict):
    """
    Ersetzt Abkürzungen in einem Text durch ihre vollständige Form.
    :param text: Der Eingabetext mit Abkürzungen
    :param abbreviation_dict: Ein Wörterbuch mit Abkürzungen als Schlüssel und ihrer langen Form als Wert
    :return: Der bearbeitete Text mit ersetzten Abkürzungen
    """

    def replace_match(match):
        abbr = match.group(0)
        return abbreviation_dict.get(abbr, abbr)

    text = remove_brackets(text)

    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in abbreviation_dict.keys()) + r')\b', re.IGNORECASE)
    text = pattern.sub(replace_match, text)

    # Altersangaben wie (28M) oder 18M durch "28 Male" oder "18 Male" ersetzen
    text = re.sub(r'\((\d+)\s*M\)', r'\1 Male', text, flags=re.IGNORECASE)
    text = re.sub(r'\((\d+)\s*F\)', r'\1 Female', text, flags=re.IGNORECASE)

    # Entfernen von Anführungszeichen, um SQL-Probleme zu vermeiden
    text = text.replace("'", "").replace('"', "").replace('“', '').replace('”', '')

    return text


# Wörterbuch mit Abkürzungen und deren Langformen
abbreviations = {
    "gf": "girlfriend",
    "idk": "I don't know",
    "STD": "sexually transmitted disease",
    "P.S": "postscript",
    "shes": "she is",
    "Ive": "I have",
    "Im": "I am",
    "alot": "a lot",
    "didnt": "did not",
    "wanna": "want to",
    "its": "it is",
    "wasnt": "was not",
    "thats": "that is",
    "youre": "you are",
    "I’d": "I would",
    "husb": "husband",
    "AIO" : "Am I Overreacting",
    "AITA" : "Am I the Asshole",
    "AITAH" : "Am I the Asshole",
}


def remove_brackets(text):
    """
    Entfernt alle Klammern und deren Inhalt aus einem String.
    Unterstützt runde, eckige und geschweifte Klammern.

    Args:
        text (str): Der Eingabetext, aus dem Klammern entfernt werden sollen

    Returns:
        str: Text ohne Klammern und deren Inhalt
    """
    result = ""
    skip_level = 0

    for char in text:
        if char in "({[":
            skip_level += 1
        elif char in ")}]":
            if skip_level > 0:
                skip_level -= 1
        elif skip_level == 0:
            result += char

    return result