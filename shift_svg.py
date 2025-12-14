import sys
import re
from lxml import etree
from svgpathtools import parse_path

def parse_translate(transform_str):
    m = re.search(r"translate\(([-+]?\d*\.?\d+),\s*([-+]?\d*\.?\d+)\)", transform_str)
    if m:
        dx = float(m.group(1))
        dy = float(m.group(2))
        return dx, dy
    return 0.0, 0.0

def shift_path(d_attr, dx, dy):
    path = parse_path(d_attr)
    # translate by (-dx, -dy) to cancel out the original transform
    path = path.translated(complex(-dx, -dy))
    return path.d()

def process_svg(input_file, output_file):
    tree = etree.parse(input_file)
    root = tree.getroot()

    dx, dy = 0.0, 0.0
    for g in root.findall(".//{http://www.w3.org/2000/svg}g"):
        transform = g.attrib.get("transform")
        if transform and "translate" in transform:
            dx, dy = parse_translate(transform)
            del g.attrib["transform"]

    for path in root.findall(".//{http://www.w3.org/2000/svg}path"):
        d = path.attrib.get("d")
        if d:
            path.attrib["d"] = shift_path(d, dx, dy)

    tree.write(output_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python shift_svg.py input.svg output.svg")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_svg(input_file, output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # rotationCenter コメントを削除
    content = re.sub(r'<!--rotationCenter[^>]*-->', '', content)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
