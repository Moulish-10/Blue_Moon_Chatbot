import mysql.connector
global cnx

# connect to the MySQL database
cnx = mysql.connector.connect(
    host = "localhost",
    user = "user",
    password = "password",
    database = "database_name"
)

# Function to save the order to the database
def get_order_status(order_id: int):

    cursor = cnx.cursor()

    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    cursor.execute(query,(order_id,))

    result = cursor.fetchone()

    cursor.close()

    if result:
        return result[0]
    else:
        return None
    
# Function to get the next order ID from the database
def get_next_order_id():
    cursor = cnx.cursor()

    query = "SELECT MAX(order_id) FROM orders"

    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    # If no orders exist, return 1 as the next order ID.
    if result is None:
        return 1
    else:
        return result + 1  # Otherwise, return the next order ID.

# Function to insert order items into the database  
def insert_order_items(item_id, quantity, order_id):
    try:
        cursor = cnx.cursor()

        cursor.callproc("insert_order_item", (item_id, quantity, order_id))

        cnx.commit()
        cursor.close()
        print("Order item inserted successfully")

        return 0
    
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()
        return -1
    
    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()
        return -1



# Function to insert order tracking information into the database
def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"

    cursor.execute(insert_query, (order_id, status))

    cnx.commit()

    cursor.close()

# Function to get the total order price from the database
def get_total_order_price(order_id):
    cursor = cnx.cursor()

    query = f"SELECT get_total_order_price({order_id})"

    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    return result

# get ordered items from the database
def get_order_items(order_id):

    cursor = cnx.cursor()

    # This query joins orders and menu_items to get the item name and quantity
    query = """
    SELECT menu_items.name, orders.quantity
    FROM orders
    JOIN menu_items ON orders.item_id = menu_items.item_id
    WHERE orders.order_id = %s
    """
    cursor.execute(query, (order_id,))

    result = cursor.fetchall()
    cursor.close()

    # Return the result as a list of dictionaries
    return [{'item_name': item[0], 'quantity': item[1]} for item in result]

