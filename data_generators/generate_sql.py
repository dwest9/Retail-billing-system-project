"""Generates seed data for testing"""
import csv
import datetime
import itertools
import random

import bcrypt

random.seed("Team23")

item_quantities = [1, 2, 3]
quantity_probabilities = [30, 10, 1]

start_day = datetime.date(2023, 7, 1)
end_day = datetime.date(2023, 12, 6)
ORDERS_PER_DAY = 150

payment_types = ["Cash", "Debit", "Credit"]

categories = [
    "Drinks",
    "Snacks",
    "Produce",
    "Bakery",
    "Cosmetics",
    "Gadgets",
    "Fruit",
]

users = ["owner", "cashier", "cashier2", "cashier3", "cashier4"]


cashier_indices = list(range(1, len(users) + 1))
payment_types_indices = list(range(1, len(payment_types) + 1))


def date_range(start_date: datetime.date, end_date: datetime.date):
    """Iterates through range of days

    Args:
        start_date (datetime.date): Start day of range, inclusive
        end_date (datetime.date): End day of the range, exclusive

    Yields:
        datetime.date: Each day within the range
    """
    num_days = (end_date - start_date).days
    for n in range(num_days):
        yield start_date + datetime.timedelta(n)


def create_query(statement: str, values: list[str]) -> str:
    """Creates a query by combining the statement and values

    Args:
        statement (str): Replace statement for the query
        values (list[str]): Values for the query

    Returns:
        str: generated query string
    """
    string = statement
    for index, value in enumerate(values):
        if index == 0:
            string += f"\n\t{value}"
        else:
            string += f",\n\t{value}"
    string += ";"
    return string


# Load all of the customers into a list
with open("test_data/Customers.csv", encoding="utf8") as customer_csv:
    reader = csv.DictReader(customer_csv)
    customers = list(reader)

# Create the payment_types seed query
payment_type_strings = [
    f"({i + 1}, '{payment_type}')" for i, payment_type in enumerate(payment_types)
]

payment_types_statement = create_query(
    "REPLACE INTO payment_types (id, payment_type) VALUES", payment_type_strings
)


# Create the user seed query
def create_user_string(uid: int, user: str) -> str:
    """Creates a string representation of a user

    Args:
        uid (int): id of the user
        user (str): username and password of the user

    Returns:
        str: string representation of the user
    """
    pw_hash = bcrypt.hashpw(user.encode(), bcrypt.gensalt()).decode()
    return f"({uid}, '{user}', '{pw_hash}', {1 if user=='owner' else 0})"


user_strings = [create_user_string(i + 1, user) for i, user in enumerate(users)]

user_statement = create_query(
    "REPLACE INTO users (id, username, user_hash, is_manager) VALUES", user_strings
)

# Create the categories seed query
category_strings = [
    f"({index+1}, '{category}')" for index, category in enumerate(categories)
]


category_statement = create_query(
    "REPLACE INTO categories (id, category) VALUES", category_strings
)

# Create the items seed query
item_strings = []
for count_id, ((category_index, category), b) in enumerate(
    itertools.product(enumerate(categories), range(54))
):
    if category in ("Produce", "Fruit"):
        item_strings.append(
            f"({count_id+1}, '{category} {b}', {b/2+0.49}, 0, 0, {category_index + 1})"
        )
    else:
        item_strings.append(
            f"({count_id+1}, '{category} {b}', {b/2+0.49}, 1, 1, {category_index + 1})"
        )

item_statement = create_query(
    "REPLACE INTO items (id, name, price, gst, pst, category_id) VALUES", item_strings
)


# Generate customer ids and timestamps for orders
inventory_count_timestamps = []
customers_used = []
timestamps = []
customers_ids = []
# Loop all days in range
for d in date_range(start_day, end_day):
    # Add a inventory count for each week
    if d.strftime("%u") == "7":
        ts = datetime.datetime.combine(
            d,
            datetime.time(0, 0, 0),
        )
        inventory_count_timestamps.append(ts)
    for _ in range(ORDERS_PER_DAY):
        # Choose a customer and get an id for it
        customer = random.choice(customers)
        if customer not in customers_used:
            customers_used.append(customer)

        # One offset to switch to database index
        customers_ids.append(customers_used.index(customer) + 1)

        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamps.append(
            datetime.datetime.combine(
                d,
                datetime.time(hour, minute, second),
            )
        )
timestamps.sort()

customers_strings = [
    f"({i+1}, \"{customer['name']}\", '{customer['phone_number']}', '{customer['email']}')"
    for i, customer in enumerate(customers_used)
]

customer_statement = create_query(
    "REPLACE INTO customers (id, customer_name, phone_number, email) VALUES",
    customers_strings,
)

order_strings = []
for count_id, (customer_id, timestamp) in enumerate(zip(customers_ids, timestamps)):
    cashier_id = random.choice(cashier_indices)
    payment_type = random.choice(payment_types_indices)
    order_strings.append(
        f"({count_id+1}, {customer_id}, {cashier_id}, {payment_type}, NULL, '{timestamp}')"
    )

order_statement = create_query(
    "REPLACE INTO orders "
    + "(id, customer_id, user_id, payment_type, order_reference, timestamp) VALUES",
    order_strings,
)

item_ids = list(range(1, len(item_strings) + 1))


order_item_strings = []
for order_index in range(len(customers_ids)):
    # 1 to 7 items per order
    num_items = random.randint(1, 7)
    items = sorted(random.sample(item_ids, k=num_items))
    for item in items:
        quantity = random.choices(item_quantities, quantity_probabilities)[0]
        order_item_strings.append(f"({order_index + 1}, {item}, {quantity})")

order_item_statement = create_query(
    "REPLACE INTO order_items (order_id, item_id, quantity) VALUES", order_item_strings
)

# 1 inventory count per week
inventory_count_strings = []
for count_id, ts in enumerate(inventory_count_timestamps):
    inventory_count_strings.append(f'({count_id +1}, "{ts}")')

inventory_count_query = create_query(
    "REPLACE INTO inventory_counts (id, ts) VALUES", inventory_count_strings
)

# TODO check if there is a better way to generate items
inventory_count_item_strings = []
for count_id in range(1, len(inventory_count_strings) + 1):
    for item_id in item_ids:
        quantity = random.randint(1, 10)
        inventory_count_item_strings.append(f"({count_id}, {item_id}, {quantity})")

inventory_count_item_query = create_query(
    "REPLACE INTO inventory_count_items (count_id, item_id, quantity) VALUES",
    inventory_count_item_strings,
)

# 1 stock adjustment per week
stock_adjustment_strings = []
for adjustment_id, ts in enumerate(inventory_count_timestamps):
    new_ts = ts + datetime.timedelta(hours=1)
    reason = f"Reason {adjustment_id + 1}"
    stock_adjustment_strings.append(f'({adjustment_id + 1}, "{reason}", "{new_ts}")')

stock_adjustment_query = create_query(
    "REPLACE INTO stock_adjustments (id, reason, ts) VALUES", stock_adjustment_strings
)

# TODO check if there is a better way to generate items
stock_adjustment_item_strings = []
for adjustment_id in range(1, len(stock_adjustment_strings) + 1):
    for item_id in item_ids:
        quantity = random.randint(-5, 5)
        stock_adjustment_item_strings.append(
            f"({adjustment_id}, {item_id}, {quantity})"
        )

stock_adjustment_item_query = create_query(
    "REPLACE INTO stock_adjustment_items (adjustment_id, item_id, quantity) VALUES",
    stock_adjustment_item_strings,
)

with open("test_data/seed_data.sql", "w", encoding="utf") as query_file:
    query_file.write("-- AUTOGENERATED\n\n")
    query_file.write(
        "/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;\n"
    )
    query_file.write("/*!40101 SET NAMES  */;\n")
    query_file.write(
        "/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;\n"
    )
    query_file.write(
        "/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;\n"
    )
    query_file.write("/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;\n\n")

    query_file.write("-- Data for payment_types table\n")
    query_file.write('/*!40000 ALTER TABLE "payment_types" DISABLE KEYS */;\n')
    query_file.write(payment_types_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "payment_types" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for users\n")
    query_file.write('/*!40000 ALTER TABLE "users" DISABLE KEYS */;\n')
    query_file.write(user_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "users" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for categories table\n")
    query_file.write('/*!40000 ALTER TABLE "categories" DISABLE KEYS */;\n')
    query_file.write(category_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "categories" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for items table\n")
    query_file.write('/*!40000 ALTER TABLE "items" DISABLE KEYS */;\n')
    query_file.write(item_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "items" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for customers table\n")
    query_file.write('/*!40000 ALTER TABLE "customers" DISABLE KEYS */;\n')
    query_file.write(customer_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "customers" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for orders table\n")
    query_file.write('/*!40000 ALTER TABLE "orders" DISABLE KEYS */;\n')
    query_file.write(order_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "orders" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for order_items table\n")
    query_file.write('/*!40000 ALTER TABLE "order_items" DISABLE KEYS */;\n')
    query_file.write(order_item_statement)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "order_items" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for inventory_counts table\n")
    query_file.write('/*!40000 ALTER TABLE "inventory_counts" DISABLE KEYS */;\n')
    query_file.write(inventory_count_query)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "inventory_counts" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for inventory_count_items table\n")
    query_file.write('/*!40000 ALTER TABLE "inventory_count_items" DISABLE KEYS */;\n')
    query_file.write(inventory_count_item_query)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "inventory_count_items" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for stock_adjustments table\n")
    query_file.write('/*!40000 ALTER TABLE "stock_adjustments" DISABLE KEYS */;\n')
    query_file.write(stock_adjustment_query)
    query_file.write("\n")
    query_file.write('/*!40000 ALTER TABLE "stock_adjustments" ENABLE KEYS */;\n\n')

    query_file.write("-- Data for stock_adjustment_items table\n")
    query_file.write('/*!40000 ALTER TABLE "stock_adjustment_items" DISABLE KEYS */;\n')
    query_file.write(stock_adjustment_item_query)
    query_file.write("\n")
    query_file.write(
        '/*!40000 ALTER TABLE "stock_adjustment_items" ENABLE KEYS */;\n\n'
    )

    query_file.write("/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;\n")
    query_file.write(
        "/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;\n"
    )
    query_file.write(
        "/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;\n"
    )
    query_file.write("/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;\n")
