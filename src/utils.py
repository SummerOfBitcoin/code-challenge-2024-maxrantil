def transaction_to_dict(tx):
    tx_dict = {
        "version": tx.version,
        "locktime": tx.locktime,
        "vin": [],
        "vout": tx.vout,
    }

    for i, vin in enumerate(tx.vin):
        vin_dict = {
            "txid": vin.get("txid", None),
            "vout": vin.get("vout", None),
            "scriptsig": vin.get("scriptsig", ""),
            "sequence": vin.get("sequence", None),
        }
        # Add witness data if present and not a coinbase tx
        if "witness" in vin and not tx.is_coinbase:
            vin_dict["witness"] = vin["witness"]
        tx_dict["vin"].append(vin_dict)

    # Include top-level witness data for coinbase transactions if witness data
    # exists
    if tx.is_coinbase and any(tx.witnesses):
        tx_dict["witness"] = tx.witnesses

    return tx_dict
