#!/bin/env python
import os
import re
import json
import argparse
import urllib.parse

import requests

from pylibdmtx.pylibdmtx import encode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.ttfonts import TTFont

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")

COLS = 5
CELL_WIDTH = 400
CELL_HEIGHT = 315
START_X_TEXT = 250
START_X_IMG = 150
START_Y = 100
BLOCK_HEIGHT = CELL_HEIGHT
PAGE_HEIGHT = 2970

BASE_URL_RE = re.compile(r"^https?:\/\/((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?$")
JSON_FILE_RE = re.compile(r"^(?:\.{0,2}\/|\/)?(?:[^\/\0]+\/)*[^\/\0]+\.json$", re.VERBOSE)

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


def query(string: str) -> str:
    operators = ["!=", "!~", "<=", ">=", "=", "<", ">", "~", "§"]

    op_pattern = "|".join(map(re.escape, operators))

    pattern = re.compile(
        rf"""
        ^(?P<field>[A-Za-z_][A-Za-z0-9_]*)
        (?P<operator>{op_pattern})
        (?P<value>.+)$
        """,
        re.VERBOSE,
    )

    match = pattern.match(string)
    if not match:
        raise argparse.ArgumentTypeError("Expected <field><condition><value>")

    value = match.group("value")
    if not value:
        raise argparse.ArgumentTypeError("Value must not be empty")

    return f"{match.group('field')}{match.group('operator')}{value}"


def base_url_or_json_type(value: str) -> tuple[str, str]:
    if BASE_URL_RE.match(value):
        return ("url", value)

    if JSON_FILE_RE.match(value):
        return ("file", value)

    raise argparse.ArgumentTypeError("Must be either a base URL (http[s]://host[:port]) or a local .json file path")


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
    parser = argparse.ArgumentParser(description="create printable pdf of grocycodes in grid")
    parser.add_argument("layout", help="layout json OR server url", type=base_url_or_json_type)
    parser.add_argument(
        "--query",
        help="An array of filter conditions, each of them is a string in the form of <field><condition><value>",
        nargs="+",
        action="append",
        type=query,
    )
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

    pdf.setFont("header", 24)
    pdf.setFillColor(colors.black)

    typ, location = args.layout

    if typ == "file":
        with open(location, "r") as f:
            layout = json.loads(f.read())
    elif typ == "url":
        api_key = check_or_load_login()
        if args.query is not None:
            queries = [urllib.parse.quote(item) for group in args.query for item in group]
            url = f"{location}/api/objects/products?query%5B%5D={'&query%5B%5D='.join(queries)}"
        else:
            url = f"{location}/api/objects/products"
        res = requests.get(
            url=url,
            headers={"accept": "application/json", "GROCY-API-KEY": api_key},
        )
        layout = res.json()

    def start_new_page(pdf):
        pdf.showPage()
        pdf.scale(scale_x, scale_y)
        pdf.setFont("header", 24)
        pdf.setFillColor(colors.black)

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
        matrix = datamatrix_to_bool_matrix(encoded)
        draw_datamatrix_vector(pdf, matrix, x=x_img, y=y + 20, size=200)

    pdf.save()


if __name__ == "__main__":
    main()
