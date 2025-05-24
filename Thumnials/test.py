from cairosvg import svg2png

#with open('./Reddit Stories Card (Community)(3)/Reddit Stories Card (Community).svg', 'r') as file:
with open('./Title.svg', 'r') as file:
    svg_code = file.read()

print(svg_code)

svg2png(bytestring=svg_code,write_to='output.png')