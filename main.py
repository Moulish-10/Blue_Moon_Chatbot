#import a necessary libraries
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import generator
import db_helper

# Create a FastAPI instance
app = FastAPI()

# Initialize an empty dictionary to store in-progress orders
inprogress_orders = {}

# Create a route to handle incoming requests
@app.post("/")

async def handle_request(request:Request):
    payload = await request.json()

# Extract the intent and parametes from the payload
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generator.extract_session_id(output_contexts[0]['name'])



    intent_handler_dict = {
        "Order_add_context : Ongoing_order": add_to_order,
        "Order_completion_context : Ongoing-order": complete_order,
        "Order_remove_context : Oongoing-order" : remove_from_order,
        "Tracking_order_context : Ongoing-tracking" : track_order
    }

    return intent_handler_dict[intent](parameters, session_id)

# Create a function to handle the order addition intent
def add_to_order(parameters:dict, session_id :str):
    cafe_items = parameters["cafe_items"]
    quantity = parameters["number"]

# check if the length of cafe_items and quantity are equal
    if len(cafe_items) != len(quantity):
        fulfillment_text = "Sorry, I don't understand your order. Can you please specify the items."
#check if the session_id is in inprogress_orders
    else:
        new_item_dict = dict(zip(cafe_items, quantity))
        if session_id in inprogress_orders:
            current_item_dict = inprogress_orders[session_id]
            current_item_dict.update(new_item_dict)
            inprogress_orders[session_id] = current_item_dict
# if the session_id is not in inprogress_orders add the new_item_dict to inprogress_orders
        else:
            inprogress_orders[session_id] = new_item_dict
        
# create a string from the food dictionary
        order_str = generator.get_str_from_food_dict(inprogress_orders[session_id])

        fulfillment_text = f"So far, you have ordered {order_str}. Is there anything else you would like to add:"

#return the fulfillment_text as a JSON response
        return JSONResponse(content  ={
            "fulfillmentText" : fulfillment_text,
        })


from fastapi.responses import JSONResponse

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order, please?"
        })

    current_order = inprogress_orders[session_id]
    cafe_items = parameters["cafe_items"]

    # ✨ Fix: Make sure cafe_items is a list
    if isinstance(cafe_items, str):
        cafe_items = [cafe_items]

    removed_items = []
    no_such_items = []

    for item in cafe_items:
        if item in current_order:
            removed_items.append(item)
            del current_order[item]
        else:
            no_such_items.append(item)

    # Build the response message
    fulfillment_text = ""

    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order. "

    if no_such_items:
        fulfillment_text += f"Your current order does not have {', '.join(no_such_items)}. "

    if not current_order:
        fulfillment_text += "Your order is empty now."
    else:
        order_str = generator.get_str_from_food_dict(current_order)
        fulfillment_text += f"Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
    })



# Function to complete the user's order and save it
def complete_order(parameters: dict, session_id: str):
    # Check if the session has an active order
    if session_id not in inprogress_orders:
        fulfillment_text = "Sorry, I don't have any order for you. Can you please add items to your order first."
    
    else:
        # Fetch the current in-progress order
        order = inprogress_orders[session_id]

        # Try to save the order to the database
        order_id = save_to_db(order)

        # Check if the saving was successful
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't save your order. Please try again."
        
        else:
            # Get the total order amount from database
            order_total = db_helper.get_total_order_price(order_id)

            # Build the success message with order id and total
            fulfillment_text = (
                f"Awesome ☺️ we have placed your order. "
                f"Your order id is : {order_id}. "
                f"Your order total amount is {order_total} Rs which you can pay at the time of delivery! "
                f"Thanks for visiting Blue_Moon_Cafe!😍"
            )

        # Remove the completed order from in-progress orders
        del inprogress_orders[session_id]

    # Return the final message as a JSON response to Dialogflow
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
    })




# Function to track the status of an order
def track_order(parameters: dict, session_id: str):
    # Get the order_id from user input parameters
    order_id = int(parameters["number"])

    # Fetch the current status of the given order_id from the database
    order_status = db_helper.get_order_status(order_id)

    # Fetch the oredred items from the database
    order_items = db_helper.get_order_items(order_id)


    # Check if the order status was found
    if order_status:
        # If found, create a success message
        fulfillment_text = f"Your order status for order id {order_id} is '{order_status}'."

        if order_items:
            items_str = ', '.join([f"{item['item_name']} (x{item['quantity']})" for item in order_items])
            fulfillment_text = f"Your order status for order ID {order_id} is: {order_status}. Here are the items in your order: {items_str}"
        else:
            fulfillment_text = f"Your order status for order ID {order_id} is: {order_status}. But there are no items associated with this order."

    else:
        # If not found, create an error message
        fulfillment_text = f"Order id {order_id} not found."

    # Return the response back to Dialogflow as JSON
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
    })



# This function saves the order to the database
def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()  # Get the next order ID

    # Iterate over the order items and insert them
    for cafe_item, quantity in order.items():
        recode = db_helper.insert_order_items(cafe_item, quantity, next_order_id)
        if recode == -1:  # If there was an error inserting the order item
            return -1
    
    # Insert order tracking information
    db_helper.insert_order_tracking(next_order_id, "In Progress")
    
    return next_order_id

        