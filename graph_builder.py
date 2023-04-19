from plotly.graph_objects import Figure, Bar, Pie, Histogram
from plotly.express import scatter

# Infile styling
colors = {
    'background': '#161a1d',
    'text': 'rgb(184, 184, 184)',
    'trace1': '#119dff',
}


# Figure Layout
def figure_layout(figure, title, xaxis, yaxis):
    figure.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font=dict(family='Century Gothic'),
        font_color=colors['text'],
        title_x=0.5,
        title_xanchor='center',
        title_y=0.9,
        title_yanchor='top',
        title=title,
        xaxis_title=xaxis,
        yaxis_title=yaxis if yaxis else None,
        margin=dict(l=80, r=80, t=120, b=40),
    )


# Figure Setup
def pie_chart(labels, values, pie_title):  # Generates pie chart
    figure = Figure(
        data=[
            Pie(labels=labels, values=values)
        ],
        layout=dict(title=dict(text=pie_title))
    )
    figure_layout(figure, pie_title, None, None)
    figure.update_traces(  # Pie chart display options
        hoverinfo='label+percent',
        textinfo='label',
        textposition='inside',
        marker=dict(line=dict(color='#000000', width=2))
    )
    return figure


def bar_chart(x, y1, x_name, y_name, bar_title):
    figure = Figure(
        data=(
            Bar(x=x, y=y1, name=x_name, marker_color=colors['trace1']),
        ),
        layout=dict(title=dict(text=bar_title))
    )
    figure_layout(figure, bar_title, x_name, y_name)
    return figure


def histogram(x, x_name, bar_title):
    figure = Figure(
        data=[
            Histogram(x=x, name=x_name, marker_color=colors['trace1']),
        ],
        layout=dict(title=dict(text=bar_title))
    )
    figure_layout(figure, bar_title, x_name, None)
    return figure


def scatter_chart(dataframe, x, y, name, color, size, scatter_title, x_name, y_name):
    figure = scatter(data_frame=dataframe, x=x, y=y, hover_name=name, color=color, size=size, title=scatter_title,
                     size_max=55, log_x=True)
    figure_layout(figure, scatter_title, x_name, y_name)
    return figure

