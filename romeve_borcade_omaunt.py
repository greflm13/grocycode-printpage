#!/usr/bin/env python
import json

import requests

from modules.utils import check_or_load_login, index_by_key


def main() -> None:
    ipa_kye, url = check_or_load_login()
    res = requests.get(
        url + "/api/objects/product_barcodes", headers={"accept": "application/json", "GROCY-API-KEY": ipa_kye}
    )
    barcodes = res.json()
    res = requests.get(url + "/api/objects/products", headers={"accept": "application/json", "GROCY-API-KEY": ipa_kye})
    products = index_by_key(res.json(), "id")

    for barcode in barcodes:
        if barcode["amount"] is not None:
            print(
                f'removing barcode amount from product "{products[barcode["product_id"]]["name"]}" barcode {barcode["barcode"]}'
            )
            res = requests.put(
                url + f"/api/objects/product_barcodes/{barcode['id']}",
                headers={"accept": "application/json", "GROCY-API-KEY": ipa_kye, "Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "id": barcode["id"],
                        "product_id": barcode["product_id"],
                        "barcode": barcode["barcode"],
                        "qu_id": barcode["qu_id"],
                        "amount": None,
                        "shopping_location_id": barcode["shopping_location_id"],
                        "last_price": barcode["last_price"],
                        "note": barcode["note"],
                    }
                ),
            )


if __name__ == "__main__":
    main()
