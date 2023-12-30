import csv
from datetime import date
import random
import sqlite3
from typing import Optional

import bcrypt
from customer_system import CustomerSystem
from inventory_system import InventorySystem

from order_system import Item, OrderSystem, User
from report_system import ReportSystem


class App:
    """Base class for the app"""

    def __init__(self, uri: str = ":memory:") -> None:
        random.seed("Team 23")
        self.conn = sqlite3.connect(uri)
        self.create_tables()
        self._seed_data_from_file()

        self.order_system = OrderSystem(self.conn)

        self.report_system = ReportSystem(self.conn)

        self.customer_system = CustomerSystem(self.conn)

        self.inventory_system = InventorySystem(self.conn)

    def seed_orders(self):
        """Seed random orders for testing"""
        items = self.get_all_items()
        customers = self.order_system.get_all_customers()
        payment_types = self.get_all_payment_types()
        cashiers = self._get_all_users()
        for customer in customers:
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                num_items = random.randint(1, 10)
                order_items = random.choices(items, k=num_items)
                order_id = self.order_system.new_order(random.choice(cashiers)[0])
                self.order_system.add_customer_to_order(order_id, customer.customer_id)
                for item in order_items:
                    self.order_system.add_order_item(order_id, item.item_id)
                self.order_system.pay_for_order(
                    order_id, random.choice(payment_types)[0]
                )

    def create_tables(self):
        """Create the initial tables"""
        with open("create_tables_sqlite.sql", encoding="utf8") as sql_file:
            self.conn.executescript(sql_file.read())
            self.conn.commit()

    def _seed_data_from_file(self, path: str = "test_data/seed_data.sql"):
        """[Internal] Seed test data from a sql file

        Args:
            path (str, optional): Path to seed file. Defaults to "test_data/seed_data.sql".
        """
        with open(path, encoding="utf8") as sql_file:
            self.conn.executescript(sql_file.read())
            self.conn.commit()

    def seed_customers_from_file(self, path: str = "test_data/Customers.csv"):
        """Seed initial customers from a csv file

        Args:
            path (str, optional): path to csv file. Defaults to "test_data/Customers.csv".
        """
        with open(path, newline="", encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.order_system.create_customer(
                    row["name"], row["phone_number"], row["email"]
                )

    def seed_items_from_file(self, path: str = "test_data/Items.csv"):
        """Seed initial items from a csv file

        Args:
            path (str, optional): path to csv file. Defaults to "test_data/Items.csv".
        """
        categories: dict[str, int] = {}
        with open(path, newline="", encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if categories.get(row["category"]) is None:
                    categories[row["category"]] = self.add_category(row["category"])
                self.add_item(
                    row["name"],
                    float(row["price"]),
                    row["gst"] == "1",
                    row["pst"] == "1",
                    categories[row["category"]],
                )

    def seed_payment_types(self):
        """Seed initial payment types for testing"""
        self.add_payment_type("Cash")
        self.add_payment_type("Debit")
        self.add_payment_type("Credit")

    def seed_users(self):
        """Seed initial users for testing"""
        self.add_user("owner", "owner", True)
        self.add_user("cashier", "cashier", False)
        self.add_user("cashier2", "cashier2", False)
        self.add_user("cashier3", "cashier3", False)
        self.add_user("cashier4", "cashier4", False)

    def login(self, username: str, password: str) -> Optional[User]:
        """Attempt to login

        Args:
            username (str): username to use
            password (str): password to use

        Returns:
            Optional[User]: User if successful, otherwise None
        """
        cur = self.conn.execute(
            "SELECT * FROM users WHERE username = ? LIMIT 1;", (username,)
        )
        user = cur.fetchone()
        if user is None:
            return None
        if not bcrypt.checkpw(password.encode(), user[2].encode()):
            return None

        return user

    def add_payment_type(self, payment_type: str) -> int:
        """Add a new payment type to the database

        Args:
            payment_type (str): display name for payment type

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of new payment type
        """
        cur = self.conn.execute(
            "INSERT INTO payment_types(payment_type) VALUES (?);", (payment_type,)
        )
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def get_all_payment_types(self):
        """Get all payment type from the database

        Returns:
            _type_: all payment types rom the database
        """
        cur = self.conn.execute("SELECT * FROM payment_types;")
        return cur.fetchall()

    def add_user(self, username: str, password: str, is_manager: bool) -> int:
        """Add a new user to the database

        Args:
            username (str): username for the new user
            password (str): password for the new user
            is_manager (bool): is the new user a manager

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of new user
        """
        cur = self.conn.execute(
            "INSERT INTO users(username, user_hash, is_manager) VALUES (?,?,?);",
            (username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()), is_manager),
        )
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def add_category(self, name: str) -> int:
        """Add a new category to the database

        Args:
            name (str): name of the new category

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of the new category
        """
        cur = self.conn.execute("INSERT INTO categories(category) VALUES (?);", (name,))
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def add_item(
        self, name: str, price: float, gst: bool, pst: bool, category_id: int
    ) -> int:
        """Add a new item to the database

        Args:
            name (str): name of the new item
            price (float): price of the new item
            gst (bool): if gst is charged on the item
            pst (bool): if pst is charged on the item
            category_id (int): category for the new item

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of the new item
        """
        cur = self.conn.execute(
            "INSERT INTO items(name, price, gst,pst, category_id) VALUES (?, ?, ?, ?, ?);",
            (name, price, gst, pst, category_id),
        )
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def get_all_items(self) -> list[Item]:
        """Get all items from the database

        Returns:
            list[Item]: list of items from the database
        """
        cur = self.conn.execute("SELECT * FROM items;")
        return list(map(Item.from_row, cur.fetchall()))

    def get_items_by_category(self, category_id: int) -> list[Item]:
        """Get all items from a given category

        Args:
            category_id (int): id of category

        Returns:
            list[Item]: list of items belonging to the category
        """
        cur = self.conn.execute(
            "SELECT * FROM items WHERE category_id = ?;", (category_id,)
        )
        return list(map(Item.from_row, cur.fetchall()))

    def get_all_categories(self) -> dict[str, list[Item]]:
        """Get all categories and items

        Returns:
            dict[str, list[Item]]: map of category name to items
        """
        cur = self.conn.execute("SELECT * FROM categories;")
        d: dict[str, list[Item]] = {}
        for category_id, category_name in cur.fetchall():
            d[category_name] = self.get_items_by_category(category_id)
        return d

    def _get_all_users(self):
        cur = self.conn.execute("SELECT * FROM users;")
        return cur.fetchall()


if __name__ == "__main__":
    app = App()
    # print("Hourly Sales")
    # for hourly_record in app.report_system.get_hourly_sales_for_date(
    #     date(2023, 10, 20)
    # ):
    #     print(hourly_record)
    # print()
    # print("Cashier Sales")
    # for cashier_record in app.report_system.get_cashier_sales_for_date(
    #     date(2023, 10, 20)
    # ):
    #     print(cashier_record)
    # print()
    # print("Item Sales")
    # for item_record in app.report_system.get_item_sales_for_date(date(2023, 10, 20)):
    #     print(item_record)
    # print()
    # for order in app.customer_system.search_orders_by_phone_number("555"):
    #     print(order)
    # print("Inventory")
    # for inventory_record in app.inventory_system.get_inventory_details():
    #     print(inventory_record)
    # print("Count Details")
    # for count_details in app.inventory_system.get_count_details(1):
    #     print(count_details)\

    counts = app.inventory_system.list_inventory_counts()
    report = app.inventory_system.get_inventory_details()
    count = app.inventory_system.get_count_details(counts[-1].count_id)
    
    for i, item in enumerate(report, start=0):
        print(item.name, count[i].item_name)


    print(len(""))