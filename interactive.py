#!/usr/bin/env python
import os
import urllib

import requests
import questionary

from modules.utils import check_or_load_login, get_bool_matrix, draw_datamatrix_vector
from grocycode import create_codepage
from codesheet import create_codesheet

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__)).removesuffix(__package__ if __package__ else "")
OUTDIR = os.path.join(SCRIPTDIR, "output")
STYLE = questionary.Style(
    [
        ("question", "fg:#ff0000 bold"),
        ("answer", "fg:#00ff00 bold"),
        ("pointer", "fg:#0000ff bold"),
        ("highlighted", "fg:#ffff00 bold"),
        ("completion-menu", "bg:#000000"),
        ("completion-menu.completion.current", "bg:#444444"),
    ]
)
MAPPINGS = {
    "product_group_id": "product_groups",
    "location_id": "locations",
    "parent_product_id": "products",
    "shopping_location_id": "shopping_locations",
    "should_not_be_frozen": "products",
}


def stickers(url: str, api_key: str, products: list[dict]):
    choices = [item["name"] for item in products]
    product_name = questionary.autocomplete("Product", choices).ask()
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
    filte = questionary.confirm("Filter list?", False).ask()
    if filte:
        choices = [questionary.Choice(item) for item in MAPPINGS.keys()]
        filters = questionary.checkbox("Which filters?", choices).ask()
        possible = {}
        for filt in filters:
            res = requests.get(
                url=f"{url}/api/objects/{MAPPINGS[filt]}",
                headers={"accept": "application/json", "GROCY-API-KEY": api_key},
            )
            possible[filt] = res.json()
        choices = [
            {
                "type": "select",
                "name": item,
                "message": f"Filter for {item}:",
                "choices": [questionary.Choice(value["name"], value["id"]) for value in values],
            }
            for item, values in possible.items()
        ]
        values = questionary.prompt(choices)
        queries = [urllib.parse.quote(f"{k}={v}") for k, v in values.items()]
        res = requests.get(
            f"{url}/api/objects/products?query%5B%5D={'&query%5B%5D='.join(queries)}",
            headers={"accept": "application/json", "GROCY-API-KEY": api_key},
        )
        products = res.json()
    choices = [questionary.Choice(item["name"], idx) for idx, item in enumerate(products)]
    selected = questionary.checkbox("Products:", choices).ask()
    prods = []
    for idx in selected:
        prods.append(products[idx])
    create_codesheet(prods, os.path.join(OUTDIR, "codesheet.pdf"))


def main() -> None:
    os.makedirs(OUTDIR, exist_ok=True)
    api_key, url = check_or_load_login()
    typ = questionary.select("Which type of pdf do you want to generate?", ["stickers", "list"]).ask()
    res = requests.get(url + "/api/objects/products", headers={"accept": "application/json", "GROCY-API-KEY": api_key})
    products = res.json()
    if typ is None:
        return
    if typ == "stickers":
        stickers(url, api_key, products)
    if typ == "list":
        lost(url, api_key, products)


if __name__ == "__main__":
    main()
