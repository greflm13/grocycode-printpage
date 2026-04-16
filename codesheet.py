#!/bin/env python
import os
import io
import json
import argparse


from PIL import Image
from pylibdmtx.pylibdmtx import encode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.ttfonts import TTFont

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
Image.MAX_IMAGE_PIXELS = 9331200000

COLS = 5
CELL_WIDTH = 400
CELL_HEIGHT = 315
START_X_TEXT = 250
START_X_IMG = 150
START_Y = 100
BLOCK_HEIGHT = CELL_HEIGHT
PAGE_HEIGHT = 2970

pdfmetrics.registerFont(TTFont("header", "FiraSans-Black.ttf"))


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="create printable pdf of grocycodes in grid")
    parser.add_argument("layout", help="layout json", type=str)
    parser.add_argument("-o", "--output", help="output directory (default 'output')", type=str, default="output")
    return parser.parse_args()


def main() -> None:
    args = argparser()
    os.makedirs(args.output, exist_ok=True)
    pagesize = pagesizes.portrait(pagesizes.A4)
    pdf = Canvas(os.path.join(args.output, "codesheet.pdf"), pagesize=pagesize)

    scale_x = pagesize[0] / 2100
    scale_y = pagesize[1] / 2970
    pdf.scale(scale_x, scale_y)

    black = colors.HexColor("#000000")

    pdf.setFont("header", 24)
    pdf.setFillColor(black)

    with open(args.layout, "r") as f:
        layout = json.loads(f.read())

    def start_new_page(pdf):
        pdf.showPage()
        pdf.scale(scale_x, scale_y)
        pdf.setFont("header", 24)
        pdf.setFillColor(black)

    row = 0

    for idx, product in enumerate(layout):
        col = idx % COLS

        if col == 0 and idx != 0:
            row += 1

        y = START_Y + row * BLOCK_HEIGHT

        if y + BLOCK_HEIGHT > PAGE_HEIGHT:
            start_new_page(pdf)
            row = 0
            y = START_Y

        x_text = START_X_TEXT + col * CELL_WIDTH
        x_img = START_X_IMG + col * CELL_WIDTH

        pdf.drawCentredString(x=x_text, y=y, text=product["name"])

        encoded = encode(f"grcy:p:{product['id']}".encode("utf-8"))
        img = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        image = ImageReader(buffer)
        pdf.drawImage(image, x=x_img, y=y + 20, width=200, height=200)

    pdf.save()


if __name__ == "__main__":
    main()
