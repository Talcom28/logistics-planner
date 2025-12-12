def generate_paperwork(cargo_type: str, origin_country: str = None, dest_countries: list = None):
    docs = ["Bill of Lading", "Commercial Invoice", "Packing List"]
    if cargo_type.lower() in {"hazardous", "dangerous", "hazmat"}:
        docs += ["IMDG Declaration", "Safety Data Sheet (SDS)", "UN Number documentation"]
    if cargo_type.lower() in {"perishable", "reefer"}:
        docs += ["Phytosanitary Certificate (if required)", "Cold-chain certificate", "Reefer temperature log"]
    if cargo_type.lower() in {"bulk", "liquid"}:
        docs += ["Certificate of Weight", "Tank/hold cleaning certificates (if required)"]
    # Add origin/destination specific forms in production by mapping countries -> required forms
    return docs