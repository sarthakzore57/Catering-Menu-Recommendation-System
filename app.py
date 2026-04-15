from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


MENU_ITEMS = [
    {
        "id": 1,
        "name": "Veg Spring Rolls",
        "category": "Starter",
        "type": "veg",
        "price": 120,
        "value": 8,
        "description": "Crispy vegetable rolls served with sweet chili dip.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Spring%20roll%20001.jpg",
    },
    {
        "id": 2,
        "name": "Chicken Tikka Skewers",
        "category": "Starter",
        "type": "non-veg",
        "price": 180,
        "value": 10,
        "description": "Smoky chicken skewers marinated with aromatic spices.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Chicken%20vegetable%20skewers.jpg",
    },
    {
        "id": 3,
        "name": "Paneer Butter Masala",
        "category": "Main Course",
        "type": "veg",
        "price": 240,
        "value": 11,
        "description": "Rich paneer curry in a smooth tomato-butter gravy.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Paneer%20Butter%20Masala.jpg",
    },
    {
        "id": 4,
        "name": "Veg Biryani",
        "category": "Main Course",
        "type": "veg",
        "price": 210,
        "value": 10,
        "description": "Fragrant basmati rice cooked with vegetables and herbs.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Indian%20Veg%20Biryani.jpg",
    },
    {
        "id": 5,
        "name": "Butter Chicken",
        "category": "Main Course",
        "type": "non-veg",
        "price": 280,
        "value": 12,
        "description": "Classic creamy chicken curry with balanced spices.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Food%20Indian%20butter%20chicken%20%2852843424475%29.jpg",
    },
    {
        "id": 6,
        "name": "Garlic Naan Basket",
        "category": "Bread",
        "type": "veg",
        "price": 90,
        "value": 6,
        "description": "Soft naan brushed with garlic butter and herbs.",
        "image": "https://images.unsplash.com/photo-1574653853027-5d5f8d1f3b5f?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": 7,
        "name": "Gulab Jamun",
        "category": "Dessert",
        "type": "veg",
        "price": 110,
        "value": 7,
        "description": "Warm milk-solid dumplings soaked in cardamom syrup.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Gulab%20jamun%201.jpg",
    },
    {
        "id": 8,
        "name": "Fruit Custard",
        "category": "Dessert",
        "type": "veg",
        "price": 100,
        "value": 6,
        "description": "Chilled custard topped with seasonal fruits.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Custard.jpg",
    },
    {
        "id": 9,
        "name": "Fresh Lime Soda",
        "category": "Beverage",
        "type": "veg",
        "price": 70,
        "value": 5,
        "description": "Refreshing lime drink with a sparkling finish.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Glass%20of%20lemonade.jpg",
    },
    {
        "id": 10,
        "name": "Mini Samosa Platter",
        "category": "Starter",
        "type": "veg",
        "price": 80,
        "value": 6,
        "description": "Bite-sized samosas with spiced potato filling.",
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Samosa%20with%20tamarind%20chutney%20and%20tomato%20sauce.jpg",
    },
]


def greedy_menu_recommendation(
    budget: float,
    people: int | None = None,
    preference: str = "all",
    categories: list[str] | None = None,
):
    filtered_items = MENU_ITEMS

    if preference in {"veg", "non-veg"}:
        filtered_items = [item for item in filtered_items if item["type"] == preference]

    if categories:
        allowed = {category.lower() for category in categories}
        filtered_items = [
            item for item in filtered_items if item["category"].lower() in allowed
        ]

    if not filtered_items:
        return {
            "selected_items": [],
            "total_cost": 0,
            "remaining_budget": budget,
            "total_value": 0,
            "estimated_people": people or 0,
            "message": "No menu items match the selected filters.",
        }

    budget_per_person = budget / people if people and people > 0 else budget

    ranked_items = sorted(
        filtered_items,
        key=lambda item: (
            item["value"] / item["price"],
            item["value"],
            -item["price"],
        ),
        reverse=True,
    )

    def build_greedy_cycle(available_budget: float, current_quantities: dict[int, int]):
        cycle_items = []
        cycle_cost = 0
        cycle_value = 0

        for item in ranked_items:
            if people and current_quantities.get(item["id"], 0) >= people:
                continue
            if cycle_cost + item["price"] <= available_budget:
                cycle_items.append(item)
                cycle_cost += item["price"]
                cycle_value += item["value"]

        return cycle_items, cycle_cost, cycle_value

    total_cost = 0
    total_value = 0
    selected_items = []
    item_summary = {}
    cycle_breakdown = []
    remaining_budget = budget
    cycle_number = 1
    current_quantities = {}

    while remaining_budget >= min(item["price"] for item in ranked_items):
        cycle_items, cycle_cost, cycle_value = build_greedy_cycle(
            remaining_budget,
            current_quantities,
        )

        if not cycle_items:
            break

        selected_items.extend(cycle_items)
        total_cost += cycle_cost
        total_value += cycle_value
        remaining_budget = round(budget - total_cost, 2)

        cycle_breakdown.append(
            {
                "cycle_number": cycle_number,
                "items_count": len(cycle_items),
                "cycle_cost": cycle_cost,
                "cycle_value": cycle_value,
            }
        )

        for item in cycle_items:
            if item["id"] not in item_summary:
                item_summary[item["id"]] = {
                    **item,
                    "quantity": 0,
                    "subtotal": 0,
                    "total_value": 0,
                }
            item_summary[item["id"]]["quantity"] += 1
            item_summary[item["id"]]["subtotal"] += item["price"]
            item_summary[item["id"]]["total_value"] += item["value"]
            current_quantities[item["id"]] = item_summary[item["id"]]["quantity"]

        cycle_number += 1

    aggregated_items = sorted(
        item_summary.values(),
        key=lambda item: (
            item["quantity"],
            item["total_value"] / item["subtotal"],
            item["total_value"],
        ),
        reverse=True,
    )

    total_portions = sum(item["quantity"] for item in aggregated_items)

    if people and people > 0:
        affordable_count = sum(
            1 for item in filtered_items if item["price"] <= budget_per_person
        )
        estimated_people = min(total_portions, people)
    else:
        affordable_count = len(aggregated_items)
        estimated_people = total_portions

    message = (
        "Recommended menu generated using repeated greedy cycles until the budget was nearly exhausted."
        if aggregated_items
        else "The current budget is too low for the selected filters."
    )

    if aggregated_items and people:
        message = (
            "Recommended menu generated using repeated greedy cycles with each item's quantity capped by the guest count."
        )

    return {
        "selected_items": aggregated_items,
        "total_cost": total_cost,
        "remaining_budget": round(budget - total_cost, 2),
        "total_value": total_value,
        "estimated_people": estimated_people,
        "affordable_item_count": affordable_count,
        "total_portions": total_portions,
        "cycle_count": len(cycle_breakdown),
        "cycle_breakdown": cycle_breakdown,
        "message": message,
    }


@app.route("/")
def index():
    categories = sorted({item["category"] for item in MENU_ITEMS})
    return render_template("index.html", menu_items=MENU_ITEMS, categories=categories)


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}

    try:
        budget = float(data.get("budget", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Please enter a valid budget."}), 400

    if budget <= 0:
        return jsonify({"error": "Budget must be greater than zero."}), 400

    people = data.get("people")
    try:
        people = int(people) if people not in (None, "", 0, "0") else None
    except (TypeError, ValueError):
        return jsonify({"error": "Number of people must be a whole number."}), 400

    preference = str(data.get("preference", "all")).lower()
    categories = data.get("categories", [])
    if not isinstance(categories, list):
        categories = []

    recommendation = greedy_menu_recommendation(
        budget=budget,
        people=people,
        preference=preference,
        categories=categories,
    )
    recommendation["budget"] = budget
    recommendation["people"] = people
    return jsonify(recommendation)


if __name__ == "__main__":
    app.run(debug=True)
