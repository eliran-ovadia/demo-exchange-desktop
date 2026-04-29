"""
Run once to generate assets/icon.ico from assets/icon.svg.
Usage:  ../.venv/Scripts/python create_icon.py
"""
import os, sys, struct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, QBuffer, QByteArray

SIZES = [16, 24, 32, 48, 64, 128, 256]


def svg_to_png_bytes(svg_path: str, size: int) -> bytes:
    renderer = QSvgRenderer(svg_path)
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    buf = QByteArray()
    buffer = QBuffer(buf)
    buffer.open(QBuffer.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buf)


def write_ico(png_list: list[bytes], output_path: str) -> None:
    count = len(png_list)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + count * 16
    directory = b""
    for size, png in zip(SIZES, png_list):
        w = 0 if size >= 256 else size
        h = 0 if size >= 256 else size
        directory += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
    with open(output_path, "wb") as f:
        f.write(header + directory + b"".join(png_list))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    here = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(here, "icon.svg")
    ico_path = os.path.join(here, "icon.ico")
    print(f"Rendering {svg_path} at sizes: {SIZES}")
    pngs = [svg_to_png_bytes(svg_path, s) for s in SIZES]
    write_ico(pngs, ico_path)
    print(f"Created: {ico_path}")
