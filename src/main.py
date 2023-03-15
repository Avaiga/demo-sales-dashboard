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


# initialization of variables
cities = list(df["City"].unique())
types = list(df["Customer_type"].unique())
genders = list(df["Gender"].unique())
city = cities
customer_type = types
gender = genders

layout = {"margin":{"l":220}}

# Markdown for the entire page
## NOTE: {: .orange} references a color from main.css use to style my text
## <text|
## |text> 
## "text" here is just a name given to my part/my section
## it has no meaning in the code
page = """<|toggle|theme|>

<|layout|columns=20 80|gap=30px|
<sidebar|
## Please **filter**{: .orange} here:

<|{city}|selector|lov={cities}|multiple|label=Select the City|dropdown|on_change=on_filter|width=100%|>

<|{customer_type}|selector|lov={types}|multiple|label=Select the Customer Type|dropdown|on_change=on_filter|width=100%|>

<|{gender}|selector|lov={genders}|multiple|label=Select the Gender|dropdown|on_change=on_filter|width=100%|>
|sidebar>

<main_page|
# 📊 **Sales**{: .orange} Dashboard

<|layout|columns=1 1 1|
<total_sales|
## **Total**{: .orange} sales:
### US $ <|{int(df_selection["Total"].sum())}|>
|total_sales>

<average_rating|
## **Average**{: .orange} Rating:
### <|{round(df_selection["Rating"].mean(), 1)}|> <|{"⭐" * int(round(round(df_selection["Rating"].mean(), 1), 0))}|>
|average_rating>

<average_sale|
## Average Sales Per **Transaction**{: .orange}:
### US $ <|{round(df_selection["Total"].mean(), 2)}|>
|average_sale>
|>

<br/>

<charts|
<|{sales_by_hour}|chart|x=index|y=Total|type=bar|title=Sales by hour|color=#ff462b|>

<|{sales_by_product_line}|chart|x=Total|y=index|type=bar|orientation=h|title=Sales by product|layout={layout}|color=#ff462b|>
|charts>
|main_page>
|>

Code from [Coding is Fun](https://github.com/Sven-Bo)

Get the Taipy Code [here](https://github.com/Avaiga/demo-sales-dashboard) and the original code [here](https://github.com/Sven-Bo/streamlit-sales-dashboard)
"""

def filter(city, customer_type, gender):
    df_selection = df[df["City"].isin(city) & df["Customer_type"].isin(customer_type) & df["Gender"].isin(gender)]

    # SALES BY PRODUCT LINE [BAR CHART]
    sales_by_product_line = df_selection[["Product line", "Total"]].groupby(by=["Product line"])\
                                                                   .sum()[["Total"]]\
                                                                   .sort_values(by="Total")
    sales_by_product_line['index'] = sales_by_product_line.index

    # SALES BY HOUR [BAR CHART]
    sales_by_hour = df_selection[["hour", "Total"]].groupby(by=["hour"]).sum()[["Total"]]
    sales_by_hour['index'] = sales_by_hour.index
    return df_selection, sales_by_product_line, sales_by_hour

def on_filter(state):
    state.df_selection,\
    state.sales_by_product_line,\
    state.sales_by_hour = filter(state.city,
                                 state.customer_type,
                                 state.gender)


if __name__ == "__main__":
    # initialize dataframes
    df_selection,\
    sales_by_product_line,\
    sales_by_hour = filter(city,
                           customer_type,
                           gender)

    # run the app
    Gui(page).run()

