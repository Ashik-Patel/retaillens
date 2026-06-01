# RetailLens

RetailLens looks at customer purchase history and groups them based on how they shop. It also predicts how much each customer is likely to spend in the next 12 months.

🔗 **Live app:** [retaillens.streamlit.app](https://retaillens.streamlit.app)

---

## Why I built this

Not every customer is the same. Some buy regularly, others haven't ordered in months. This project helps a business see who their best customers are, who might be leaving, and where to spend their marketing money.

---

## What I did

**1. Cleaned the data**
The raw dataset had over a million rows. I removed orders with no customer ID, cancelled orders, and anything with missing or incorrect values. That left around 805,000 usable transactions from 5,878 customers.

**2. RFM analysis**
I turned all those transactions into one summary row per customer showing three things — when they last bought, how many times they've ordered, and how much they've spent overall.

**3. Grouped customers into segments**
Used a clustering algorithm to split customers into three groups based on their buying patterns — Champions, Loyal Customers, and Lost or Inactive customers.

**4. Predicted future value**
Used a statistical model to estimate how much each customer is likely to spend over the next 12 months. Champions averaged £55,447, Loyal Customers £2,008, and Lost customers just £97.

---

## The app

The Streamlit dashboard has five pages:

- **Overview** — key numbers, segment breakdown, monthly revenue
- **Segment Explorer** — compare segments with interactive charts
- **CLV Analysis** — predicted value by segment and top customers
- **Customer Lookup** — search any customer and see their order history
- **Recommendations** — what to do with each customer group

---

## Tech stack

| Area | Tools |
|---|---|
| Data wrangling | Python, pandas, numpy |
| Machine learning | scikit-learn |
| CLV modelling | lifetimes |
| Visualisation | plotly, matplotlib, seaborn |
| App & deployment | Streamlit, Streamlit Community Cloud |

---

Built by **Ashik Patel** — Data Analyst, United Kingdom  
[retaillens.streamlit.app](https://retaillens.streamlit.app)