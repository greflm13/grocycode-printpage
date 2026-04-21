#!/usr/bin/env python
import requests

from modules.utils import check_or_load_login


def main() -> None:
    ipa_kye, url = check_or_load_login()
    res = requests.get(
        url + "/api/objects/product_barcodes", headers={"accept": "application/json", "GROCY-API-KEY": ipa_kye}
    )
    barcodes = res.json()

    for barcode in barcodes:
        if barcode["amount"] is not None:
            res = requests.put(
                url + f"/api/objects/product_barcodes/{barcode['id']}",
                headers={"accept": "application/json", "GROCY-API-KEY": ipa_kye},
                data={
                    "id": barcode["id"],
                    "product_id": barcode["product_id"],
                    "barcode": barcode["barcode"],
                    "qu_id": barcode["qu_id"],
                    "amount": None,
                    "shopping_location_id": barcode["shopping_location_id"],
                    "last_price": barcode["last_price"],
                    "note": barcode["note"],
                },
            )


if __name__ == "__main__":
    main()
