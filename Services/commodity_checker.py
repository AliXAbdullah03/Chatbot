# services/commodity_checker.py

SERVICE_RESTRICTIONS = {
    "ph-uae": [
        "fresh bread", "pastries", "cakes", "perishable", "lottery", "gambling", "bank card",
        "bank cheque", "oxidizer", "peroxide", "liquid fertilizer", "flammable", "plant", "seedling",
        "lv", "prescribed medicine", "injection", "needle", "syringe", "gold", "money", "fashion accessory",
        "pork", "vape", "cigarette", "religious item", "statue", "chicharon"
    ],
    "th-uae": [
        "fresh bread", "pastries", "cakes", "perishable", "lottery", "gambling", "bank card",
        "bank cheque", "oxidizer", "peroxide", "liquid fertilizer", "flammable", "plant", "seedling",
        "lv", "prescribed medicine", "injection", "needle", "syringe", "gold", "money", "fashion accessory",
        "pork", "vape", "cigarette", "religious item", "statue"
    ],
    "uae-ph": [
        "fresh bread", "pastries", "cakes", "perishable", "dairy", "fresh meat", "fresh fruit",
        "lottery", "gambling", "bank card", "bank cheque", "oxidizer", "peroxide", "liquid fertilizer",
        "flammable", "plant", "seedling", "prescribed medicine", "injection", "needle", "syringe",
        "gold", "money", "fashion accessory", "pork", "vape", "cigarette"
    ]
}

SUPPLEMENT_TERMS = ["supplement", "capsule", "powder", "liquid"]


# Normalize string

def normalize(text: str) -> str:
    return text.lower().strip()


def is_commodity_allowed(route: str, item_name: str) -> tuple[bool, str]:
    item = normalize(item_name)
    restricted_terms = SERVICE_RESTRICTIONS.get(route, [])

    for term in restricted_terms:
        if term in item:
            return False, f"Pasensya na po, hindi po pwede ang '{item_name}' sa service na yan po."

    for supplement in SUPPLEMENT_TERMS:
        if supplement in item:
            return True, (
                "Allowed po ang supplements (capsule, liquid, powder), pero may ibang rate at tentative loading schedule po."
            )

    # Additional context-based reminders
    if "clothes" in item:
        return True, "Reminder lang po, LV-branded clothing is allowed pero subject for approval."

    if route == "uae-ph" and "chocolate" in item:
        return True, "Note lang po, if Pix brand po ang chocolate, hindi po siya allowed."

    return True, ""
