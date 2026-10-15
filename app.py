import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Supply Chain Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Supply Chain Analytics Dashboard")
st.subheader(
    "Customer, Product, and Profitability Performance Analysis"
)

st.markdown("""
This dashboard analyzes supply chain sales, profit, customer segments,
product categories, regional performance, and discounts.
""")

# Upload dataset
uploaded_file = st.sidebar.file_uploader(
    "Upload APL_Logistics.csv",
    type=["csv"]
)

if uploaded_file is not None:

    # Load data
    df = pd.read_csv(uploaded_file, encoding="latin1")

    st.success("Dataset uploaded successfully!")

    # Required columns
    required_columns = [
        "Sales",
        "Order Item Total",
        "Order Profit Per Order",
        "Order Item Discount Rate"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        st.error(f"Missing columns: {missing_columns}")
        st.stop()

    # Convert numeric fields
    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sidebar filters
    st.sidebar.header("Filters")

    filtered_df = df.copy()

    if "Customer Segment" in filtered_df.columns:
        segments = sorted(
            filtered_df["Customer Segment"]
            .dropna().unique().tolist()
        )

        selected_segments = st.sidebar.multiselect(
            "Customer Segment",
            segments,
            default=segments
        )

        filtered_df = filtered_df[
            filtered_df["Customer Segment"].isin(selected_segments)
        ]

    if "Market" in filtered_df.columns:
        markets = sorted(
            filtered_df["Market"].dropna().unique().tolist()
        )

        selected_markets = st.sidebar.multiselect(
            "Market",
            markets,
            default=markets
        )

        filtered_df = filtered_df[
            filtered_df["Market"].isin(selected_markets)
        ]

    # Calculate KPIs
    gross_sales = filtered_df["Sales"].sum()
    net_sales = filtered_df["Order Item Total"].sum()
    total_profit = filtered_df["Order Profit Per Order"].sum()

    profit_margin = (
        total_profit / net_sales * 100
        if net_sales != 0 else 0
    )

    average_discount = (
        filtered_df["Order Item Discount Rate"].mean() * 100
    )

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Gross Sales",
        f"{gross_sales:,.2f}"
    )

    col2.metric(
        "Net Sales",
        f"{net_sales:,.2f}"
    )

    col3.metric(
        "Recorded Profit",
        f"{total_profit:,.2f}"
    )

    col4.metric(
        "Aggregate Profit Margin",
        f"{profit_margin:.2f}%"
    )

    st.metric(
        "Average Discount Rate",
        f"{average_discount:.2f}%"
    )

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Product Analysis",
        "Customer Analysis",
        "Discount Analysis"
    ])

    # Overview
    with tab1:
        st.header("Dataset Overview")

        st.write("Rows:", len(filtered_df))
        st.write("Columns:", len(filtered_df.columns))

        st.dataframe(
            filtered_df.head(100),
            use_container_width=True
        )

        st.subheader("Missing Values")

        missing_values = (
            filtered_df.isnull()
            .sum()
            .sort_values(ascending=False)
        )

        st.dataframe(
            missing_values.to_frame("Missing Values"),
            use_container_width=True
        )

    # Product Analysis
    with tab2:
        st.header("Product Category Performance")

        if "Category Name" in filtered_df.columns:

            category_analysis = filtered_df.groupby(
                "Category Name"
            ).agg(
                Total_Sales=("Order Item Total", "sum"),
                Total_Profit=("Order Profit Per Order", "sum")
            ).sort_values(
                "Total_Sales",
                ascending=False
            )

            st.dataframe(
                category_analysis,
                use_container_width=True
            )

            top_categories = category_analysis.head(10)

            fig, ax = plt.subplots(figsize=(10, 5))

            top_categories["Total_Sales"].plot(
                kind="bar",
                ax=ax
            )

            ax.set_title("Top 10 Categories by Sales")
            ax.set_xlabel("Category")
            ax.set_ylabel("Net Sales")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            st.pyplot(fig)
            plt.close(fig)

        else:
            st.warning("Category Name column not found.")

    # Customer Analysis
    with tab3:
        st.header("Customer Segment Performance")

        if "Customer Segment" in filtered_df.columns:

            customer_analysis = filtered_df.groupby(
                "Customer Segment"
            ).agg(
                Total_Sales=("Order Item Total", "sum"),
                Total_Profit=("Order Profit Per Order", "sum")
            ).sort_values(
                "Total_Profit",
                ascending=False
            )

            st.dataframe(
                customer_analysis,
                use_container_width=True
            )

            fig, ax = plt.subplots(figsize=(8, 5))

            customer_analysis["Total_Profit"].plot(
                kind="bar",
                ax=ax
            )

            ax.set_title("Profit by Customer Segment")
            ax.set_xlabel("Customer Segment")
            ax.set_ylabel("Recorded Profit")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()

            st.pyplot(fig)
            plt.close(fig)

        else:
            st.warning("Customer Segment column not found.")

    # Discount Analysis
    with tab4:
        st.header("Discount Analysis")

        discount_df = filtered_df.copy()

        discount_df["Discount Band"] = pd.cut(
            discount_df["Order Item Discount Rate"],
            bins=[-0.001, 0.05, 0.10, 0.20, 1.0],
            labels=[
                "0–5%",
                "5–10%",
                "10–20%",
                "Above 20%"
            ]
        )

        discount_analysis = discount_df.groupby(
            "Discount Band",
            observed=False
        ).agg(
            Items=("Order Item Discount Rate", "count"),
            Total_Sales=("Order Item Total", "sum"),
            Total_Profit=("Order Profit Per Order", "sum")
        )

        st.dataframe(
            discount_analysis,
            use_container_width=True
        )

        fig, ax = plt.subplots(figsize=(9, 5))

        discount_analysis[
            ["Total_Sales", "Total_Profit"]
        ].plot(
            kind="bar",
            ax=ax
        )

        ax.set_title("Sales and Profit by Discount Band")
        ax.set_xlabel("Discount Band")
        ax.set_ylabel("Amount")
        plt.xticks(rotation=0)
        plt.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

    # Download filtered data
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Dataset",
        data=csv_data,
        file_name="filtered_supply_chain_data.csv",
        mime="text/csv"
    )

else:
    st.info(
        "Upload your APL_Logistics.csv dataset using the sidebar "
        "to start the analysis."
    )
