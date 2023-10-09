import pandas as pd
from taipy.gui import Gui, notify

# ---- READ EXCEL ----

df = pd.read_excel(
    io="data/supermarkt_sales.xlsx",
    engine="openpyxl",
    sheet_name="Sales",
    skiprows=3,
    usecols="B:R",
    nrows=1000,
)
# Add 'Hour' column to dataframe
df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour


cities = list(df["City"].unique())
types = list(df["Customer_type"].unique())
genders = list(df["Gender"].unique())
city = cities
customer_type = types
gender = genders

layout = {"margin":{"l":150}}

page = """
<|toggle|theme|>

<|25 75|layout|gap=30px|
<|sidebar|
## Please **filter**{: .color-primary} here:

<|{city}|selector|lov={cities}|multiple|label=Select the City|dropdown|on_change=filter_data|class_name=fullwidth|>

<|{customer_type}|selector|lov={types}|multiple|label=Select the Customer Type|dropdown|on_change=filter_data|class_name=fullwidth|>

<|{gender}|selector|lov={genders}|multiple|label=Select the Gender|dropdown|on_change=filter_data|class_name=fullwidth|>
|>

<main_page|
# 📊 Sales **Dashboard**{: .color-primary}

<|1 1 1|layout|
<total_sales|
## **Total**{: .color-primary} sales:
US $ <|{int(df_selection["Total"].sum())}|>
|total_sales>

<average_rating|
## Average **Rating**{: .color-primary}:
<|{round(df_selection["Rating"].mean(), 1)}|> <|{"⭐" * int(round(round(df_selection["Rating"].mean(), 1), 0))}|>
|average_rating>

<average_sale|
## Average **Sales**{: .color-primary}:
US $ <|{round(df_selection["Total"].mean(), 2)}|>
|average_sale>
|>

<br/>

<|Table|expandable|not expanded|
<|{df_selection}|table|>
|>

<|card p2|
<|{sales_by_hour}|chart|x=Hour|y=Total|type=bar|title=Sales by hour|>

<|{sales_by_product_line}|chart|x=Total|y=Product|type=bar|orientation=h|title=Sales by product|layout={layout}|>
|>
|main_page>
|>
"""

def filter_data(state):
    state.df_selection = df[df["City"].isin(state.city) & df["Customer_type"].isin(state.customer_type) & df["Gender"].isin(state.gender)]

    # SALES BY PRODUCT LINE [BAR CHART]
    sales_by_product_line = state.df_selection[['Product line', 'Total']].groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
    sales_by_product_line['Product'] = sales_by_product_line.index
    state.sales_by_product_line = sales_by_product_line

    # SALES BY HOUR [BAR CHART]
    sales_by_hour = state.df_selection[['Hour', 'Total']].groupby(by=["Hour"]).sum()[["Total"]]
    sales_by_hour['Hour'] = sales_by_hour.index
    state.sales_by_hour = sales_by_hour


df_selection = df[df["City"].isin(city) & df["Customer_type"].isin(customer_type) & df["Gender"].isin(gender)]


# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection[['Product line', 'Total']].groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
sales_by_product_line['Product'] = sales_by_product_line.index

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection[['Hour', 'Total']].groupby(by=["Hour"]).sum()[["Total"]]
sales_by_hour['Hour'] = sales_by_hour.index

Gui(page).run(margin="0em", title="Sales Dashboard")

