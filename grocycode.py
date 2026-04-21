#!/bin/env python
import os
import argparse

import requests

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.ttfonts import TTFont

from modules.utils import (
    BASE_URL_RE,
    get_bool_matrix,
    draw_datamatrix_vector,
    check_or_load_login,
    PageLayout,
)

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")

pdfmetrics.registerFont(TTFont("header", "FiraSans-Black.ttf"))


def create_codepage(matrix: list[bool], filename: str, product_name) -> None:
    pagesize = pagesizes.portrait(pagesizes.A4)
    pdf = Canvas(filename, pagesize=pagesize)

    scale_x = pagesize[0] / PageLayout.PAGE_WIDTH.value
    scale_y = pagesize[1] / PageLayout.PAGE_HEIGHT.value
    pdf.scale(scale_x, scale_y)

    pdf.setFont("header", 48)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(x=2100 / 2, y=2880, text=product_name)
    pdf.setTitle(product_name)
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


def base_url_or_int_type(value: str) -> tuple[str, str]:
    if BASE_URL_RE.match(value):
        return ("url", value)

    try:
        int(value)
        return ("id", value)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be either a base URL (http[s]://host[:port]) or an integer")


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="create printable pdf of grocycode")
    parser.add_argument("product_id", help="product id OR server url for the code", type=base_url_or_int_type)
    parser.add_argument("product_name", help="product name for the code", type=str)
    parser.add_argument("-o", "--output", help="output directory (default 'output')", type=str, default="output")
    return parser.parse_args()


def main() -> None:
    args = argparser()
    os.makedirs(args.output, exist_ok=True)

    typ, value = args.product_id
    if typ == "id":
        product_id = value
    elif typ == "url":
        api_key, _ = check_or_load_login()
        res = requests.get(
            url=f"{value}/api/objects/products?query%5B%5D=name%3D{args.product_name}",
            headers={"accept": "application/json", "GROCY-API-KEY": api_key},
        )
        try:
            product_id = res.json()[0]["id"]
        except IndexError:
            raise RuntimeError("Product not found: %s" % args.product_name)

    matrix = get_bool_matrix(product_id)
    create_codepage(matrix, os.path.join(args.output, args.product_name + ".pdf"), args.produc_name)


if __name__ == "__main__":
    main()
