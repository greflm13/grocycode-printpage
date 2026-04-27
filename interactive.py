#!/usr/bin/env python
import os
import urllib

import requests
import questionary

from modules.utils import check_or_load_login, get_bool_matrix, MAPPINGS
from grocycode import create_codepage
from codesheet import create_codesheet

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
OUTDIR = os.path.join(SCRIPTDIR, "output")
STYLE = questionary.Style(
    [
        ("answer", "fg:#f6f6f6"),
        ("checkbox-selected", "fg:#6fd80d bold"),
        ("checkbox", "fg:#d7dae0"),
        ("completion-menu.completion.current", "bg:#528bff fg:#16171d bold"),
        ("completion-menu.completion", "bg:#16171d fg:#d7dae0"),
        ("completion-menu", "bg:#16171d fg:#d7dae0"),
        ("cursor-line", "bg:#1e2029"),
        ("cursor", "fg:#16171d bg:#528bff"),
        ("disabled", "fg:#d7dae0"),
        ("error", "fg:#ff3f4f bold"),
        ("frame.border", "fg:#528bff"),
        ("highlighted", "fg:#ffd945 bold"),
        ("hint", "fg:#19d1e5"),
        ("instruction", "fg:#d7dae0"),
        ("pointer", "fg:#528bff bold"),
        ("question", "fg:#6fd80d bold"),
        ("radiolist-selected", "fg:#6fd80d bold"),
        ("radiolist", "fg:#d7dae0"),
        ("selected-focused", "fg:#ffd945 bold"),
        ("selected", "fg:#ffd945"),
        ("separator", "fg:#d7dae0"),
        ("text", "fg:#f6f6f6"),
        ("warning", "fg:#ffd945"),
    ]
)


def stickers(url: str, api_key: str, products: list[dict]):
    choices = [item["name"] for item in products]
    product_name = questionary.autocomplete("Product", choices, style=STYLE).ask()
    if product_name is None:
        return

    res = requests.get(
        url=f"{url}/api/objects/products?query%5B%5D=name%3D{product_name}",
        headers={"accept": "application/json", "GROCY-API-KEY": api_key},
    )
    try:
        product_id = res.json()[0]["id"]
    except IndexError:
        raise RuntimeError("Product not found: %s" % product_name)
    matrix = get_bool_matrix(product_id)
    create_codepage(matrix, os.path.join(OUTDIR, product_name + ".pdf"), product_name)


def lost(url: str, api_key: str, products: list[dict]):
    filte = questionary.confirm("Filter list?", False, style=STYLE).ask()
    if filte:
        choices = [questionary.Choice(item) for item in MAPPINGS.keys()]
        filters = questionary.checkbox("Which filters?", choices, style=STYLE).ask()
        possible = {}
        for filt in filters:
            res = requests.get(
                url=f"{url}/api/objects/{MAPPINGS[filt][0]}",
                headers={"accept": "application/json", "GROCY-API-KEY": api_key},
            )
            possible[filt] = sorted(res.json(), key=lambda x: x["name"])
        choices = [
            {
                "type": "select",
                "name": item,
                "message": f"Filter for {item}:",
                "style": STYLE,
                "choices": [questionary.Choice(value["name"], value["id"]) for value in values],
            }
            for item, values in possible.items()
        ]
        values = questionary.prompt(choices)
        queries = [urllib.parse.quote(f"{MAPPINGS[k][1]}={v}") for k, v in values.items()]
        res = requests.get(
            f"{url}/api/objects/products?query%5B%5D={'&query%5B%5D='.join(queries)}",
            headers={"accept": "application/json", "GROCY-API-KEY": api_key},
        )
        products = sorted(res.json(), key=lambda x: x["name"])
    choices = [questionary.Choice(item["name"], idx) for idx, item in enumerate(products)]
    selected = questionary.checkbox("Products:", choices, style=STYLE).ask()
    prods = []
    for idx in selected:
        prods.append(products[idx])
    create_codesheet(prods, os.path.join(OUTDIR, "codesheet.pdf"))


def main() -> None:
    os.makedirs(OUTDIR, exist_ok=True)
    api_key, url = check_or_load_login()
    typ = questionary.select("Which type of pdf do you want to generate?", ["stickers", "list"], style=STYLE).ask()
    res = requests.get(url + "/api/objects/products", headers={"accept": "application/json", "GROCY-API-KEY": api_key})
    products = sorted(res.json(), key=lambda x: x["name"])
    if typ is None:
        return
    if typ == "stickers":
        stickers(url, api_key, products)
    if typ == "list":
        lost(url, api_key, products)


if __name__ == "__main__":
    main()
