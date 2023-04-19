from dash import Dash, dcc, html, Input, Output
from pandas import read_csv
from graph_builder import bar_chart, pie_chart, histogram, scatter_chart

# Load data
adidas_df = read_csv('zara_items.csv')

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
            ],
            value='bar',
            searchable=False
        ),
        html.Br(),
    ]),
    html.Div(className="graphs", children=[
        dcc.Graph(id='graph'),
        html.Div([
            dcc.RadioItems(
                [
                    'Category',
                    'Subcategory',
                ],
                value='Subcategory',
                id='selector_radio'
            ),
        ], className='RadioItems'),
        dcc.Graph(
            id='scatter_plot',
            figure=scatter_chart(adidas_df, 'interested', 'price', 'subcategory', 'category', 'views',
                                 'Price linked to number of interested people and views', 'Number of Interested people', 'Price')
        ),
        html.Div([
            html.H2('Dynamic Plot : Choose the information you want to display'),
            html.Div([
                dcc.Dropdown(
                    id='x_axis_selector',
                    options=[
                        {'label': 'Price', 'value': 'Price'},
                        {'label': 'Size', 'value': 'Size'},
                        {'label': 'Condition', 'value': 'Condition'},
                        {'label': 'Views', 'value': 'Views'},
                        {'label': 'Interested', 'value': 'Interested'},
                    ],
                    value='Price',
                    searchable=False
                ),
            ], className='axis_selector_div'),
            html.Div([
                dcc.Dropdown(
                    id='y_axis_selector',
                    options=[
                        {'label': 'Price', 'value': 'Price'},
                        {'label': 'Size', 'value': 'Size'},
                        {'label': 'Condition', 'value': 'Condition'},
                        {'label': 'Views', 'value': 'Views'},
                        {'label': 'Interested', 'value': 'Interested'},
                    ],
                    value='Condition',
                    searchable=False
                ),
            ], className='axis_selector_div'),
            dcc.Graph(id='dynamic_plot')
        ])
    ])
])


@app.callback(
    Output('graph', 'figure'),
    [Input('dropdown', 'value')],
)
def update_graph(dropdown_value, selector_output='Subcategory'):
    if dropdown_value == 'bar':
        return bar_chart(adidas_df.groupby(selector_output.lower()).price.mean().index,
                         adidas_df.groupby(selector_output.lower()).price.mean(),
                         selector_output, 'Prices', 'Pricing per category')
    elif dropdown_value == 'pie':
        return pie_chart(adidas_df[selector_output.lower()], adidas_df.views,
                         'Views per category')
    elif dropdown_value == 'histogram':
        return histogram(adidas_df[selector_output.lower()],
                         selector_output, 'Items per categories')


@app.callback(
    Output('graph', 'figure', allow_duplicate=True),
    Input('selector_radio', 'value'),
    [Input('dropdown', 'value')],
    prevent_initial_call=True
)
def update_selector(selector_radio, dropdown_value):
    if selector_radio == 'Subcategory':
        output = update_graph(dropdown_value, 'Subcategory')
    else:
        output = update_graph(dropdown_value, 'Category')

    return output


@app.callback(
    Output('dynamic_plot', 'figure'),
    [Input('x_axis_selector', 'value'),
        Input('y_axis_selector', 'value')],
    )
def update_dynamic_plot(x_axis, y_axis):
    return scatter_chart(adidas_df, x_axis.lower(), y_axis.lower(), 'subcategory', 'category', 'views',
                         '{} per {}'.format(x_axis, y_axis), x_axis, y_axis)


if __name__ == '__main__':
    app.run_server(debug=True)
