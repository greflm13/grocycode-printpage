import os
import re
import json

from enum import Enum
from importlib.metadata import version, PackageNotFoundError


from ppf.datamatrix import DataMatrix
from reportlab.lib import colors

_OPERATORS = ["!=", "!~", "<=", ">=", "=", "<", ">", "~", "§"]
_OP_PATTERN = "|".join(map(re.escape, _OPERATORS))
QUERY_RE = re.compile(rf"^(?P<field>[A-Za-z_][A-Za-z0-9_]*)(?P<operator>{_OP_PATTERN})(?P<value>.+)$", re.VERBOSE)
BASE_URL_RE = re.compile(r"^https?:\/\/((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?$")
JSON_FILE_RE = re.compile(r"^(?:\.{0,2}\/|\/)?(?:[^\/\0]+\/)*[^\/\0]+\.json$", re.VERBOSE)
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
if "APPDATA" in os.environ:
    CONFIGHOME = os.environ["APPDATA"]
elif "XDG_CONFIG_HOME" in os.environ:
    CONFIGHOME = os.environ["XDG_CONFIG_HOME"]
else:
    CONFIGHOME = os.path.join(os.environ["HOME"], ".config")
CONFIGPATH = os.path.join(CONFIGHOME, "grocycode-printpage")

MAPPINGS = {
    "Product Group": ("product_groups", "product_group_id"),
    "Location": ("locations", "location_id"),
    "Parent Product": ("products", "parent_product_id"),
    "Shopping Location": ("shopping_locations", "shopping_location_id"),
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


def get_version() -> str:
    try:
        return version("grocycode-printpage")
    except PackageNotFoundError:
        return "dev"


def get_bool_matrix(data) -> list[bool]:
    matrix = DataMatrix(f"grcy:p:{data}")
    return matrix.matrix


def add_quiet_zone(matrix, q=1):
    cols = len(matrix[0])
    empty_row = [0] * (cols + 2 * q)

    out = []

    for _ in range(q):
        out.append(empty_row[:])

    for row in matrix:
        out.append([0] * q + row + [0] * q)

    for _ in range(q):
        out.append(empty_row[:])

    return out


def draw_datamatrix_vector(pdf, matrix, x, y, size) -> None:
    matrix = add_quiet_zone(matrix)
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
    if not os.path.exists(CONFIGPATH):
        return None, None

    try:
        with open(CONFIGPATH, "r") as login_file:
            login_dict = json.load(login_file)

        api_key = login_dict.get("api_key")
        url = login_dict.get("url")

        if not api_key or not url:
            return None, None

        return api_key, url

    except (json.JSONDecodeError, OSError):
        return None, None


def save_login(api_key: str, url: str) -> None:
    os.makedirs(CONFIGHOME, exist_ok=True)
    with open(CONFIGPATH, "w") as f:
        json.dump({"api_key": api_key, "url": url}, f)
