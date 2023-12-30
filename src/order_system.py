"""Main Report Module"""
from dataclasses import dataclass
import sqlite3
from typing import Any, Optional
import functools


@dataclass
class Item:
    """Represents an item"""

    item_id: int
    name: str
    price: float
    category: int
    gst: bool
    pst: bool

    @staticmethod
    def from_row(row: Any) -> "Item":
        """Converts a sqlite row to an Item

        Args:
            row (Any): Row from the database

        Returns:
            Item: an Item from the database
        """
        item_id, name, price, gst, pst, category_id = row
        return Item(item_id, name, price, category_id, gst, pst)


@dataclass
class ItemQuantity(Item):
    """Represents an item with a quantity attached"""

    quantity: int

    @staticmethod
    def from_row(row: Any) -> "ItemQuantity":
        """Converts a sqlite row to an ItemQuantity

        Args:
            row (Any): Row from the database

        Returns:
            ItemQuantity: an ItemQuantity from the database
        """
        item_id, quantity, name, price, gst, pst, category_id = row
        return ItemQuantity(
            item_id=item_id,
            quantity=quantity,
            name=name,
            price=price,
            category=category_id,
            gst=gst,
            pst=pst,
        )

    def __add__(self, item_quantity):
        if item_quantity.item_id == self.item_id:
            self.quantity += item_quantity.item_id
            return True
        return False

    def subtotal(self) -> float:
        """Calculates the subtotal of this item

        Returns:
            float: subtotal of this ItemQuantity
        """
        return self.price * self.quantity

    def get_gst(self) -> float:
        """Calculates the gst of the item(if applicable)

        Returns:
            float: gst on this ItemQuantity
        """
        return self.price * self.quantity * int(self.gst) * 0.05

    def get_pst(self) -> float:
        """Calculates the pst of the item(if applicable)

        Returns:
            float: pst on this ItemQuantity
        """
        return self.price * self.quantity * int(self.pst) * 0.06

    def total(self) -> float:
        """Calculates the total of the item

        Returns:
            float: total of the ItemQuantity
        """
        return self.subtotal() + self.get_gst() + self.get_pst()


@dataclass
class Order:
    """Represents an order"""

    order_id: int
    customer_id: int
    user_id: int
    payment: Optional[int]
    order_reference: Optional[int]
    timestamp: str
    items: list[ItemQuantity]
    order_updated: bool

    @staticmethod
    def from_row(row: Any) -> "Order":
        """Converts a sqlite row to an Order

        Args:
            row (Any): Row from the database

        Returns:
            Order: a Order from the database
        """
        (
            order_id,
            customer_id,
            user_id,
            payment_type,
            order_reference,
            timestamp,
            order_updated,
        ) = row
        return Order(
            order_id,
            customer_id,
            user_id,
            payment_type,
            order_reference,
            timestamp,
            [],
            order_updated,
        )

    def calculate_subtotal(self) -> float:
        """Calculates the subtotal of this order

        Returns:
            float: subtotal of this order
        """
        return functools.reduce(lambda a, b: a + b.subtotal(), self.items, 0.0)

    def calculate_gst(self) -> float:
        """Calculates the gst on the order

        Returns:
            float: gst of this order
        """
        return functools.reduce(lambda a, b: a + b.get_gst(), self.items, 0.0)

    def calculate_pst(self) -> float:
        """Calculates the pst on the order

        Returns:
            float: pst of this order
        """
        return functools.reduce(lambda a, b: a + b.get_pst(), self.items, 0.0)

    def calculate_total(self) -> float:
        """Calculates the total of the order

        Returns:
            float: the total of this order
        """
        return functools.reduce(lambda a, b: a + b.total(), self.items, 0.0)

    def to_string(self) -> str:
        """Creates a string representation of this order as a bill

        Returns:
            str: bill for this order
        """
        string = ""
        if self.order_reference is not None:
            string += "RETURN\n"
            string += f"Original Order: {self.order_reference}\n"
        string += (
            f"Bill Number: {self.order_id}\n"
            + f"Customer ID: {self.customer_id}\n"
            + f"User ID: {self.user_id}\n"
            + f"Payment: {self.payment}\n"
            + f"Timestamp: {self.timestamp}\n"
        )

        for item in self.items:
            string += f" - {item.name}  x{item.quantity}  ${item.subtotal():.2f}\n"
        string += f"Subtotal: {self.calculate_subtotal():.2f}\n"
        string += f"GST: {self.calculate_gst():.2f}\n"
        string += f"PST: {self.calculate_pst():.2f}\n"
        string += f"Total: {self.calculate_total():.2f}"
        return string


@dataclass
class OrderSummary:
    """Represents the summary of an order"""

    order_id: int
    customer_id: Optional[int]
    user_id: int
    payment_type: int
    timestamp: str
    num_items: int
    subtotal: float
    gst_total: float
    pst_total: float

    @staticmethod
    def from_row(row: Any) -> "OrderSummary":
        """Converts a sqlite row to an order

        Args:
            row (Any): Row from the database

        Returns:
            OrderSummary: OrderSummary from the database
        """
        (
            order_id,
            customer_id,
            user_id,
            payment_type,
            timestamp,
            num_items,
            subtotal,
            gst_total,
            pst_total,
        ) = row
        return OrderSummary(
            order_id,
            customer_id,
            user_id,
            payment_type,
            timestamp,
            num_items,
            subtotal,
            gst_total,
            pst_total,
        )


@dataclass
class Customer:
    """Represents a customer from the database"""

    customer_id: int
    name: str
    phone_number: Optional[str]
    email: Optional[str]

    @staticmethod
    def from_row(row: Any) -> "Customer":
        """Converts a sqlite row to a Customer

        Args:
            row (Any): Row from the database

        Returns:
            Customer: a Customer from the database
        """
        customer_id, name, phone_number, email = row
        return Customer(customer_id, name, phone_number, email)


@dataclass
class User:
    """Represents a user from the database"""

    user_id: int
    username: int
    is_manager: bool

    @staticmethod
    def from_row(row: Any) -> "User":
        """Converts a sqlite row to a User

        Args:
            row (Any): Row from the database

        Returns:
            User: a User from the database
        """
        user_id, username, _, is_manager = row
        return User(user_id, username, is_manager)


class OrderSystem:
    """Order System class"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def new_order(self, user_id: int, customer_id: Optional[int] = None) -> int:
        """Create a new order

        Args:
            user_id (int): id of user who creates the order
            customer_id (Optional[int], optional): id of customer. Defaults to None.

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of the new order
        """
        cur = self.conn.execute(
            "INSERT INTO orders(customer_id, user_id) VALUES (?,?);",
            (customer_id, user_id),
        )
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def new_return_order(
        self, user_id: int, order_id: int, customer_id: Optional[int] = None
    ) -> int:
        """Create a new return transaction, linking to a previous order

        Args:
            user_id (int): id of the user who creates the transaction
            order_id (int): id of the original order
            customer_id (Optional[int], optional): id of customer. Defaults to None.

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of new order
        """
        cur = self.conn.execute(
            "INSERT INTO orders(user_id, order_reference, customer_id) VALUES (?, ?, ?);",
            (user_id, order_id, customer_id),
        )
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def set_order_item(self, order_id: int, item_id: int, quantity: int):
        """Sets the quantity of an item on an order

        Args:
            order_id (int): id of the order
            item_id (int): id of the item
            quantity (int): quantity of the item
        """
        self.conn.execute(
            "INSERT INTO order_items (order_id, item_id, quantity) VALUES (?, ?, ?);",
            (order_id, item_id, quantity),
        )
        self.conn.commit()

    def add_customer_to_order(self, order_id: int, customer_id: int):
        """Link a customer to an order

        Args:
            order_id (int): id of order
            customer_id (int): id of customer
        """
        self.conn.execute(
            "UPDATE orders SET customer_id = ? WHERE id = ?;", (customer_id, order_id)
        )
        self.conn.commit()

    def pay_for_order(self, order_id: int, payment_type: int):
        """Marks an order as paid for

        Args:
            order_id (int): id of order to pay for
            payment_type (int): id of payment type
        """
        self.conn.execute(
            "UPDATE orders SET payment_type = ? WHERE id = ?;",
            (payment_type, order_id),
        )
        self.conn.commit()

    def order_paid(self, order_id: int) -> bool:
        """Checks if an order is marked paid

        Args:
            order_id (int): id of order to check

        Returns:
            bool: true if paid, otherwise false
        """
        cur = self.conn.execute(
            "SELECT payment_type FROM orders WHERE id = ?;", (order_id,)
        )
        return cur.fetchone()[0] is not None

    def add_order_item(self, order_id: int, item_id: int):
        """Add item to an order

        Args:
            order_id (int): order to add item to
            item_id (int): id of item to add
        """
        self.conn.execute(
            """
INSERT INTO
    order_items(order_id, item_id, quantity)
VALUES
    (?, ?, ?) ON CONFLICT(order_id, item_id) DO
UPDATE
SET
    quantity = quantity + 1;
""",
            (order_id, item_id, 1),
        )
        self.conn.commit()

    def remove_order_item(self, order_id: int, item_id: int):
        """Remove an item from the order

        Args:
            order_id (int): order to remove item from
            item_id (int): id of item to remove
        """
        self.conn.execute(
            """
UPDATE
    order_items
SET
    quantity = max(quantity - 1, 0)
WHERE
    order_id = ?
    AND item_id = ?;
""",
            (order_id, item_id),
        )
        self.conn.commit()

    def get_order_details(self, order_id: int) -> Order:
        """Get details of an order

        Args:
            order_id (int): id of order to get

        Returns:
            Order: details of the order
        """
        cur = self.conn.execute(
            """
SELECT id,
    customer_id,
    user_id,
    payment_type,
    order_reference,
    timestamp,
    EXISTS(
        SELECT 1
        FROM orders
        WHERE order_reference = o.id
    ) AS order_updated
FROM orders o
WHERE id = ?;
""",
            (order_id,),
        )
        cur2 = self.conn.execute(
            """
SELECT
    items.id,
    quantity,
    name,
    price,
    gst,
    pst,
    category_id
FROM
    order_items
    LEFT JOIN items ON order_items.item_id = items.id
WHERE
    order_items.order_id = ?;
""",
            (order_id,),
        )
        order = Order.from_row(cur.fetchone())
        order.items = list(map(ItemQuantity.from_row, cur2.fetchall()))
        return order

    def get_order_details_for_return(self, order_id: int) -> Order:
        """Get details of an order, with item quantities updated by returns

        Args:
            order_id (int): id of order to get

        Returns:
            Order: details of the order
        """
        cur = self.conn.execute(
            """
SELECT id,
    customer_id,
    user_id,
    payment_type,
    order_reference,
    timestamp,
    EXISTS(
        SELECT 1
        FROM orders
        WHERE order_reference = o.id
    ) AS order_updated
FROM orders o
WHERE id = ?;
""",
            (order_id,),
        )
        cur2 = self.conn.execute(
            """
WITH RECURSIVE ord(id) AS (
    SELECT id
    FROM orders
    WHERE id = ?
    UNION ALL
    SELECT orders.id
    FROM orders,
        ord
    WHERE orders.order_reference = ord.id
)
SELECT order_items.item_id,
    SUM(quantity),
    name,
    price,
    gst,
    pst,
    category_id
FROM ord
    INNER JOIN order_items ON ord.id = order_items.order_id
    LEFT JOIN items ON order_items.item_id = items.id
GROUP BY order_items.item_id;
""",
            (order_id,),
        )
        order = Order.from_row(cur.fetchone())
        order.items = list(map(ItemQuantity.from_row, cur2.fetchall()))
        return order

    def create_customer(
        self,
        customer_name: str,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> int:
        """Create a new customer

        Args:
            customer_name (str): Name of the customer
            customer_phone (Optional[str], optional): customer's phone number Defaults to None.
            customer_email (Optional[str], optional): email of the customer. Defaults to None.

        Raises:
            RuntimeError: if db did not set last row id

        Returns:
            int: id of the new customer
        """
        cur = self.conn.execute(
            "INSERT INTO customers(customer_name, phone_number, email) VALUES(?, ?, ?);",
            (customer_name, customer_phone, customer_email),
        )
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def get_all_customers(self) -> list[Customer]:
        """Get all customers from the database

        Returns:
            list[Customer]: list of customers from the database
        """
        cur = self.conn.execute("SELECT * FROM customers;")
        return list(map(Customer.from_row, cur.fetchall()))
