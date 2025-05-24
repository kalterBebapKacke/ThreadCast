import xml.etree.ElementTree as ET
from typing import Tuple, List, Optional
import textwrap
import base64
from pathlib import Path, PurePath
import cairosvg
import sys
import os


class SVGTextBoxGenerator:
    def __init__(self):
        self.svg_ns = "http://www.w3.org/2000/svg"
        ET.register_namespace('', self.svg_ns)

    def calculate_text_size(self, text_lines: List[str], font_size: int) -> Tuple[float, float]:
        avg_char_width = font_size * 0.6
        max_line_width = max(len(line) * avg_char_width for line in text_lines)
        total_height = len(text_lines) * font_size * 1.1
        return max_line_width, total_height

    def wrap_text(self, text: str, max_width: int, font_size: int) -> List[str]:
        avg_char_width = font_size * 0.6
        chars_per_line = int(max_width / avg_char_width)
        wrapped_lines = textwrap.fill(text, width=chars_per_line, break_long_words=False).split('\n')
        return wrapped_lines

    def embed_svg(self, parent: ET.Element, svg_file: str, x: int, y: int, width: int, height: int) -> None:
        try:
            tree = ET.parse(svg_file)
            svg_root = tree.getroot()

            bg_group = ET.SubElement(parent, f'{{{self.svg_ns}}}g')
            bg_group.set('transform', f'translate({x}, {y})')

            bg_rect = ET.SubElement(bg_group, f'{{{self.svg_ns}}}rect')
            bg_rect.set('x', '0')
            bg_rect.set('y', '0')
            bg_rect.set('width', str(width))
            bg_rect.set('height', str(height))
            bg_rect.set('fill', 'white')

            content_group = ET.SubElement(parent, f'{{{self.svg_ns}}}g')

            viewBox = svg_root.get('viewBox', '0 0 100 100').split()
            orig_width = float(svg_root.get('width', viewBox[2]))
            orig_height = float(svg_root.get('height', viewBox[3]))

            scale_x = width / orig_width
            scale_y = height / orig_height
            scale = min(scale_x, scale_y)
            translate_x = x + (width - (orig_width * scale)) / 2
            translate_y = y + (height - (orig_height * scale)) / 2
            content_group.set('transform', f'translate({translate_x}, {translate_y}) scale({scale})')

            for child in svg_root:
                content_group.append(child)

        except Exception as e:
            rect = ET.SubElement(parent, f'{{{self.svg_ns}}}rect')
            rect.set('x', str(x))
            rect.set('y', str(y))
            rect.set('width', str(width))
            rect.set('height', str(height))
            rect.set('fill', 'white')
            rect.set('stroke', 'black')

    def embed_image(self, parent: ET.Element, image_file: str, x: int, y: int, width: int, height: int) -> None:
        try:
            with open(image_file, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()

            image = ET.SubElement(parent, f'{{{self.svg_ns}}}image')
            image.set('x', str(x))
            image.set('y', str(y))
            image.set('width', str(width))
            image.set('height', str(height))
            image.set('preserveAspectRatio', 'xMidYMid meet')

            mime_type = 'image/png' if image_file.lower().endswith('.png') else 'image/jpeg'
            image.set('href', f'data:{mime_type};base64,{img_data}')

        except Exception as e:
            rect = ET.SubElement(parent, f'{{{self.svg_ns}}}rect')
            rect.set('x', str(x))
            rect.set('y', str(y))
            rect.set('width', str(width))
            rect.set('height', str(height))
            rect.set('fill', 'white')
            rect.set('stroke', 'black')

    def create_svg_with_text(self, text: str, output_file: str,
                             top_svg_file: str,
                             bottom_left_image: str,
                             bottom_right_image: str,
                             max_width: int = 400,
                             min_width: int = 200,
                             min_height: int = 100,
                             font_size: int = 24,
                             padding: int = 20,
                             corner_radius: int = 20,
                             top_image_height: int = 200,
                             bottom_image_height: int = 200,
                             image_padding: int = 20):

        usable_width = max_width - (padding * 2)
        text_lines = self.wrap_text(text, usable_width, font_size)
        text_width, text_height = self.calculate_text_size(text_lines, font_size)

        width = max(min_width, min(max_width, text_width + (padding * 2)))
        height = max(min_height, text_height + (image_padding * 3))
        total_height = height + top_image_height + bottom_image_height + (padding * 2) - 20

        root = ET.Element(f'{{{self.svg_ns}}}svg')
        root.set('width', str(width))
        root.set('height', str(total_height))
        root.set('viewBox', f'0 0 {width} {total_height}')

        style = ET.SubElement(root, f'{{{self.svg_ns}}}style')
        style.text = "@font-face { font-family: 'Arial'; src: local('Arial Bold'); font-weight: bold; }"

        rect = ET.SubElement(root, f'{{{self.svg_ns}}}rect')
        rect.set('x', '0')
        rect.set('y', '0')
        rect.set('width', str(width))
        rect.set('height', str(total_height))
        rect.set('rx', str(corner_radius))
        rect.set('ry', str(corner_radius))
        rect.set('fill', 'white')

        self.embed_svg(root, top_svg_file, padding-10, padding,
                       width - (padding * 2), top_image_height)

        start_y = top_image_height + padding + image_padding + 30

        line_height = font_size * 1.2
        for i, line in enumerate(text_lines):
            text_elem = ET.SubElement(root, f'{{{self.svg_ns}}}text')
            text_elem.set('x', str(padding))
            text_elem.set('y', str(start_y + i * line_height))
            text_elem.set('text-anchor', 'start')
            text_elem.set('font-family', 'Arial')
            text_elem.set('font-weight', 'bold')
            text_elem.set('font-size', str(font_size))
            text_elem.text = line

        bottom_y = total_height - bottom_image_height - padding
        bottom_image_width = (width - (padding * 3)) / 2

        self.embed_image(root, bottom_left_image, padding, bottom_y,
                         134, bottom_image_height)

        self.embed_image(root, bottom_right_image, width - padding - 115, bottom_y,
                         115, bottom_image_height)

        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

def create_reddit(text:str, location:str) -> None:
    generator = SVGTextBoxGenerator()
    generator.create_svg_with_text(
        text=text,
        output_file=location,
        top_svg_file= str(get_path("./fertig.svg")),
        bottom_right_image= str(get_path("./Share.png")),
        bottom_left_image= str(get_path("./Likes.png")),
        max_width=880,
        min_width=880,
        min_height=60,
        font_size=54,
        padding=35,
        corner_radius=35,
        top_image_height=135,
        bottom_image_height=42,
        image_padding=20
    )
    return None

def get_path(location:str):
    p = PurePath('Thumnials', 'media', location)
    return p


def convert_svg_to_png(svg_path, png_path=None):
    try:
        # Wenn kein PNG-Pfad angegeben wurde, erstelle einen
        if png_path is None:
            png_path = os.path.splitext(svg_path)[0] + '.png'

        # Konvertiere SVG zu PNG
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        #print(f"Erfolgreich konvertiert: {svg_path} -> {png_path}")

    except FileNotFoundError:
        print(f"Fehler: Die Datei {svg_path} wurde nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {str(e)}")

if __name__ == "__main__":
    generator = SVGTextBoxGenerator()
    generator.create_svg_with_text(
        text="Dies ist ein Beispieltext mit eingebetteten SVGs und Bildern Text Text Text Text Text",
        output_file="textbox_with_embedded_media.svg",
        top_svg_file="./fertig.svg",
        bottom_right_image="./Share.png",  # Change to your image file
        bottom_left_image="./Likes.png",  # Change to your image file
        max_width=880,
        min_width=880,
        min_height=60,
        font_size=54,
        padding=35,
        corner_radius=35,
        top_image_height=135,
        bottom_image_height=42,
        image_padding=20
    )


