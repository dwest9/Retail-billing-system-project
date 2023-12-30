"""Main Report Module"""
from dataclasses import dataclass
from datetime import date
import sqlite3
from typing import Any


@dataclass
class HourlySales:
    """Represents a record of sales over an hour"""

    hour: str
    num_orders: int
    num_items: int
    subtotal: float
    gst_total: float
    pst_total: float

    @staticmethod
    def from_row(row: Any) -> "HourlySales":
        """Converts a sqlite row to an HourlySales record

        Args:
            row (Any): Row from the database

        Returns:
            HourlySales: an HourlySales record
        """
        hour, num_orders, num_items, subtotal, gst_total, pst_total = row
        return HourlySales(hour, num_orders, num_items, subtotal, gst_total, pst_total)


@dataclass
class DailySales:
    """Represents a record of sales over a day"""

    day: str
    num_orders: int
    num_items: int
    subtotal: float
    gst_total: float
    pst_total: float

    @staticmethod
    def from_row(row: Any) -> "DailySales":
        """Converts a sqlite row to a DailySales record

        Args:
            row (Any): Row from the database

        Returns:
            DailySales: a DailySales record
        """
        day, num_orders, num_items, subtotal, gst_total, pst_total = row
        return DailySales(day, num_orders, num_items, subtotal, gst_total, pst_total)


@dataclass
class CashierRow:
    """Represents a record of sales grouped by user and payment type"""

    user_id: int
    username: str
    payment_type_id: int
    payment_type: str
    num_orders: int
    num_items: int
    subtotal: float
    gst_total: float
    pst_total: float

    @staticmethod
    def from_row(row: Any) -> "CashierRow":
        """Converts a sqlite row to a CashierRow record

        Args:
            row (Any): Row from the database

        Returns:
            CashierRow: a CashierRow record
        """
        (
            user_id,
            username,
            payment_type_id,
            payment_type,
            num_orders,
            num_items,
            subtotal,
            gst_total,
            pst_total,
        ) = row
        return CashierRow(
            user_id,
            username,
            payment_type_id,
            payment_type,
            num_orders,
            num_items,
            subtotal,
            gst_total,
            pst_total,
        )


@dataclass
class ItemSales:
    """Represents a record of sales grouped by item"""

    item_id: int
    item_name: str
    category_id: int
    category_name: str
    quantity: int
    subtotal: float
    gst_total: float
    pst_total: float

    @staticmethod
    def from_row(row: Any) -> "ItemSales":
        """Converts a sqlite row to an ItemSales record

        Args:
            row (Any): Row for the database

        Returns:
            ItemSales: a ItemRow record
        """
        (
            item_id,
            item_name,
            category_id,
            category_name,
            quantity,
            subtotal,
            gst_total,
            pst_total,
        ) = row
        return ItemSales(
            item_id,
            item_name,
            category_id,
            category_name,
            quantity,
            subtotal,
            gst_total,
            pst_total,
        )


class ReportSystem:
    """Report System Class"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_hourly_sales_for_date(self, day: date) -> list[HourlySales]:
        """Get a report of sales grouped by hour for a given day

        Args:
            day (date): date to generate report for

        Returns:
            list[HourlySales]: Records of sales by hour
        """
        cur = self.conn.execute(
            """
SELECT
    hour,
    num_orders,
    num_items,
    subtotal,
    gst_total,
    pst_total
FROM
    hourly_sales
WHERE
    date = ?;
""",
            (day,),
        )
        return list(map(HourlySales.from_row, cur.fetchall()))

    def get_hourly_sales_for_date_range(
        self, start: date, end: date
    ) -> list[HourlySales]:
        """Get a report of sales grouped by hour for a given date range

        Args:
            start (date): start of date range(inclusive)
            end (date): end of date range(inclusive)

        Returns:
            list[HourlySales]: Records of sales by hour
        """
        cur = self.conn.execute(
            """
SELECT
    hour,
    SUM(num_orders),
    SUM(num_items),
    SUM(subtotal),
    SUM(gst_total),
    SUM(pst_total)
FROM
    hourly_sales
WHERE
    date BETWEEN ? AND ?
GROUP BY
    hour;
""",
            (start, end),
        )
        return list(map(HourlySales.from_row, cur.fetchall()))

    def get_daily_sales_for_date_range(
        self, start: date, end: date
    ) -> list[DailySales]:
        """Get a report of sales grouped by day for a given date range

        Args:
            start (date): start of date range(inclusive)
            end (date): end of date range(inclusive)

        Returns:
            list[DailySales]: records of sales by day
        """

        cur = self.conn.execute(
            """
SELECT
    day,
    num_orders,
    num_items,
    subtotal,
    gst_total,
    pst_total
FROM
    daily_sales
WHERE
    day BETWEEN ? AND ?;
""",
            (start, end),
        )
        return list(map(DailySales.from_row, cur.fetchall()))

    def get_cashier_sales_for_date(self, day: date) -> list[CashierRow]:
        """Get a report of sales grouped by cashier and payment_type

        Args:
            day (date): date to generate report for

        Returns:
            list[CashierRow]: records of sales for each cashier and payment_type
        """
        cur = self.conn.execute(
            """
SELECT
    user_id,
    username,
    payment_types.id AS payment_type_id,
    payment_types.payment_type AS payment_type,
    COUNT(*) AS num_orders,
    SUM(num_items) AS num_items,
    SUM(subtotal) AS subtotal,
    SUM(gst_total) AS gst_total,
    SUM(pst_total) AS pst_total
FROM
    order_summary
    LEFT JOIN users ON user_id = users.id
    LEFT JOIN payment_types ON order_summary.payment_type = payment_types.id
WHERE
    DATE(TIMESTAMP) = ?
GROUP BY
    user_id,
    order_summary.payment_type;
""",
            (day,),
        )
        return list(map(CashierRow.from_row, cur.fetchall()))

    def get_cashier_sales_for_date_range(
        self, start: date, end: date
    ) -> list[CashierRow]:
        """Get a report of sales grouped by cashier and payment_type

        Args:
            start (date): start of date range(inclusive)
            end (date): end of date range(inclusive)

        Returns:
            list[CashierRow]: records of sales for each cashier and payment type
        """
        cur = self.conn.execute(
            """
SELECT
    user_id,
    username,
    payment_types.id AS payment_type_id,
    payment_types.payment_type AS payment_type,
    COUNT(*) AS num_orders,
    SUM(num_items) AS num_items,
    SUM(subtotal) AS subtotal,
    SUM(gst_total) AS gst_total,
    SUM(pst_total) AS pst_total
FROM
    order_summary
    LEFT JOIN users ON user_id = users.id
    LEFT JOIN payment_types ON order_summary.payment_type = payment_types.id
WHERE
    DATE(TIMESTAMP) BETWEEN ? AND ?
GROUP BY
    user_id,
    order_summary.payment_type;
""",
            (start, end),
        )
        return list(map(CashierRow.from_row, cur.fetchall()))

    def get_item_sales_for_date(self, day: date) -> list[ItemSales]:
        """Get a report of sales broken down by item for a given day

        Args:
            day (date): date to generate report for

        Returns:
            list[ItemSales]: records of sales by item
        """
        cur = self.conn.execute(
            """
SELECT
    item_id,
    name AS item_name,
    category_id,
    category AS category_name,
    SUM(quantity) AS quantity,
    SUM(quantity) * price AS subtotal,
    SUM(quantity) * price * gst * 0.05 AS gst_total,
    SUM(quantity) * price * pst * 0.06 AS pst_total
FROM
    orders
    LEFT JOIN order_items ON orders.id = order_items.order_id
    LEFT JOIN items ON order_items.item_id = items.id
    LEFT JOIN categories ON items.category_id = categories.id
WHERE
    DATE(TIMESTAMP) = ?
GROUP BY
    order_items.item_id;
""",
            (day,),
        )
        return list(map(ItemSales.from_row, cur.fetchall()))

    def get_item_sales_for_date_range(self, start: date, end: date) -> list[ItemSales]:
        """Generates a report of sales broken down by item

        Args:
            start (date): start of date range(inclusive)
            end (date): end of date range(inclusive)

        Returns:
            list[ItemSales]: records of sales by item
        """
        cur = self.conn.execute(
            """
SELECT
    item_id,
    name AS item_name,
    category_id,
    category AS category_name,
    SUM(quantity) AS quantity,
    SUM(quantity) * price AS subtotal,
    SUM(quantity) * price * gst * 0.05 AS gst_total,
    SUM(quantity) * price * pst * 0.06 AS pst_total
FROM
    orders
    LEFT JOIN order_items ON orders.id = order_items.order_id
    LEFT JOIN items ON order_items.item_id = items.id
    LEFT JOIN categories ON items.category_id = categories.id
WHERE
    DATE(TIMESTAMP) BETWEEN ? AND ?
GROUP BY
    order_items.item_id;
""",
            (start, end),
        )
        return list(map(ItemSales.from_row, cur.fetchall()))
