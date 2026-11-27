"""Unit tests for the deterministic synthetic e-commerce source generator.

These tests do not require Airflow or PostgreSQL. They verify the source-data
contract and the deliberately injected data-quality cases.
"""
import random

import numpy as np

from src.generate_data import (
    generate_customers,
    generate_products,
    generate_orders,
    generate_order_items,
    introduce_data_quality_issues,
)


def _build_raw_frames():
    np.random.seed(42)
    random.seed(42)
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers)
    items = generate_order_items(orders, products)
    return customers, products, orders, items


def test_generator_creates_expected_source_shapes():
    customers, products, orders, items = _build_raw_frames()

    assert len(customers) == 2_000
    assert len(products) == 100
    assert len(orders) == 10_000
    assert 10_000 <= len(items) <= 50_000
    assert customers["customer_id"].is_unique
    assert products["product_id"].is_unique
    assert orders["order_id"].is_unique


def test_orders_never_precede_customer_signup():
    customers, _, orders, _ = _build_raw_frames()
    signup = customers.assign(signup_date=__import__("pandas").to_datetime(customers["signup_date"]))
    order_dates = orders.assign(order_date=__import__("pandas").to_datetime(orders["order_date"]))
    joined = order_dates.merge(signup[["customer_id", "signup_date"]], on="customer_id")

    assert (joined["order_date"] >= joined["signup_date"]).all()


def test_quality_injection_adds_documented_anomalies():
    customers, products, orders, items = _build_raw_frames()
    np.random.seed(42)

    dirty_customers, dirty_products, dirty_orders, dirty_items, stats = (
        introduce_data_quality_issues(customers, products, orders, items)
    )

    assert stats == {
        "duplicate_customers": 15,
        "missing_customer_cities": 15,
        "missing_product_prices": 2,
        "invalid_order_item_quantities": 150,
        "missing_payment_methods": 60,
        "orphan_order_customer_ids": 50,
        "orphan_order_item_product_ids": 120,
    }
    assert len(dirty_customers) == 2_015
    assert dirty_customers["customer_id"].duplicated().sum() == 15
    assert dirty_customers["city"].isna().sum() == 15
    assert dirty_products["price"].isna().sum() == 2
    assert (dirty_items["quantity"] <= 0).sum() == 150
    assert dirty_orders["payment_method"].isna().sum() == 60
    assert (dirty_orders["customer_id"] == 99_999).sum() == 50
    assert (dirty_items["product_id"] == 9_999).sum() == 120
