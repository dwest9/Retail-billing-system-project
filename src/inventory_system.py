"""Contains functionality for managing inventory"""
from dataclasses import dataclass
import datetime
import sqlite3
from typing import Any


@dataclass
class InventoryCount:
    """Represents a inventory count"""

    count_id: int
    timestamp: str

    @staticmethod
    def from_row(row: Any) -> "InventoryCount":
        """Converts a sqlite row to an Item

        Args:
            row (Any): Row from the database

        Returns:
            Item: an Item from the database
        """
        count_id, timestamp = row
        return InventoryCount(count_id, timestamp)


@dataclass
class CountDetailsRecord:
    """Represents an record in an count details report"""

    category_id: int
    category_name: str
    item_id: int
    item_name: str
    previous_quantity: int
    quantity_sold: int
    adjustment_quantity: int
    actual_quantity: int

    @staticmethod
    def from_row(row: Any) -> "CountDetailsRecord":
        """Converts a sqlite row to an Item

        Args:
            row (Any): Row from the database

        Returns:
            Item: an Item from the database
        """
        (
            category_id,
            category_name,
            item_id,
            item_name,
            previous_quantity,
            quantity_sold,
            adjustment_quantity,
            actual_quantity,
        ) = row
        return CountDetailsRecord(
            category_id,
            category_name,
            item_id,
            item_name,
            previous_quantity,
            quantity_sold,
            adjustment_quantity,
            actual_quantity,
        )


@dataclass
class InventoryReportRecord:
    """Represents an record in an inventory report"""

    category_id: int
    category_name: str
    item_id: int
    name: str
    date: str
    day_quantity: int
    month_quantity: int
    count_quantity: int
    adjustment_quantity: int
    quantity_sold: int

    @staticmethod
    def from_row(row: Any) -> "InventoryReportRecord":
        """Converts a sqlite row to an Item

        Args:
            row (Any): Row from the database

        Returns:
            Item: an Item from the database
        """
        (
            category_id,
            category_name,
            item_id,
            name,
            date,
            day_quantity,
            month_quantity,
            count_quantity,
            adjustment_quantity,
            quantity_sold,
        ) = row
        return InventoryReportRecord(
            category_id,
            category_name,
            item_id,
            name,
            date,
            day_quantity,
            month_quantity,
            count_quantity,
            adjustment_quantity,
            quantity_sold,
        )


class InventorySystem:
    """Inventory System Class"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_count(self) -> int:
        """Creates a new count using the current time

        Raises:
            RuntimeError: if the database failed to set lastrowid

        Returns:
            int: id of the new inventory count
        """
        cur = self.conn.execute("INSERT INTO inventory_counts DEFAULT VALUES;")
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def set_item_in_count(self, count_id: int, item_id: int, quantity: int):
        """Sets the quantity of an item for a stock adjustment

        Args:
            count_id (int): id of the inventory count
            item_id (int): id of the item
            quantity (int): quantity of the item
        """
        self.conn.execute(
            "INSERT INTO inventory_count_items (count_id, item_id, quantity) VALUES (?, ?, ?);",
            (count_id, item_id, quantity),
        )
        self.conn.commit()

    def create_adjustment(self, reason: str) -> int:
        """Creates a new stock adjustment

        Args:
            reason (str): reason for stock adjustment

        Raises:
            RuntimeError: if the database failed to set lastrowid

        Returns:
            int: id of the new stock adjustment
        """
        cur = self.conn.execute(
            "INSERT INTO stock_adjustments (reason) VALUES (?);", (reason,)
        )
        self.conn.commit()
        if cur.lastrowid is None:
            raise RuntimeError
        return cur.lastrowid

    def set_item_in_adjustment(self, adjustment_id: int, item_id: int, quantity: int):
        """Sets the quantity of an item for a stock adjustment

        Args:
            adjustment_id (int): id of the stock adjustment
            item_id (int): id of the item
            quantity (int): quantity to set
        """
        self.conn.execute(
            "INSERT INTO stock_adjustment_items (adjustment_id, item_id, quantity) VALUES (?,?,?);",
            (adjustment_id, item_id, quantity),
        )
        self.conn.commit()

    def list_inventory_counts(self) -> list[InventoryCount]:
        """Lists inventory counts in the database

        Returns:
            list[InventoryCount] inventory counts from the database
        """
        cur = self.conn.execute("SELECT id, ts FROM inventory_counts;")
        return list(map(InventoryCount.from_row, cur.fetchall()))

    def get_count_details(self, count_id: int) -> list[CountDetailsRecord]:
        """Gets details about a count

        Args:
            count_id (int): id of count

        Returns:
            list[CountDetailsRecord]: count details for each item
        """
        cur = self.conn.execute(
            """
SELECT
    categories.id AS category_id,
    categories.category AS category_name,
    items.id AS item_id,
    items.name AS item_name,
    COALESCE(previous_count, 0) AS previous_count,
    COALESCE(quantity_sold, 0) AS quantity_sold,
    COALESCE(adjustment_quantity, 0) AS adjustment_quantity,
    actual_quantity
FROM
    items
    LEFT JOIN categories ON items.category_id = categories.id
    LEFT JOIN (
        SELECT
            item_id,
            quantity AS previous_count
        FROM
            inventory_counts
            LEFT JOIN inventory_count_items ON inventory_counts.id = inventory_count_items.count_id
        WHERE
            id = (
                SELECT
                    previous_id
                FROM
                    inventory_count_windows
                WHERE
                    id = ?1
            )
    ) prev ON items.id = prev.item_id
    LEFT JOIN (
        SELECT
            item_id,
            SUM(quantity) AS quantity_sold
        FROM
            orders
            LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE
            TIMESTAMP BETWEEN (
                SELECT
                    previous_ts
                FROM
                    inventory_count_windows
                WHERE
                    id = ?1
            )
            AND (
                SELECT
                    current_ts
                FROM
                    inventory_count_windows
                WHERE
                    id = ?1
            )
        GROUP BY
            item_id
    ) sales ON items.id = sales.item_id
    LEFT JOIN (
        SELECT
            item_id,
            SUM(quantity) AS adjustment_quantity
        FROM
            stock_adjustments
            LEFT JOIN stock_adjustment_items ON stock_adjustments.id = stock_adjustment_items.adjustment_id
        WHERE
            ts BETWEEN (
                SELECT
                    previous_ts
                FROM
                    inventory_count_windows
                WHERE
                    id = ?1
            )
            AND (
                SELECT
                    current_ts
                FROM
                    inventory_count_windows
                WHERE
                    id = ?1
            )
        GROUP BY
            item_id
    ) adjustments ON items.id = adjustments.item_id
    LEFT JOIN (
        SELECT
            item_id,
            quantity AS actual_quantity
        FROM
            inventory_counts
            LEFT JOIN inventory_count_items ON inventory_counts.id = inventory_count_items.count_id
        WHERE
            id = ?1
    ) cur ON items.id = cur.item_id;
""",
            (count_id,),
        )
        return list(map(CountDetailsRecord.from_row, cur.fetchall()))

    def get_inventory_details(self) -> list[InventoryReportRecord]:
        """Gets a report of the current inventory information

        Returns:
            list[InventoryReportRecord]: inventory information for each item
        """
        today = datetime.date.today()
        cur = self.conn.execute(
            """
SELECT
    category_id,
    categories.category AS category_name,
    items.id AS item_id,
    name AS item_name,
    COALESCE(date, ?1) AS day,
    COALESCE(day_quantity, 0) AS day_quantity,
    COALESCE(month_quantity, 0) AS month_quantity,
    COALESCE(count_quantity, 0) AS count_quantity,
    COALESCE(adjustment_quantity, 0) AS adjustment_quantity,
    COALESCE(quantity_sold, 0) AS quantity_sold
FROM
    items
    LEFT JOIN categories ON items.category_id = categories.id
    LEFT JOIN (
        SELECT
            DATE(TIMESTAMP) AS DATE,
            item_id,
            SUM(quantity) AS day_quantity
        FROM
            orders
            LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE
            DATE = ?1
        GROUP BY
            DATE(TIMESTAMP),
            item_id
    ) day ON items.id = day.item_id
    LEFT JOIN (
        SELECT
            STRFTIME('%Y-%m', timestamp) AS MONTH,
            item_id,
            SUM(quantity) AS month_quantity
        FROM
            orders
            LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE
            MONTH = STRFTIME('%Y-%m', ?1)
        GROUP BY
            STRFTIME('%Y-%m', timestamp),
            item_id
    ) month ON items.id = month.item_id
    LEFT JOIN (
        SELECT
            item_id,
            quantity AS count_quantity
        FROM
            inventory_count_items
        WHERE
            count_id = (
                SELECT
                    id
                FROM
                    inventory_counts
                ORDER BY
                    ts DESC
                LIMIT
                    1
            )
    ) count ON items.id = count.item_id
    LEFT JOIN (
        SELECT
            item_id,
            SUM(quantity) AS adjustment_quantity
        FROM
            stock_adjustments
            LEFT JOIN stock_adjustment_items ON stock_adjustments.id = stock_adjustment_items.adjustment_id
        WHERE
            ts > (
                SELECT
                    ts
                FROM
                    inventory_counts
                ORDER BY
                    ts DESC
                LIMIT
                    1
            )
        GROUP BY
            item_id
    ) adjustment ON items.id = adjustment.item_id
    LEFT JOIN (
        SELECT
            item_id,
            SUM(quantity) AS quantity_sold
        FROM
            orders
            LEFT JOIN order_items ON orders.id = order_items.order_id
        WHERE
            TIMESTAMP > (
                SELECT
                    ts
                FROM
                    inventory_counts
                ORDER BY
                    ts DESC
                LIMIT
                    1
            )
        GROUP BY
            item_id
    ) sold ON items.id = sold.item_id
GROUP BY
    items.id;
""",
            (today,),
        )
        return list(map(InventoryReportRecord.from_row, cur.fetchall()))
