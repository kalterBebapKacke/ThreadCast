import sys
import time
from typing import Dict
#from options import clear_screen

import sys
from typing import Dict


class ProgressBar:
    """Eine flexible Progress Bar mit Support für multiple Instanzen und Print Management."""

    _instances: Dict[str, 'ProgressBar'] = {}
    _total_bars = 0  # Zählt die Gesamtanzahl der aktiven Bars

    @classmethod
    def print_text(cls, text: str):
        """
        Druckt Text unter allen Progress Bars.

        Args:
            text: Der zu druckende Text
        """
        # Bewege Cursor unter alle Bars
        sys.stdout.write('\033[%d;0H' % (cls._total_bars + 1))
        # Drucke den Text
        print(text)
        # Aktualisiere alle sichtbaren Bars
        for bar in cls._instances.values():
            if bar.visible:
                bar.print_progress()

    def __init__(self, total: int, prefix: str = '', suffix: str = '', decimals: int = 1,
                 length: int = 50, fill: str = '█', print_end: str = '\r', id: str = 'default'):
        """
        Initialisiert eine neue Progress Bar.

        Args:
            total: Gesamtanzahl der Schritte
            prefix: Prefix String
            suffix: Suffix String
            decimals: Anzahl der Dezimalstellen für Prozent
            length: Länge der Progress Bar
            fill: Bar Fill Charakter
            print_end: String am Ende (usually '\r' für gleiche Zeile)
            id: Eindeutige ID für multiple Bars
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.id = id
        self.current = 0
        self.visible = True
        self.line_position = len(ProgressBar._instances)

        # Registriere diese Instanz
        ProgressBar._instances[id] = self
        ProgressBar._total_bars = max(ProgressBar._total_bars, self.line_position + 1)

    def print_progress(self):
        """Druckt den aktuellen Fortschritt."""
        if not self.visible:
            return

        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.current / float(self.total)))
        filled_length = int(self.length * self.current // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)

        # Bewege Cursor zur richtigen Position
        #sys.stdout.write('\033[%d;0H' % (self.line_position + 1))
        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end=self.print_end)

        # Bewege Cursor zurück unter alle Bars
        #sys.stdout.write('\033[%d;0H' % (ProgressBar._total_bars + 1))

    def update(self, current: int = None):
        """
        Aktualisiert den Fortschritt der Bar.

        Args:
            current: Aktuelle Position (wenn None, wird um 1 erhöht)
        """
        if current is not None:
            self.current = current
        else:
            self.current += 1

        self.print_progress()

    def hide(self):
        """Versteckt die Progress Bar."""
        self.visible = False
        # Lösche die Zeile
        sys.stdout.write('\033[%d;0H' % (self.line_position + 1))
        sys.stdout.write('\r' + ' ' * (len(self.prefix) + self.length + 20) + '\r')

    def show(self):
        """Zeigt die Progress Bar wieder an."""
        self.visible = True
        self.print_progress()

    @classmethod
    def clear_all(cls):
        """Löscht alle Progress Bars vom Bildschirm."""
        for bar in cls._instances.values():
            bar.hide()
        cls._instances.clear()
        cls._total_bars = 0


from time import sleep
from rich.progress import Progress, BarColumn, TextColumn

# Erstellt ein Progress-Objekt mit individueller Spaltenanordnung
progress = Progress(
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
)

# Starte das Rendering
progress.start()

# Erstelle mehrere Fortschrittsbalken
task1 = progress.add_task("Task 1", total=100)
task2 = progress.add_task("Task 2", total=100, visible=False)  # Erst unsichtbar
task3 = progress.add_task("Task 3", total=100)

for i in range(100):
    sleep(0.1)
    progress.update(task1, advance=1)

    # Zeigt Task 2 nach 30% Fortschritt von Task 1 an
    if i == 30:
        progress.update(task2, visible=True)
    print('lol')
    progress.update(task2, advance=1.5)
    progress.update(task3, advance=2)

progress.stop()