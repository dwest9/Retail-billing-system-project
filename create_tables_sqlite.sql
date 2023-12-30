CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL COLLATE NOCASE,
    user_hash TEXT NOT NULL,
    is_manager BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    gst BOOLEAN,
    pst BOOLEAN,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL COLLATE NOCASE,
    phone_number TEXT,
    email TEXT COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS payment_types(
    id INTEGER PRIMARY KEY,
    payment_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    user_id INTEGER NOT NULL,
    payment_type INTEGER,
    order_reference INTEGER,
    timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (payment_type) REFERENCES payment_types (id),
    FOREIGN KEY (order_reference) REFERENCES orders (id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE VIEW order_summary AS
SELECT
    orders.id,
    orders.customer_id,
    orders.user_id,
    orders.payment_type,
    orders.timestamp,
    SUM(order_items.quantity) AS num_items,
    SUM(order_items.quantity * items.price) AS subtotal,
    SUM(
        order_items.quantity * items.price * items.gst * 0.05
    ) AS gst_total,
    SUM(
        order_items.quantity * items.price * items.pst * 0.06
    ) AS pst_total
FROM
    orders
    LEFT JOIN order_items ON orders.id = order_items.order_id
    LEFT JOIN items ON order_items.item_id = items.id
GROUP BY
    order_items.order_id;

CREATE VIEW customer_orders AS
SELECT
    order_summary.id AS order_id,
    customer_name,
    phone_number,
    email,
    payment_types.payment_type,
    users.username as cashier,
    TIMESTAMP,
    subtotal,
    gst_total,
    pst_total
FROM
    customers
    LEFT JOIN order_summary ON customers.id = order_summary.customer_id
    LEFT JOIN payment_types ON order_summary.payment_type = payment_types.id
    LEFT JOIN users ON order_summary.user_id = users.id;

CREATE VIEW hourly_sales AS
SELECT
    strftime('%Y-%m-%d', timestamp) as date,
    strftime('%H:00:00', TIMESTAMP) AS hour,
    COUNT(*) as num_orders,
    SUM(num_items) as num_items,
    SUM(subtotal) as subtotal,
    SUM(gst_total) as gst_total,
    SUM(pst_total) as pst_total
FROM
    order_summary
GROUP BY
    strftime('%Y-%m-%d %H', timestamp);

CREATE VIEW daily_sales AS
SELECT
    DATE(TIMESTAMP) AS day,
    COUNT(*) AS num_orders,
    SUM(num_items) AS num_items,
    SUM(subtotal) AS subtotal,
    SUM(gst_total) as gst_total,
    SUM(pst_total) as pst_total
FROM
    order_summary
GROUP BY
    DATE(timestamp);

CREATE TABLE IF NOT EXISTS inventory_counts (
    id INTEGER PRIMARY KEY,
    ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_count_items (
    count_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(count_id, item_id),
    FOREIGN KEY (count_id) REFERENCES inventory_counts(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS stock_adjustments (
    id INTEGER PRIMARY KEY,
    reason TEXT NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_adjustment_items (
    adjustment_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(adjustment_id, item_id),
    FOREIGN KEY (adjustment_id) REFERENCES stock_adjustments(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE INDEX order_timestamp ON orders(TIMESTAMP);

CREATE INDEX order_day ON orders(DATE(TIMESTAMP));

CREATE INDEX order_month ON orders(STRFTIME('%Y-%m', TIMESTAMP));

CREATE INDEX inventory_count_timestamp ON inventory_counts(ts);

CREATE INDEX stock_adjustment_timestamp ON stock_adjustments(ts);

CREATE VIEW inventory_count_windows AS
SELECT
    id,
    ts AS current_ts,
    COALESCE(
        FIRST_VALUE(ts) OVER (
            ORDER BY
                ts ROWS BETWEEN 1 PRECEDING
                AND 1 PRECEDING
        ),
        "0000-00-00 00:00:00"
    ) AS previous_ts,
    FIRST_VALUE(id) OVER (
        ORDER BY
            ts ROWS BETWEEN 1 PRECEDING
            AND 1 PRECEDING
    ) as previous_id
FROM
    inventory_counts;