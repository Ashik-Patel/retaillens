"""RetailLens dashboard for RFM segmentation and CLV analysis."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Page setup
st.set_page_config(
    page_title="RetailLens",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Small CSS block for sidebar branding
st.markdown(
    """
<style>
    [data-testid="stSidebar"] { background-color: #0f1117; }
    [data-testid="stSidebar"] * { color: #fafafa !important; }
    .brand-title { font-size: 26px; font-weight: 700; letter-spacing: -0.5px; color: #1D9E75; }
    .brand-sub   { font-size: 12px; color: #888; margin-top: -6px; }
    .segment-pill {
        display: inline-block; padding: 3px 14px;
        border-radius: 20px; font-size: 13px; font-weight: 500;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Segment colours used across all charts
SEGMENT_COLORS = {
    "Champions": "#1D9E75",
    "Loyal Customers": "#378ADD",
    "Lost / Inactive": "#888780",
}

# Data folder path
DATA_DIR = Path(__file__).parent.parent / "data"

# Required columns for the dashboard
REQUIRED_RFM_COLUMNS = {
    "Customer ID",
    "Segment",
    "Recency",
    "Frequency",
    "Monetary",
    "CLV_12m",
}

REQUIRED_TRANSACTION_COLUMNS = {
    "Customer ID",
    "Invoice",
    "InvoiceDate",
    "StockCode",
    "TotalRevenue",
}


# Helper functions
@st.cache_data(show_spinner="Loading RFM and CLV data...")
def load_rfm() -> pd.DataFrame:
    """Load customer-level RFM and CLV data."""
    return pd.read_csv(DATA_DIR / "rfm_clv.csv")


@st.cache_data(show_spinner="Loading transaction data...")
def load_transactions() -> pd.DataFrame:
    """Load transaction-level retail data."""
    return pd.read_csv(DATA_DIR / "clean_data.csv", parse_dates=["InvoiceDate"])


def validate_columns(data: pd.DataFrame, required_columns: set[str], dataset_name: str) -> None:
    """Stop the app if a required dataset column is missing."""
    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        st.error(
            f"{dataset_name} is missing required columns: "
            f"{', '.join(sorted(missing_columns))}"
        )
        st.stop()


def segment_data(segment: str) -> pd.DataFrame:
    """Return all customers belonging to one segment."""
    return rfm[rfm["Segment"] == segment]


def segment_avg(segment: str, column: str) -> float:
    """Return the average value for one segment."""
    data = segment_data(segment)
    return 0.0 if data.empty else data[column].mean()


def percentile_cap(data: pd.DataFrame, column: str, quantile: float = 0.99) -> float:
    """Set a chart cap using a percentile instead of a fixed number."""
    if data.empty:
        return 0.0
    return data[column].quantile(quantile)


def format_currency(value: float, decimals: int = 0) -> str:
    """Format values as GBP."""
    return f"£{value:,.{decimals}f}"


# Load data
rfm = load_rfm()
df = load_transactions()

validate_columns(rfm, REQUIRED_RFM_COLUMNS, "rfm_clv.csv")
validate_columns(df, REQUIRED_TRANSACTION_COLUMNS, "clean_data.csv")

# Keep Customer ID type consistent in both datasets
rfm["Customer ID"] = rfm["Customer ID"].astype(str)
df["Customer ID"] = df["Customer ID"].astype(str)

# Build date range from the data
start_date = df["InvoiceDate"].min().strftime("%b %Y")
end_date = df["InvoiceDate"].max().strftime("%b %Y")


# Sidebar
with st.sidebar:
    st.markdown('<div class="brand-title">RetailLens</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Customer Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Segment Explorer",
            "CLV Analysis",
            "Customer Lookup",
            "Recommendations",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Dataset**")
    st.caption(f"{len(df):,} transactions")
    st.caption(f"{rfm['Customer ID'].nunique():,} customers")
    st.caption(f"{start_date} – {end_date}")
    st.markdown("---")
    st.caption("Built by **Ashik Patel**")
    st.caption("UCI Online Retail II dataset")


# Page 1: Overview
if page == "Overview":
    st.title("RetailLens — Customer Intelligence")
    st.markdown(
        "RFM segmentation + BG/NBD Customer Lifetime Value model · "
        "UK e-commerce · UCI Online Retail II"
    )
    st.markdown("---")

    # Main KPI cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{rfm['Customer ID'].nunique():,}")
    c2.metric("Total Revenue", format_currency(rfm["Monetary"].sum()))
    c3.metric("Avg CLV (12m)", format_currency(rfm["CLV_12m"].mean()))
    c4.metric(
        "Champion Revenue",
        format_currency(segment_data("Champions")["Monetary"].sum()),
    )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer segments")

        # Customer count by segment
        seg_counts = rfm["Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]

        fig = px.pie(
            seg_counts,
            values="Count",
            names="Segment",
            hole=0.55,
            color="Segment",
            color_discrete_map=SEGMENT_COLORS,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly revenue trend")

        # Monthly revenue trend
        monthly_df = df.copy()
        monthly_df["YearMonth"] = monthly_df["InvoiceDate"].dt.to_period("M").astype(str)
        monthly = monthly_df.groupby("YearMonth", as_index=False)["TotalRevenue"].sum()

        fig2 = px.bar(
            monthly,
            x="YearMonth",
            y="TotalRevenue",
            labels={"TotalRevenue": "Revenue (£)", "YearMonth": ""},
            color_discrete_sequence=["#1D9E75"],
        )
        fig2.update_layout(margin=dict(t=20, b=40, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Segment summary")

    # Summary table by segment
    summary = (
        rfm.groupby("Segment")
        .agg(
            Customers=("Customer ID", "count"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Spend=("Monetary", "mean"),
            Avg_CLV_12m=("CLV_12m", "mean"),
            Total_Revenue=("Monetary", "sum"),
        )
        .round(1)
        .reset_index()
    )
    summary.columns = [
        "Segment",
        "Customers",
        "Avg Recency (days)",
        "Avg Orders",
        "Avg Spend (£)",
        "Avg CLV 12m (£)",
        "Total Revenue (£)",
    ]
    st.dataframe(summary, use_container_width=True, hide_index=True)


# Page 2: Segment Explorer
elif page == "Segment Explorer":
    st.title("Segment Explorer")
    st.markdown("Compare RFM distributions across customer segments.")
    st.markdown("---")

    selected = st.multiselect(
        "Select segments to display",
        options=sorted(rfm["Segment"].unique().tolist()),
        default=sorted(rfm["Segment"].unique().tolist()),
    )

    # Filter selected segments
    filtered = rfm[rfm["Segment"].isin(selected)].copy() if selected else rfm.copy()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Recency vs spend")
        fig = px.scatter(
            filtered,
            x="Recency",
            y="Monetary",
            color="Segment",
            size="Frequency",
            color_discrete_map=SEGMENT_COLORS,
            hover_data=["Customer ID", "Frequency", "CLV_12m"],
            labels={"Recency": "Recency (days)", "Monetary": "Total Spend (£)"},
            opacity=0.7,
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Purchase frequency distribution")

        # Hide extreme frequency outliers for readability
        freq_cap = percentile_cap(filtered, "Frequency")
        freq_plot = filtered[filtered["Frequency"] <= freq_cap]

        fig2 = px.histogram(
            freq_plot,
            x="Frequency",
            color="Segment",
            barmode="overlay",
            color_discrete_map=SEGMENT_COLORS,
            labels={"Frequency": "Number of orders"},
            opacity=0.75,
            nbins=40,
        )
        fig2.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("RFM metric distributions by segment")
    metric = st.selectbox("Metric", ["Recency", "Frequency", "Monetary", "CLV_12m"])

    fig3 = px.box(
        filtered,
        x="Segment",
        y=metric,
        color="Segment",
        color_discrete_map=SEGMENT_COLORS,
        points="outliers",
    )
    fig3.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)


# Page 3: CLV Analysis
elif page == "CLV Analysis":
    st.title("Customer Lifetime Value Analysis")
    st.markdown("Predicted 12-month CLV using the **BG/NBD + Gamma-Gamma** model.")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg CLV — Champions", format_currency(segment_avg("Champions", "CLV_12m")))
    c2.metric(
        "Avg CLV — Loyal Customers",
        format_currency(segment_avg("Loyal Customers", "CLV_12m")),
    )
    c3.metric(
        "Avg CLV — Lost / Inactive",
        format_currency(segment_avg("Lost / Inactive", "CLV_12m")),
    )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Average predicted CLV by segment")
        clv_seg = rfm.groupby("Segment", as_index=False)["CLV_12m"].mean()
        clv_seg.columns = ["Segment", "Avg CLV (£)"]
        clv_seg = clv_seg.sort_values("Avg CLV (£)", ascending=False)

        fig = px.bar(
            clv_seg,
            x="Segment",
            y="Avg CLV (£)",
            color="Segment",
            color_discrete_map=SEGMENT_COLORS,
            text_auto=".0f",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        clv_cap = percentile_cap(rfm, "CLV_12m")
        st.subheader(f"CLV distribution (capped at 99th percentile: {format_currency(clv_cap)})")

        clv_plot = rfm[rfm["CLV_12m"] <= clv_cap]
        fig2 = px.histogram(
            clv_plot,
            x="CLV_12m",
            color="Segment",
            color_discrete_map=SEGMENT_COLORS,
            labels={"CLV_12m": "Predicted CLV 12m (£)"},
            nbins=60,
            opacity=0.75,
            barmode="overlay",
        )
        fig2.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top 20 customers by predicted CLV")
    top20 = rfm.nlargest(20, "CLV_12m")[
        ["Customer ID", "Segment", "Recency", "Frequency", "Monetary", "CLV_12m"]
    ].copy()
    top20.columns = [
        "Customer ID",
        "Segment",
        "Recency (days)",
        "Orders",
        "Total Spend (£)",
        "Predicted CLV 12m (£)",
    ]
    st.dataframe(top20.round(1), use_container_width=True, hide_index=True)

    st.subheader("Historical spend vs predicted CLV")

    # Cap extreme CLV values in the scatter chart
    scatter_cap = percentile_cap(rfm, "CLV_12m", 0.995)
    scatter_plot = rfm[rfm["CLV_12m"] <= scatter_cap]

    fig3 = px.scatter(
        scatter_plot,
        x="Monetary",
        y="CLV_12m",
        color="Segment",
        color_discrete_map=SEGMENT_COLORS,
        labels={
            "Monetary": "Total Historical Spend (£)",
            "CLV_12m": "Predicted CLV 12m (£)",
        },
        opacity=0.6,
        hover_data=["Customer ID", "Frequency"],
    )
    fig3.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)


# Page 4: Customer Lookup
elif page == "Customer Lookup":
    st.title("Customer Lookup")
    st.markdown("Enter a Customer ID to view their full profile, segment, and predicted CLV.")
    st.markdown("---")

    customer_ids = sorted(rfm["Customer ID"].unique().tolist())
    selected_id = st.selectbox("Select or type a Customer ID", customer_ids)

    # Get selected customer profile
    cust = rfm[rfm["Customer ID"] == selected_id].iloc[0]
    segment = cust["Segment"]
    color = SEGMENT_COLORS.get(segment, "#888")

    st.markdown(
        f"""
    <div style="border-left:5px solid {color}; padding:1rem 1.5rem;
                background:#f8f9fa; border-radius:8px; margin-bottom:1rem;">
        <h3 style="margin:0; color:#111;">Customer #{selected_id}</h3>
        <span class="segment-pill" style="background:{color}20; color:{color}; margin-top:6px; display:inline-block;">
            {segment}
        </span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last purchase", f"{int(cust['Recency'])} days ago")
    c2.metric("Total orders", f"{int(cust['Frequency'])}")
    c3.metric("Total spend", format_currency(cust["Monetary"], 2))
    c4.metric("Predicted CLV", format_currency(cust["CLV_12m"], 2))

    # Get transaction history for the selected customer
    cust_tx = df[df["Customer ID"] == selected_id].copy()
    cust_tx = cust_tx.sort_values("InvoiceDate", ascending=False)

    st.subheader("Spending over time")
    st.caption(f"`{len(cust_tx):,}` line items across `{cust_tx['Invoice'].nunique()}` orders")

    cust_tx["Month"] = cust_tx["InvoiceDate"].dt.to_period("M").astype(str)
    monthly_spend = cust_tx.groupby("Month", as_index=False)["TotalRevenue"].sum()

    fig = px.bar(
        monthly_spend,
        x="Month",
        y="TotalRevenue",
        labels={"TotalRevenue": "Revenue (£)", "Month": ""},
        color_discrete_sequence=[color],
    )
    fig.update_layout(margin=dict(t=10, b=40))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent orders")

    # Convert line items into invoice-level orders
    recent = (
        cust_tx.groupby("Invoice")
        .agg(
            Date=("InvoiceDate", "first"),
            Items=("StockCode", "count"),
            Revenue=("TotalRevenue", "sum"),
        )
        .reset_index()
        .sort_values("Date", ascending=False)
        .head(10)
    )
    recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
    recent["Revenue"] = recent["Revenue"].round(2)
    st.dataframe(recent, use_container_width=True, hide_index=True)


# Page 5: Recommendations
elif page == "Recommendations":
    st.title("Business Recommendations")
    st.markdown("Actionable marketing strategies derived from RetailLens segmentation and CLV modelling.")
    st.markdown("---")

    champions = segment_data("Champions")
    loyal = segment_data("Loyal Customers")
    inactive = segment_data("Lost / Inactive")

    # Recommendation text uses live values from the data
    recs = {
        "Champions": {
            "color": "#1D9E75",
            "stats": champions,
            "what": (
                f"Your top {len(champions):,} customers by purchase frequency and spend. "
                f"They buy often, recently, and have the highest predicted CLV "
                f"(avg {format_currency(champions['CLV_12m'].mean())})."
            ),
            "actions": [
                "Send thank-you emails after purchase",
                "Give early access to new products or seasonal offers",
                "Offer small loyalty discounts for repeat purchases",
                "Recommend similar products based on their past orders",
                "Ask for reviews because they are your best customers",
            ],
        },
        "Loyal Customers": {
            "color": "#378ADD",
            "stats": loyal,
            "what": (
                f"Your core base of {len(loyal):,} active customers. They bought recently, "
                f"show moderate frequency, and have strong growth potential "
                f"(avg CLV {format_currency(loyal['CLV_12m'].mean())})."
            ),
            "actions": [
                "Send monthly emails with products they may like",
                "Offer free shipping or a small discount on their next order",
                "Send reminders if they have not bought for 90 days",
                "Promote related products to increase basket size",
                "Run campaigns before busy months such as September and October",
            ],
        },
        "Lost / Inactive": {
            "color": "#888780",
            "stats": inactive,
            "what": (
                f"{len(inactive):,} customers have not purchased in "
                f"{inactive['Recency'].mean():.0f} days on average. Their average CLV is "
                f"{format_currency(inactive['CLV_12m'].mean())}, so reactivation should be selective."
            ),
            "actions": [
                "Send one win-back email with a clear discount",
                "Show products similar to what they bought before",
                "Ask why they stopped buying using a short survey",
                "If they do not respond, stop sending frequent marketing emails",
                "Focus more budget on Champions and Loyal Customers",
            ],
        },
    }

    for seg, data in recs.items():
        with st.expander(
            f"{seg}  —  {len(data['stats']):,} customers",
            expanded=True,
        ):
            st.markdown(f"**What the data says:** {data['what']}")
            st.markdown("**Recommended actions:**")
            for action in data["actions"]:
                st.markdown(f"- {action}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Avg recency", f"{data['stats']['Recency'].mean():.0f} days")
            c2.metric("Avg orders", f"{data['stats']['Frequency'].mean():.1f}")
            c3.metric("Avg CLV 12m", format_currency(data["stats"]["CLV_12m"].mean()))

    st.markdown("---")
    st.subheader("Priority action matrix")

    priority = pd.DataFrame(
        {
            "Segment": ["Champions", "Loyal Customers", "Lost / Inactive"],
            "Effort": ["Low", "Medium", "High"],
            "Impact": ["Very High", "High", "Low"],
            "Priority": [
                "1 — Retain & reward",
                "2 — Grow frequency",
                "3 — Win-back or cut",
            ],
            "Budget split": ["20%", "60%", "20%"],
        }
    )
    st.dataframe(priority, use_container_width=True, hide_index=True)
