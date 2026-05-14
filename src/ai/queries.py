PREDEFINED_QUERIES = {
    "Battery Cathodes & Anodes": [
        "Suggest safer and affordable alternatives to cobalt-based high-nickel cathodes",
        "Find lightweight conductive materials for EV batteries",
        "Looking for a cheap, highly stable iron-based cathode material",
        "Identify stable lithium-rich metallic compounds",
        "Suggest a high-capacity manganese-based cathode that avoids costly nickel",
        "Find a stable, non-metallic sodium compound for grid storage",
        "Looking for an ultra-stable lithium phosphate material",
        "Recommend a conductive copper-based material for battery current collectors",
        "Find an affordable, stable aluminum-based battery component",
        "What is a highly stable, metallic compound containing titanium and lithium?"
    ],
    "Aerospace & Lightweight": [
        "I need an extremely lightweight metallic conductor for aerospace applications",
        "Find a stable, low-density aluminum alloy alternative",
        "Suggest a lightweight, highly stable non-metal for structural use",
        "Looking for a low-density titanium-based metallic material",
        "Identify ultra-lightweight materials containing sodium or lithium",
        "Find a stable, lightweight material that avoids heavy metals like iron and manganese",
        "Suggest a low-density, affordable metallic compound",
        "Find a lightweight non-metal with a wide band gap",
        "Looking for an affordable, lightweight material without copper or nickel",
        "Identify the most stable lightweight metallic compound available"
    ],
    "Cost-Effective Grid Storage": [
        "Suggest an ultra-cheap, highly stable material for bulk energy storage",
        "Find a stable, low-cost sodium-based semiconductor",
        "Looking for an affordable, iron-rich metallic compound",
        "Recommend a cheap, stable material without cobalt or lithium",
        "Find a highly stable, low-cost manganese oxide alternative",
        "Suggest an affordable, non-metallic phosphorus compound",
        "Identify a low-cost, conductive material containing copper and iron",
        "Find a cheap, stable alternative to titanium-based storage materials",
        "Looking for a highly abundant, low-cost metallic material",
        "Suggest an affordable sodium and phosphorus based stable compound"
    ],
    "Semiconductors & Electronics": [
        "Find a cheap, highly stable semiconductor without lithium or manganese",
        "Looking for a non-metallic material with a very wide band gap",
        "Suggest a stable, non-metallic copper compound for electronics",
        "Find an affordable, stable titanium-based semiconductor",
        "Identify a non-metallic iron compound with a moderate band gap",
        "Looking for a highly stable, low-density semiconductor",
        "Suggest a cheap, non-metallic aluminum compound",
        "Find a stable semiconductor containing nickel but no cobalt",
        "Looking for an affordable, non-metallic compound with phosphorus",
        "Identify a highly stable, wide band gap material without sodium"
    ],
    "Extreme Constraints": [
        "Find a stable material that avoids all battery metals (Li, Co, Ni, Mn)",
        "Looking for a highly conductive, ultra-dense metallic material",
        "Suggest the absolute cheapest, most stable non-metal available",
        "Find a metallic material containing only iron and titanium",
        "Identify a highly stable material that strictly avoids oxygen and fluorine",
        "Looking for an affordable, low-density metal containing copper",
        "Suggest a highly stable, non-metallic compound with exactly zero band gap",
        "Find a cheap, dense semiconductor without aluminum or phosphorus",
        "Looking for a highly stable metallic compound with sodium and manganese",
        "Identify the most affordable, lightweight, non-metallic material available"
    ]
}

# Flatten the queries into a single list for random selection
ALL_QUERIES = [query for category in PREDEFINED_QUERIES.values() for query in category]
