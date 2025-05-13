from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Load data
df = pd.read_csv("ecommerce_data.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M').astype(str)

@app.route('/', methods=['GET'])
def dashboard():
    selected_month = request.args.get('month', 'All')

    if selected_month != 'All':
        filtered_df = df[df['Month'] == selected_month]
    else:
        filtered_df = df.copy()

    # KPIs
    total_revenue = round(filtered_df['Total Sales'].sum(), 2)
    total_orders = len(filtered_df)
    unique_customers = filtered_df['Customer ID'].nunique()
    average_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0

    # Dropdown options
    month_options = ['All'] + sorted(df['Month'].unique().tolist())

    # Monthly Revenue Chart
    monthly = filtered_df.groupby('Month').sum(numeric_only=True)['Total Sales'].reset_index()
    fig1 = px.bar(monthly, x='Month', y='Total Sales', title="Monthly Revenue")

    # Top Products
    top_products = filtered_df.groupby('Product Name').sum(numeric_only=True)['Total Sales'] \
        .sort_values(ascending=False).head(5).reset_index()
    fig2 = px.pie(top_products, names='Product Name', values='Total Sales', title="Top Selling Products")

    # Payment Method
    payment_counts = filtered_df['Payment Method'].value_counts().reset_index()
    payment_counts.columns = ['Payment Method', 'count']
    fig3 = px.pie(payment_counts, names='Payment Method', values='count', title="Payment Methods Used")

    # Sales by Country
    country_sales = filtered_df.groupby('Country').sum(numeric_only=True)['Total Sales'].reset_index()
    fig4 = px.bar(country_sales, x='Country', y='Total Sales', title="Sales by Country")

    # Sales by Category
    category_sales = filtered_df.groupby('Product Category').sum(numeric_only=True)['Total Sales'].reset_index()
    fig5 = px.bar(category_sales, x='Product Category', y='Total Sales', title="Product Category Performance")

    # Convert plots to HTML
    plot1 = pio.to_html(fig1, full_html=False)
    plot2 = pio.to_html(fig2, full_html=False)
    plot3 = pio.to_html(fig3, full_html=False)
    plot4 = pio.to_html(fig4, full_html=False)
    plot5 = pio.to_html(fig5, full_html=False)

    return render_template("index.html",
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           unique_customers=unique_customers,
                           average_order_value=average_order_value,
                           month_options=month_options,
                           selected_month=selected_month,
                           plot1=plot1,
                           plot2=plot2,
                           plot3=plot3,
                           plot4=plot4,
                           plot5=plot5)

if __name__ == "__main__":
    app.run(debug=True)
