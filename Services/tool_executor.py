from tools.booking_form import show_booking_form
from tools.rate_calculator import get_shipping_rate
from tools.volumetric_weight import volumetric_calculator
from tools.dropoff_location import get_dropoff_location
from tools.check_allowed_items import check_allowed_items
from tools.loading_schedule import get_loading_schedule
from tools.pickup_delivery_policy import get_pickup_policy, get_dropoff_policy
from tools.tracking import track_package

def execute_tool(intent: str, sender_id: str, tool_input: dict) -> str:
    route = tool_input.get("route")
    item = tool_input.get("item")
    weight = tool_input.get("weight")

    if intent == "booking":
        return show_booking_form(sender_id, {"route": route, "item": item, "weight": weight})

    elif intent == "rate":
        return get_shipping_rate(sender_id, {"route": route, "weight": weight})

    elif intent == "volumetric":
        return volumetric_calculator(sender_id, {"weight": weight})

    elif intent == "dropoff_location":
        return get_dropoff_location(sender_id, {"route": route})

    elif intent in ["check_allowed_items", "allowed_items"]:
        return check_allowed_items(sender_id, {"route": route, "item": item})

    elif intent == "loading_schedule":
        return get_loading_schedule(sender_id, {"route": route})

    elif intent == "pickup_policy":
        return get_pickup_policy(sender_id, {"route": route, "weight": weight})

    elif intent == "dropoff_policy":
        return get_dropoff_policy(sender_id, {"route": route})

    elif intent == "tracking":
        return track_package(sender_id, tool_input)

    else:
        return "Sorry po, I cannot process this request right now."
