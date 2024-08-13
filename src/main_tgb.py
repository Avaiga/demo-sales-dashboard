import pandas as pd
from taipy.gui import Gui, notify
import taipy.gui.builder as tgb

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

city = cities = list(df["City"].unique())
customer_type = types = list(df["Customer_type"].unique())
gender = genders = list(df["Gender"].unique())

layout = {"margin": {"l": 220}}


def filter(city, customer_type, gender):
    df_selection = df[
        df["City"].isin(city)
        & df["Customer_type"].isin(customer_type)
        & df["Gender"].isin(gender)
    ]

    # SALES BY PRODUCT LINE [BAR CHART]
    sales_by_product_line = (
        df_selection[["Product line", "Total"]]
        .groupby(by=["Product line"])
        .sum()[["Total"]]
        .sort_values(by="Total")
    )
    sales_by_product_line["Product line"] = sales_by_product_line.index

    # SALES BY HOUR [BAR CHART]
    sales_by_hour = (
        df_selection[["Hour", "Total"]].groupby(by=["Hour"]).sum()[["Total"]]
    )
    sales_by_hour["Hour"] = sales_by_hour.index
    return df_selection, sales_by_product_line, sales_by_hour


def on_filter(state):
    if len(state.city) == 0 or len(state.customer_type) == 0 or len(state.gender) == 0:
        notify(state, "Error", "No results found. Check the filters.")
        return

    state.df_selection, state.sales_by_product_line, state.sales_by_hour = filter(
        state.city, state.customer_type, state.gender
    )


with tgb.Page() as page:
    tgb.toggle(theme=True)

    with tgb.layout(columns="25 75", columns__mobile="1", gap="30px"):
        with tgb.part("sidebar"):
            tgb.text("## Please **filter** here:", mode="md")

            tgb.selector(
                "{city}",
                lov=cities,
                multiple=True,
                label="Select the City",
                dropdown=True,
                on_change=on_filter,
                class_name="fullwidth",
            )

            tgb.selector(
                "{customer_type}",
                lov=types,
                multiple=True,
                label="Select the Customer Type",
                dropdown=True,
                on_change=on_filter,
                class_name="fullwidth mt1",
            )

            tgb.selector(
                "{gender}",
                lov=genders,
                multiple=True,
                label="Select the Gender",
                dropdown=True,
                on_change=on_filter,
                class_name="fullwidth mt1",
            )

        with tgb.part("m1"):
            tgb.text("# 📊 Sales **Dashboard**", mode="md")

            with tgb.layout(columns="1 1 1"):
                tgb.text(
                    lambda df_selection: f"""## **Total** sales:\n\n#### US $ {int(df_selection['Total'].sum())}""",
                    mode="md",
                )

                tgb.text(
                    lambda df_selection: f"""## Average **Rating**:\n\n#### {round(df_selection['Rating'].mean(), 1)} {'⭐' * int(round(round(df_selection['Rating'].mean(), 1), 0))}""",
                    mode="md",
                )

                tgb.text(
                    lambda df_selection: f"""## Average **Sales**:\n\n#### US $ {round(df_selection['Total'].mean(), 2)}""",
                    mode="md",
                )

            tgb.html("br")

            with tgb.expandable(title="Sales Table", expanded=False):
                tgb.table("{df_selection}", page_size=5)

            with tgb.part("card p2"):
                tgb.chart(
                    "{sales_by_hour}",
                    x="Hour",
                    y="Total",
                    type="bar",
                    title="Sales by Hour",
                    layout=layout,
                )

                tgb.chart(
                    "{sales_by_product_line}",
                    x="Total",
                    y="Product line",
                    type="bar",
                    orientation="h",
                    title="Sales by Product",
                    layout=layout,
                )

            tgb.text(
                """Get the Taipy Code [here](https://github.com/Avaiga/demo-sales-dashboard) and 
                   the original code [here](https://github.com/Sven-Bo/streamlit-sales-dashboard)""",
                mode="md",
            )


if __name__ == "__main__":
    df_selection, sales_by_product_line, sales_by_hour = filter(
        city, customer_type, gender
    )
    Gui(page).run(margin="0em", title="Sales Dashboard")
