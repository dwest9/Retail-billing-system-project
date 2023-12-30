"""Handles operations centered around customers"""
from dataclasses import dataclass
import sqlite3
from typing import Optional


@dataclass
class CustomerOrder:
    """Represents an order with customer information"""

    order_id: int
    customer_name: str
    phone_number: Optional[str]
    email: Optional[str]
    payment_type: str
    cashier: str
    timestamp: str
    subtotal: float
    gst_total: float
    pst_total: float


class CustomerSystem:
    """Customer System class"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_customer_order_by_id(self, order_id: int) -> Optional[CustomerOrder]:
        """Gets a customer order by id

        Args:
            order_id (int): id of order to get

        Returns:
            Optional[CustomerOrder]: CustomerOrder of the order id or None
        """
        cur = self.conn.execute(
            """
SELECT
    order_id,
    customer_name,
    phone_number,
    email,
    payment_type,
    cashier,
    timestamp,
    subtotal,
    gst_total,
    pst_total
FROM
    customer_orders
WHERE
    order_id = ?;
""",
            (order_id,),
        )
        order = cur.fetchone()
        if order is None:
            return None
        return CustomerOrder(*order)

    def search_orders_by_name(self, customer_name: str) -> list[CustomerOrder]:
        """Search customer orders by customer name

        Args:
            customer_name (str): name or partial name

        Returns:
            list[Customer]: list of customer orders matching a name
        """
        cur = self.conn.execute(
            """
SELECT
    order_id,
    customer_name,
    phone_number,
    email,
    payment_type,
    cashier,
    timestamp,
    subtotal,
    gst_total,
    pst_total
FROM
    customer_orders
WHERE
    customer_name LIKE '%' || ? || '%';
""",
            (customer_name,),
        )
        return list(map(lambda row: CustomerOrder(*row), cur.fetchall()))

    def search_orders_by_email(self, customer_email: str) -> list[CustomerOrder]:
        """Search customer orders by customer email

        Args:
            customer_email (str): email or partial email

        Returns:
            list[Customer]: list of customer orders matching an email
        """
        cur = self.conn.execute(
            """
SELECT
    order_id,
    customer_name,
    phone_number,
    email,
    payment_type,
    cashier,
    timestamp,
    subtotal,
    gst_total,
    pst_total
FROM
    customer_orders
WHERE
    email LIKE '%' || ? || '%';
""",
            (customer_email,),
        )
        return list(map(lambda row: CustomerOrder(*row), cur.fetchall()))

    def search_orders_by_phone_number(self, phone_number: str) -> list[CustomerOrder]:
        """Search customer orders by customer phone number

        Args:
            phone_number (str): phone number or partial phone number

        Returns:
            list[Customer]: list of customer orders matching a phone number
        """
        cur = self.conn.execute(
            """
SELECT
    order_id,
    customer_name,
    phone_number,
    email,
    payment_type,
    cashier,
    timestamp,
    subtotal,
    gst_total,
    pst_total
FROM
    customer_orders
WHERE
    phone_number LIKE '%' || ? || '%';
""",
            (phone_number,),
        )
        return list(map(lambda row: CustomerOrder(*row), cur.fetchall()))
