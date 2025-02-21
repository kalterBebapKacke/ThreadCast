import os
import sys


def clear_screen():
    """Bildschirm je nach Betriebssystem leeren"""
    os.system('cls' if os.name == 'nt' else 'clear')


def beispiel_funktion1():
    print("Funktion 1 wurde ausgeführt")
    input("\nDrücke Enter um fortzufahren...")


def beispiel_funktion2():
    print("Funktion 2 wurde ausgeführt")
    input("\nDrücke Enter um fortzufahren...")


def beispiel_funktion3():
    print("Funktion 3 wurde ausgeführt")
    input("\nDrücke Enter um fortzufahren...")


# Dictionary mit den verfügbaren Funktionen
funktionen = {
    "1": {
        "name": "Erste Funktion",
        "func": beispiel_funktion1
    },
    "2": {
        "name": "Zweite Funktion",
        "func": beispiel_funktion2
    },
    "3": {
        "name": "Dritte Funktion",
        "func": beispiel_funktion3
    }
}


def zeige_menu(info:dict):
    funktionen = info
    """Hauptmenü anzeigen"""
    while True:
        #clear_screen()
        print("=== Hauptmenü ===")
        print("\nVerfügbare Optionen:")

        # Alle verfügbaren Optionen anzeigen
        for key, value in funktionen.items():
            print(f"{key}. {value['name']}")

        print("\n0. Programm beenden")

        # Benutzereingabe
        auswahl = input("\nBitte wähle eine Option: ")

        if auswahl == "0":
            print("\nProgramm wird beendet...")
            sys.exit()

        # Ausgewählte Funktion ausführen
        if auswahl in funktionen:
            clear_screen()
            print(f"=== {funktionen[auswahl]['name']} ===\n")
            funktionen[auswahl]['func']()
        else:
            print("\nUngültige Eingabe!")
            input("Drücke Enter um fortzufahren...")


if __name__ == "__main__":
    #zeige_menu()
    pass
