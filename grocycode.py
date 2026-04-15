#!/bin/env python
import os
import io
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

pdfmetrics.registerFont(TTFont("header", "FiraSans-Black.ttf"))
pdfmetrics.registerFont(TTFont("hour", "FiraSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("add", "FiraSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("foot", "FiraSans-Thin.ttf"))


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="create printable pdf of grocycode")
    parser.add_argument("product_id", help="product id for the code", type=str)
    parser.add_argument("product_name", help="product name for the code", type=str)
    parser.add_argument("-o", "--output", help="output directory (default 'output')", type=str, default="output")
    return parser.parse_args()


def main() -> None:
    args = argparser()
    os.makedirs(args.output, exist_ok=True)
    pagesize = pagesizes.portrait(pagesizes.A4)
    pdf = Canvas(os.path.join(args.output, args.product_name + ".pdf"), pagesize=pagesize)

    scale_x = pagesize[0] / 1188
    scale_y = pagesize[1] / 840
    pdf.scale(scale_x, scale_y)

    black = colors.HexColor("#000000")

    pdf.setFont("header", 48)
    pdf.setFillColor(black)
    pdf.drawCentredString(x=1188 / 2, y=790, text=args.product_name)

    encoded = encode(f"grcy:p:{args.product_id}".encode("utf-8"))
    img = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    image = ImageReader(buffer)

    for i in range(14):
        for j in range(19):
            pdf.drawImage(image, x=45 + i * 80, y=20 + j * 40, width=60, height=30)

    pdf.save()


if __name__ == "__main__":
    main()
