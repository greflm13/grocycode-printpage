import os
import re
import json

from enum import Enum

from reportlab.lib import colors
from pylibdmtx.pylibdmtx import encode

_OPERATORS = ["!=", "!~", "<=", ">=", "=", "<", ">", "~", "§"]
_OP_PATTERN = "|".join(map(re.escape, _OPERATORS))
QUERY_RE = re.compile(rf"^(?P<field>[A-Za-z_][A-Za-z0-9_]*)(?P<operator>{_OP_PATTERN})(?P<value>.+)$", re.VERBOSE)
BASE_URL_RE = re.compile(r"^https?:\/\/((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?$")
JSON_FILE_RE = re.compile(r"^(?:\.{0,2}\/|\/)?(?:[^\/\0]+\/)*[^\/\0]+\.json$", re.VERBOSE)
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")


MAPPINGS = {
    "product_group_id": "product_groups",
    "location_id": "locations",
    "parent_product_id": "products",
    "shopping_location_id": "shopping_locations",
}


class PageLayout(Enum):
    COLS = 5
    CELL_WIDTH = 400
    CELL_HEIGHT = 315
    START_X_TEXT = 250
    START_X_IMG = 150
    START_Y = 100
    BLOCK_HEIGHT = CELL_HEIGHT
    PAGE_HEIGHT = 2970
    PAGE_WIDTH = 2100


def get_bool_matrix(data) -> list[bool]:
    encoded = encode(f"grcy:p:{data}".encode("utf-8"))
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


def index_by_key(lst: list[dict], key: str) -> dict:
    dic = {}
    for item in lst:
        dic[item.get(key)] = item
    return dic


def check_or_load_login() -> tuple[str, str]:
    file = os.path.join(SCRIPTDIR, ".api_key")
    if not os.path.exists(file):
        api_key = input("Your api key: ")
        url = input("Server URL: ")
        login_dict = {"api_key": api_key, "url": url}

        persist = input("Do you want to save your api key to a hidden file?: [y/n] ")
        if persist.lower() in {"yes", "y", "ye", "j", "ja"}:
            with open(file, "w") as login_file:
                json.dump(login_dict, login_file)
            print("Your api key has been saved to <" + str(file) + ">, to renew it please delete the file\n")

    else:
        with open(file, "r") as login_file:
            login_dict = json.load(login_file)
            api_key = login_dict["api_key"]
            url = login_dict["url"]
    return api_key, url


def check_or_load_gui_login() -> tuple[str | None, str | None]:
    file = os.path.join(SCRIPTDIR, ".api_key")

    if not os.path.exists(file):
        return None, None

    try:
        with open(file, "r") as login_file:
            login_dict = json.load(login_file)

        api_key = login_dict.get("api_key")
        url = login_dict.get("url")

        if not api_key or not url:
            return None, None

        return api_key, url

    except (json.JSONDecodeError, OSError):
        return None, None


def save_login(api_key: str, url: str) -> None:
    file = os.path.join(SCRIPTDIR, ".api_key")
    with open(file, "w") as f:
        json.dump({"api_key": api_key, "url": url}, f)
