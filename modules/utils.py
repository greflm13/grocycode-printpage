import os
import re
import json

from reportlab.lib import colors

_OPERATORS = ["!=", "!~", "<=", ">=", "=", "<", ">", "~", "§"]
_OP_PATTERN = "|".join(map(re.escape, _OPERATORS))
QUERY_RE = re.compile(rf"^(?P<field>[A-Za-z_][A-Za-z0-9_]*)(?P<operator>{_OP_PATTERN})(?P<value>.+)$", re.VERBOSE)
BASE_URL_RE = re.compile(r"^https?:\/\/((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?$")
JSON_FILE_RE = re.compile(r"^(?:\.{0,2}\/|\/)?(?:[^\/\0]+\/)*[^\/\0]+\.json$", re.VERBOSE)
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")


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
