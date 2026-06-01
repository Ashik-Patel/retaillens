# RetailLens

🔗 **Live app:** [retaillens.streamlit.app](https://retaillens.streamlit.app)

I built this project to sharpen my data analysis skills and push myself to work with a real dataset end to end — from messy raw data all the way through to a live deployed app. I learnt a lot along the way, especially around customer modelling and building things that actually work outside of a notebook.

---

## What it does

RetailLens takes customer transaction data and helps answer a simple question — which customers are worth investing in, and which ones have already moved on?

It groups customers by how they shop and predicts how much each one is likely to spend over the next year. The results are shown in an interactive dashboard anyone can open in their browser.

---

## How I built it

**Cleaning the data**
The raw dataset had just over a million rows of UK retail transactions. A lot of it wasn't usable — guest orders with no customer ID, cancellations, and rows with missing values. After cleaning, I had around 805,000 transactions from 5,878 customers to work with.

**RFM analysis**
I summarised each customer's history into three numbers — how recently they bought, how often they order and how much they've spent in total. This is called RFM analysis and it's a straightforward way to compare customers who would otherwise be lost in a sea of rows.

**Segmenting customers**
I used K-Means clustering to group customers into three segments based on their RFM scores. Rather than just picking a number of groups, I used the silhouette score to find the right one objectively.

**Predicting future value**
I used the BG/NBD model to predict how often each customer would buy again, and the Gamma-Gamma model to estimate how much they'd spend per order. Together these give a 12-month revenue prediction per customer - Champions averaged around £55k, Loyal Customers around £2k and Lost customers just £97.

---

## The dashboard

Built with Streamlit and publicly deployed. It has five pages:

- **Overview** — top level numbers and a monthly revenue chart
- **Segment Explorer** — compare the three customer groups visually
- **CLV Analysis** — predicted value by segment and the top 20 customers
- **Customer Lookup** — type in any customer ID to see their full history
- **Recommendations** — practical actions for each customer group

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