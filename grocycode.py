#!/bin/env python
import os
import re
import json
import argparse

import requests

from pylibdmtx.pylibdmtx import encode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.ttfonts import TTFont

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
BASE_URL_RE = re.compile(r"^https?:\/\/((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?$")

pdfmetrics.registerFont(TTFont("header", "FiraSans-Black.ttf"))


def datamatrix_to_bool_matrix(encoded) -> list:
    w, h = encoded.width, encoded.height
    pixels = encoded.pixels

    matrix = [[False] * w for _ in range(h)]
    idx = 0

    for y in range(h):
        for x in range(w):
            r = pixels[idx]
            matrix[y][x] = r < 128
            idx += 3

    return matrix


def draw_datamatrix_vector(pdf, matrix, x, y, size) -> None:
    rows = len(matrix)
    cols = len(matrix[0])

    module = size / max(rows, cols)

    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)

    for row in range(rows):
        for col in range(cols):
            if matrix[row][col]:
                pdf.rect(x + col * module, y + (rows - row - 1) * module, module, module, stroke=0, fill=1)


def base_url_or_int_type(value: str) -> tuple[str, str]:
    if BASE_URL_RE.match(value):
        return ("url", value)

    try:
        int(value)
        return ("id", value)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be either a base URL (http[s]://host[:port]) or an integer")


def check_or_load_login() -> str:
    file = os.path.join(SCRIPTDIR, ".api_key")
    if not os.path.exists(file):
        api_key = input("Your api key: ")
        login_dict = {"api_key": api_key}

        persist = input("Do you want to save your api key to a hidden file?: [y/n] ")
        if persist.lower() in {"yes", "y", "ye", "j", "ja"}:
            with open(file, "w") as login_file:
                json.dump(login_dict, login_file)
            print("Your api key has been saved to <" + str(file) + ">, to renew it please delete the file\n")

    else:
        with open(file, "r") as login_file:
            login_dict = json.load(login_file)
            api_key = login_dict["api_key"]
    return api_key


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="create printable pdf of grocycode")
    parser.add_argument("product_id", help="product id for the code", type=base_url_or_int_type)
    parser.add_argument("product_name", help="product name for the code", type=str)
    parser.add_argument("-o", "--output", help="output directory (default 'output')", type=str, default="output")
    return parser.parse_args()


def main() -> None:
    args = argparser()
    os.makedirs(args.output, exist_ok=True)
    pagesize = pagesizes.portrait(pagesizes.A4)
    pdf = Canvas(os.path.join(args.output, args.product_name + ".pdf"), pagesize=pagesize)

    scale_x = pagesize[0] / 2100
    scale_y = pagesize[1] / 2970
    pdf.scale(scale_x, scale_y)

    pdf.setFont("header", 48)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(x=2100 / 2, y=2880, text=args.product_name)
    pdf.setTitle(args.product_name)

    typ, value = args.product_id
    if typ == "id":
        product_id = value
    elif typ == "url":
        api_key = check_or_load_login()
        res = requests.get(
            url=f"{value}/api/objects/products?query%5B%5D=name%3D{args.product_name}",
            headers={"accept": "application/json", "GROCY-API-KEY": api_key},
        )
        try:
            product_id = res.json()[0]["id"]
        except IndexError:
            raise RuntimeError("Product not found: %s" % args.product_name)

    encoded = encode(f"grcy:p:{product_id}".encode("utf-8"))
    matrix = datamatrix_to_bool_matrix(encoded)
    pdf.beginForm("dm")
    draw_datamatrix_vector(pdf, matrix, 0, 0, size=100)
    pdf.endForm()

    for i in range(10):
        for j in range(27):
            pdf.saveState()
            pdf.translate(90 + i * 203.25, 125 + j * 100)
            pdf.doForm("dm")
            pdf.restoreState()

    pdf.save()


if __name__ == "__main__":
    main()
