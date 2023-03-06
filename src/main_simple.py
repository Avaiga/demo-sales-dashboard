import pandas as pd
from taipy import Gui

# ---- READ EXCEL ----

df = pd.read_excel(
    io="data/supermarkt_sales.xlsx",
    engine="openpyxl",
    sheet_name="Sales",
    skiprows=3,
    usecols="B:R",
    nrows=1000,
)
# Add 'hour' column to dataframe
df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour


cities = list(df["City"].unique())
types = list(df["Customer_type"].unique())
genders = list(df["Gender"].unique())
city = cities
customer_type = types
gender = genders

layout = {"margin":{"l":150}}
show = True
page = """
<|toggle|theme|>

<|{show}|pane|persistent=True|
## Please filter here:

<|{city}|selector|lov={cities}|multiple|label=Select the City|dropdown|on_change=filter_data|width=100%|>

<|{customer_type}|selector|lov={types}|multiple|label=Select the Customer Type|dropdown|on_change=filter_data|width=100%|>

<|{gender}|selector|lov={genders}|multiple|label=Select the Gender|dropdown|on_change=filter_data|width=100%|>
|>

# 📊 Sales Dashboard

<|layout|columns=1 1 1|
<total_sales|
### Total sales:
US $ <|{int(df_selection["Total"].sum())}|>
|total_sales>

<average_rating|
### Average Rating:
<|{round(df_selection["Rating"].mean(), 1)}|> <|{"⭐" * int(round(round(df_selection["Rating"].mean(), 1), 0))}|>
|average_rating>

<average_sale|
### Average Sales Per Transaction:
US $ <|{round(df_selection["Total"].mean(), 2)}|>
|average_sale>
|>

<br/>

<charts|
<|{sales_by_hour}|chart|x=index|y=Total|type=bar|title=Sales by hour|>

<|{sales_by_product_line}|chart|x=Total|y=index|type=bar|orientation=h|title=Sales by product|layout={layout}|>
|charts>

"""

def filter_data(state):
    print("Begin filter_data")
    state.df_selection = df[df["City"].isin(state.city) & df["Customer_type"].isin(state.customer_type) & df["Gender"].isin(state.gender)]

    sales_by_product_line = state.df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
    sales_by_product_line['index'] = sales_by_product_line.index
    state.sales_by_product_line = sales_by_product_line

    # SALES BY HOUR [BAR CHART]
    sales_by_hour = state.df_selection.groupby(by=["hour"]).sum()[["Total"]]
    sales_by_hour['index'] = sales_by_hour.index
    state.sales_by_hour = sales_by_hour
    print("End filter_data")


df_selection = df[df["City"].isin(city) & df["Customer_type"].isin(customer_type) & df["Gender"].isin(gender)]


# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
sales_by_product_line['index'] = sales_by_product_line.index

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
sales_by_hour['index'] = sales_by_hour.index

Gui(page).run(host="0.0.0.0", port=4006)

