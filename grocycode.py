#!/bin/env python
import os
import io
import re
import json
import argparse

import requests

from PIL import Image
from pylibdmtx.pylibdmtx import encode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors, pagesizes
from reportlab.pdfbase.ttfonts import TTFont

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
Image.MAX_IMAGE_PIXELS = 9331200000

BASE_URL_RE = re.compile(r"^https?:\/\/((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?$")

pdfmetrics.registerFont(TTFont("header", "FiraSans-Black.ttf"))


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
            print("Your password has been saved to <" + str(file) + ">, to renew it please delete the file\n")

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

    black = colors.HexColor("#000000")

    pdf.setFont("header", 48)
    pdf.setFillColor(black)
    pdf.drawCentredString(x=2100 / 2, y=2870, text=args.product_name)

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
    img = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    resized = img.resize((900, 900), resample=Image.Resampling.NEAREST)

    buffer = io.BytesIO()
    resized.save(buffer, format="PNG")
    buffer.seek(0)

    image = ImageReader(buffer)

    for i in range(10):
        for j in range(27):
            pdf.drawImage(image, x=85 + i * 203.25, y=135 + j * 100, width=100, height=100)

    pdf.save()


if __name__ == "__main__":
    main()
