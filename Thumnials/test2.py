import xml.etree.ElementTree as ET

# SVG-Datei laden
tree = ET.parse('./Reddit Stories Card (Community)(3)/Reddit Stories Card (Community).svg')
# Root-Element bekommen
root = tree.getroot()
print(root)

text_elemente = root.findall('.//{http://www.w3.org/2000/svg}image')
print(text_elemente)

