import os
from typing import List, Any
from datetime import datetime


class TerminalInterface:
    def __init__(self, title: str = "Daten Übersicht"):
        self.title = title
        self.page = 0
        self.items_per_page = 10

    def clear_screen(self):
        """Bildschirm leeren - funktioniert sowohl unter Windows als auch Unix"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Kopfzeile mit Titel ausgeben"""
        print("=" * 50)
        print(f"{self.title:^50}")
        print("=" * 50)
        print()

    def print_menu(self):
        """Menüoptionen anzeigen"""
        print("\nBefehle:")
        print("n - Nächste Seite")
        print("p - Vorherige Seite")
        print("q - Beenden")
        print("s - Suchen")

    def display_data(self, data: List[Any]):
        """Hauptmethode zum Anzeigen der Daten"""
        while True:
            self.clear_screen()
            self.print_header()

            # Berechne Start- und Endindex für aktuelle Seite
            start_idx = self.page * self.items_per_page
            end_idx = start_idx + self.items_per_page
            current_items = data[start_idx:end_idx]

            # Zeige Seitennummer und Gesamtanzahl
            print(f"Seite {self.page + 1} von {(len(data) - 1) // self.items_per_page + 1}")
            print()

            # Zeige Daten der aktuellen Seite
            for idx, item in enumerate(current_items, start=start_idx + 1):
                print(f"{idx:3d}. {str(item)}")

            self.print_menu()

            # Benutzereingabe verarbeiten
            choice = input("\nWählen Sie eine Option: ").lower()

            if choice == 'q':
                break
            elif choice == 'n' and end_idx < len(data):
                self.page += 1
            elif choice == 'p' and self.page > 0:
                self.page -= 1
            elif choice == 's':
                search_term = input("Suchbegriff eingeben: ").lower()
                filtered_data = [
                    item for item in data
                    if search_term in str(item).lower()
                ]
                if filtered_data:
                    print("\nSuchergebnisse:")
                    for item in filtered_data:
                        print(f"- {item}")
                else:
                    print("\nKeine Ergebnisse gefunden.")
                input("\nDrücken Sie Enter zum Fortfahren...")


# Beispielverwendung
if __name__ == "__main__":
    # Beispieldaten
    sample_data = [
        {"id": i, "name": f"Eintrag {i}", "datum": datetime.now()}
        for i in range(1, 26)
    ]

    # Interface erstellen und Daten anzeigen
    interface = TerminalInterface("Beispiel Datenliste")
    interface.display_data(sample_data)
