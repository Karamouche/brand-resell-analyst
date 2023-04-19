from dash import Dash, dcc, html, Input, Output
from pandas import read_csv
from graph_builder import bar_chart, pie_chart, histogram, scatter_chart

# Load data
adidas_df = read_csv('adidas_items3.csv')

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        className="app-header--title",
        children='Brand Resell Analyst'),
    html.Div(className="dropdownMenu", children=[
        html.Label('Select a graph type:'),
        dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': 'Pricing', 'value': 'bar'},
                {'label': 'Views per category', 'value': 'pie'},
                {'label': 'Items per category', 'value': 'histogram'},
                {'label': 'Views and likes linked to price', 'value': 'scatter'}
            ],
            value='bar',
            searchable=False
        ),
        html.Br(),
    ]),
    html.Div(className="graphs", children=[
        dcc.Graph(id='graph')
    ])
])


@app.callback(
    Output('graph', 'figure'),
    [Input('dropdown', 'value')]
)
def update_graph(dropdown_value):
    if dropdown_value == 'bar':
        return bar_chart(adidas_df.groupby('subcategory'), adidas_df.groupby('subcategory').price.mean(),
                         'Categories', 'Prices', 'Pricing')
    elif dropdown_value == 'pie':
        return pie_chart(adidas_df.subcategory, adidas_df.views,
                         'Views per category')
    elif dropdown_value == 'histogram':
        return histogram(adidas_df.subcategory,
                         'Categories', 'Items per categories')
    elif dropdown_value == 'scatter':
        return scatter_chart(adidas_df, 'interested', 'price', 'subcategory', 'category', 'views',
                             'Price per views', 'Number of Interested people', 'Price')


if __name__ == '__main__':
    app.run_server(debug=True)
