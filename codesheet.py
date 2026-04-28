#!/bin/env python
import os
import json
import argparse
import urllib.parse

if __name__ == "__main__":
    import requests

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.ttfonts import TTFont

from modules.utils import (
    QUERY_RE,
    BASE_URL_RE,
    JSON_FILE_RE,
    get_bool_matrix,
    draw_datamatrix_vector,
    check_or_load_login,
    PageLayout,
    get_version,
)

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")

pdfmetrics.registerFont(TTFont("header", "FiraSans-Black.ttf"))


def create_codesheet(layout: list[dict], filename: str) -> None:
    pagesize = pagesizes.portrait(pagesizes.A4)
    pdf = Canvas(filename, pagesize=pagesize)

    scale_x = pagesize[0] / PageLayout.PAGE_WIDTH.value
    scale_y = pagesize[1] / PageLayout.PAGE_HEIGHT.value
    pdf.scale(scale_x, scale_y)

    pdf.setFont("header", 24)
    pdf.setFillColor(colors.black)

    def start_new_page(pdf):
        pdf.showPage()
        pdf.scale(scale_x, scale_y)
        pdf.setFont("header", 24)
        pdf.setFillColor(colors.black)

    row = 0

    for idx, product in enumerate(layout):
        col = idx % PageLayout.COLS.value

        if col == 0 and idx != 0:
            row += 1

        y = PageLayout.START_Y.value + row * PageLayout.BLOCK_HEIGHT.value

        if y + PageLayout.BLOCK_HEIGHT.value > PageLayout.PAGE_HEIGHT.value:
            start_new_page(pdf)
            row = 0
            y = PageLayout.START_Y.value

        x_text = PageLayout.START_X_TEXT.value + col * PageLayout.CELL_WIDTH.value
        x_img = PageLayout.START_X_IMG.value + col * PageLayout.CELL_WIDTH.value

        pdf.drawCentredString(x=x_text, y=y, text=product["name"])

        matrix = get_bool_matrix(product["id"])
        draw_datamatrix_vector(pdf, matrix, x=x_img, y=y + 20, size=200)

    pdf.save()


def query(string: str) -> str:
    match = QUERY_RE.match(string)
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
    parser.add_argument("-V", "--version", action="version", version="%(prog)s " + get_version())
    return parser.parse_args()


def main() -> None:
    args = argparser()
    os.makedirs(args.output, exist_ok=True)

    typ, location = args.layout

    if typ == "file":
        with open(location, "r") as f:
            layout = json.loads(f.read())
    elif typ == "url":
        api_key, _ = check_or_load_login()
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

    create_codesheet(layout, args.output)


if __name__ == "__main__":
    main()
