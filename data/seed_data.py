import random
from datetime import date, timedelta
from sqlalchemy import create_engine, text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)

REGIONS = ["Mumbai", "Pune", "Nashik", "Nagpur", "Aurangabad"]
DISTRIBUTORS = [f"Distributor_{i}" for i in range(1, 21)]
SKUS = ["Gold Milk 1L", "Cow Ghee 500g", "Paneer 200g", "Curd 400g", "Butter 100g",
        "Lassi 200ml", "Cheese Slice 200g", "Whey Protein 1kg", "Flavoured Milk 200ml", "Buttermilk 500ml"]
CATEGORIES = {
    "Gold Milk 1L": "Milk", "Cow Ghee 500g": "Ghee", "Paneer 200g": "Paneer",
    "Curd 400g": "Curd", "Butter 100g": "Butter", "Lassi 200ml": "Beverages",
    "Cheese Slice 200g": "Cheese", "Whey Protein 1kg": "Nutrition",
    "Flavoured Milk 200ml": "Beverages", "Buttermilk 500ml": "Beverages"
}
MRP = {
    "Gold Milk 1L": 62, "Cow Ghee 500g": 320, "Paneer 200g": 90,
    "Curd 400g": 48, "Butter 100g": 55, "Lassi 200ml": 30,
    "Cheese Slice 200g": 120, "Whey Protein 1kg": 1800,
    "Flavoured Milk 200ml": 25, "Buttermilk 500ml": 35
}

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS distributors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    distributor_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    mrp DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    distributor_id INT NOT NULL,
    product_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (distributor_id) REFERENCES distributors(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


def seed():
    with engine.begin() as conn:
        for stmt in CREATE_TABLES.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))

        # Seed distributors
        conn.execute(text("DELETE FROM sales"))
        conn.execute(text("DELETE FROM products"))
        conn.execute(text("DELETE FROM distributors"))

        for i, name in enumerate(DISTRIBUTORS, 1):
            region = random.choice(REGIONS)
            conn.execute(text(
                "INSERT INTO distributors (id, distributor_name, region, city) VALUES (:id, :name, :region, :city)"
            ), {"id": i, "name": name, "region": region, "city": region})

        # Seed products
        for i, sku in enumerate(SKUS, 1):
            conn.execute(text(
                "INSERT INTO products (id, sku_name, category, mrp) VALUES (:id, :sku, :cat, :mrp)"
            ), {"id": i, "sku": sku, "cat": CATEGORIES[sku], "mrp": MRP[sku]})

        # Seed sales (2 years of data)
        start_date = date(2023, 1, 1)
        records = []
        for _ in range(20000):
            dist_id = random.randint(1, 20)
            prod_id = random.randint(1, 10)
            sku = SKUS[prod_id - 1]
            qty = random.randint(1, 200)
            sale_date = start_date + timedelta(days=random.randint(0, 730))
            revenue = round(qty * MRP[sku] * random.uniform(0.8, 0.95), 2)
            records.append({"dist_id": dist_id, "prod_id": prod_id, "date": sale_date, "qty": qty, "rev": revenue})

        conn.execute(
            text("INSERT INTO sales (distributor_id, product_id, sale_date, quantity, revenue) VALUES (:dist_id, :prod_id, :date, :qty, :rev)"),
            records
        )

    print(f"Seeded: {len(DISTRIBUTORS)} distributors, {len(SKUS)} products, 20000 sales records.")


if __name__ == "__main__":
    seed()