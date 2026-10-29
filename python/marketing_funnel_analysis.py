
import argparse
from pathlib import Path

import pandas as pd


def analyze(input_file):
    df = pd.read_excel(input_file, sheet_name="Cleaned_Data")

    df["event_time"] = pd.to_datetime(
        df["event_time"], errors="coerce", utc=True
    )
    df["event_type"] = (
        df["event_type"].astype("string").str.strip().str.lower()
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    for column in ["category_code", "brand", "user_session"]:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    total_events = len(df)
    total_users = df["user_id"].nunique()
    total_sessions = df["user_session"].nunique()
    total_products = df["product_id"].nunique()

    valid_times = df["event_time"].dropna()

    event_counts = df["event_type"].value_counts(dropna=False)

    sessions = (
        df.dropna(subset=["user_session"])
        .groupby("user_session")
        .agg(
            event_count=("event_type", "size"),
            view_events=("event_type", lambda x: (x == "view").sum()),
            cart_events=("event_type", lambda x: (x == "cart").sum()),
            purchase_events=(
                "event_type", lambda x: (x == "purchase").sum()
            ),
            remove_from_cart_events=(
                "event_type",
                lambda x: (x == "remove_from_cart").sum()
            ),
        )
        .reset_index()
    )

    for event in ["view", "cart", "purchase", "remove_from_cart"]:
        sessions[f"has_{event}"] = sessions[f"{event}_events"] > 0

    view_sessions = int(sessions["has_view"].sum())
    cart_sessions = int(sessions["has_cart"].sum())
    purchase_sessions = int(sessions["has_purchase"].sum())

    view_cart = int(
        (sessions["has_view"] & sessions["has_cart"]).sum()
    )
    view_purchase = int(
        (sessions["has_view"] & sessions["has_purchase"]).sum()
    )
    all_three = int(
        (
            sessions["has_view"]
            & sessions["has_cart"]
            & sessions["has_purchase"]
        ).sum()
    )

    lines = []

    def heading(title):
        lines.extend(["", "=" * 65, title, "=" * 65])

    def item(label, value):
        lines.append(f"{label}: {value}")

    heading("MARKETING FUNNEL AND CONVERSION PERFORMANCE ANALYSIS")

    item("Dataset", str(input_file))
    item("Total event records", f"{total_events:,}")
    item("Unique users", f"{total_users:,}")
    item("Unique sessions", f"{total_sessions:,}")
    item("Unique products", f"{total_products:,}")

    if len(valid_times):
        item("First event (UTC)", str(valid_times.min()))
        item("Last event (UTC)", str(valid_times.max()))

    heading("1. EVENT ANALYSIS")

    for event, count in event_counts.items():
        percentage = count / total_events * 100 if total_events else 0
        item(
            str(event),
            f"{count:,} events ({percentage:.2f}%)"
        )

    heading("2. SESSION-LEVEL FUNNEL")

    item("Sessions containing views", view_sessions)
    item("Sessions containing cart events", cart_sessions)
    item("Sessions containing purchases", purchase_sessions)
    item("Sessions containing both views and carts", view_cart)
    item("Sessions containing both views and purchases", view_purchase)
    item("Sessions containing views, carts and purchases", all_three)

    if view_sessions:
        item(
            "Cart sessions / view sessions",
            f"{cart_sessions / view_sessions * 100:.2f}%"
        )
        item(
            "Purchase sessions / view sessions",
            f"{purchase_sessions / view_sessions * 100:.2f}%"
        )

    lines.append(
        "Interpretation: These percentages are descriptive ratios. "
        "They are not validated sequential conversion rates because "
        "session-level event presence alone does not prove event order."
    )

    heading("3. PRICE ANALYSIS")

    item("Valid numeric prices", int(df["price"].notna().sum()))

    if df["price"].notna().any():
        item("Average price", f"{df['price'].mean():.2f}")
        item("Median price", f"{df['price'].median():.2f}")
        item("Minimum price", f"{df['price'].min():.2f}")
        item("Maximum price", f"{df['price'].max():.2f}")

    heading("4. CATEGORY ANALYSIS")

    category_report = (
        df.groupby("category_code", dropna=False)
        .agg(
            events=("event_type", "size"),
            unique_sessions=("user_session", "nunique"),
            unique_users=("user_id", "nunique"),
            average_price=("price", "mean"),
        )
        .sort_values("events", ascending=False)
    )

    lines.append(
        category_report.head(20).to_string(
            na_rep="Missing", float_format=lambda x: f"{x:.2f}"
        )
    )

    heading("5. BRAND ANALYSIS")

    brand_report = (
        df.groupby("brand", dropna=False)
        .agg(
            events=("event_type", "size"),
            unique_sessions=("user_session", "nunique"),
            unique_users=("user_id", "nunique"),
            average_price=("price", "mean"),
        )
        .sort_values("events", ascending=False)
    )

    lines.append(
        brand_report.head(20).to_string(
            na_rep="Missing", float_format=lambda x: f"{x:.2f}"
        )
    )

    heading("6. DAILY EVENT TREND")

    daily = (
        df.dropna(subset=["event_time"])
        .assign(date_utc=lambda x: x["event_time"].dt.strftime("%Y-%m-%d"))
        .groupby(["date_utc", "event_type"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    lines.append(daily.to_string())

    heading("7. DATA QUALITY CHECKS")

    quality = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing Percentage": [
            round(df[c].isna().mean() * 100, 2) for c in df.columns
        ],
        "Distinct Values": [
            int(df[c].nunique(dropna=True)) for c in df.columns
        ],
    })

    lines.append(quality.to_string(index=False))

    item("Exact duplicate rows", int(df.duplicated().sum()))
    item("Missing timestamps", int(df["event_time"].isna().sum()))
    item("Missing event types", int(df["event_type"].isna().sum()))
    item("Missing prices", int(df["price"].isna().sum()))
    item(
        "Non-positive prices",
        int((df["price"].notna() & (df["price"] <= 0)).sum())
    )
    item("Missing user IDs", int(df["user_id"].isna().sum()))
    item("Missing session IDs", int(df["user_session"].isna().sum()))

    heading("8. FINDINGS AND LIMITATIONS")

    lines.append(
        "The event counts, session counts, prices, categories and brands "
        "above are calculated directly from the supplied dataset."
    )
    lines.append(
        "This analysis covers only the records in the cleaned sample. "
        "It must not be presented as analysis of the complete October "
        "2019 dataset."
    )
    lines.append(
        "Missing category and brand values have not been guessed "
        "or replaced."
    )
    lines.append(
        "Event presence within a session does not establish a customer's "
        "exact journey or the order of conversion steps."
    )
    lines.append(
        "The observed patterns should not be generalized to all "
        "customers or the entire month without a larger dataset."
    )

    report_text = "\n".join(lines)
    print(report_text)
    print(f"Analysis completed. Records analyzed: {total_events:,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze e-commerce marketing funnel performance."
    )
    parser.add_argument(
        "--input",
        default=(
            Path(__file__).resolve().parent.parent
            / "data"
            / "cleaned"
            / "Task_3_Marketing_Funnel_Cleaned.xlsx"
        )
    )
    args = parser.parse_args()

    analyze(args.input)
