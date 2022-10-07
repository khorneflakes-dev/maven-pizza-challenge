import pandas as pd
from dash import dash, dcc, html, dash_table
import plotly_express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import flask

server = flask.Flask(__name__) # define flask app.server

# Aquí hay algunas preguntas que nos gustaría poder responder:

# ¿Qué días y horas tendemos a estar más ocupados?
# ¿Cuántas pizzas estamos haciendo durante los períodos pico?
# ¿Cuáles son nuestras mejores y peores pizzas vendidas?
# ¿Cuál es nuestro valor promedio de pedido?
# ¿Qué tan bien estamos utilizando nuestra capacidad de asientos? (tenemos 15 mesas y 60 asientos)

# cargando los datasets
df_orders = pd.read_csv('./pizza_sales/orders.csv', delimiter=',')
df_orders_details = pd.read_csv('./pizza_sales/order_details.csv', delimiter=',')
df_pizzas = pd.read_csv('./pizza_sales/pizzas.csv', delimiter=',')
df_pizzas_types = pd.read_csv('./pizza_sales/pizza_types.csv', delimiter=',', encoding='latin1')

# aniadiendo columnas de dia y hora 
df_orders['month'] = pd.to_datetime(df_orders['date']).dt.month_name()
df_orders['day'] = pd.to_datetime(df_orders['date']).dt.day_name()
df_orders['hour'] = pd.to_datetime(df_orders['time']).dt.hour

# concatenando los dataframes necesarios
aux = pd.merge(df_orders_details, df_orders, on='order_id', how='left')
aux2 = pd.merge(aux, df_pizzas, on='pizza_id', how='left')
aux3 = pd.merge(aux2, df_pizzas_types, on='pizza_type_id', how='left')


# dias de la semana mas ocupados
# buscar cual es el promedio de pizzas hechas por dia
agrupado_dias = aux3.groupby(['date', 'day'], as_index=False).agg({'quantity':'sum'})
dias_mas_ocupados = agrupado_dias.groupby(['day'], as_index=False).agg({'date':'count', 'quantity':'sum'})
dias_mas_ocupados['avg'] = round(dias_mas_ocupados['quantity'] / dias_mas_ocupados['date'],0 )


# buscar cual es el promedio de pizzas hechas por hora
# hacer 2 graficas, una para las horas totales y otra para horas segun el dia

# cuales fueron nuestras mejores y peores pizzas segun el criterio de cual fue la mas o menos vendida
# mejores pizzas
mejores_pizzas = aux3.groupby('name', as_index=False).agg({'pizza_id':'count'}).sort_values('pizza_id', ascending=False)
# peores pizzas
peores_pizzas  = aux3.groupby('name', as_index=False).agg({'pizza_id':'count'}).sort_values('pizza_id', ascending=False).tail(5)

# cual es el valor promedio de un pedido, considerando el order_id
aux3['total_price'] = aux3['price'] * aux3['quantity']
valor_promedio = aux3.groupby('order_id', as_index=False).agg({'total_price':'sum'})
valor_promedio_orden = round(valor_promedio['total_price'].mean(),2)

# eficacia del uso de las mesas
# primero armamos una grafica para ver que horas tienen mas ordenes
ordenes_hora = aux3.groupby(['order_id', 'quantity'], as_index=False).agg({'quantity':'sum'})
agrupado_ordenes_hora = ordenes_hora.groupby(['quantity'],as_index=False).agg({'order_id':'count'})

app = dash.Dash(__name__, server=server)

app.title = 'Platos Pizza'

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src='assets/pizzalogo.png', className='pizza-logo'),
            html.Div([
                html.H1("Plato's Pizza", className='title'),
                html.P('Year Performance - 2015', className='subtitle-banner'),
            ], className = 'title-container'),
        ], className='pizza-container'),
        html.Img(src='assets/mavenlogo.png', className='maven-logo'),
    ], className = 'banner'),

    # row 1
    html.Div([

        html.Div([
            
            html.Div([
            dcc.Graph(id='revenue-per-month', figure={}, clickData=None),
            ], className='rpm-graph'),

        ], className='row1-column0'),

        html.Div([

            html.Div([
                dcc.RadioItems(id='dias-aux', value='', className='dias-aux'),

            ], className='row1-column1-row1'),

            html.Div([

                dcc.Graph(id='dias_graph', figure={}, clickData=None)

            ], className='row1-column1-row2')

        ], className='row1-column1'),

        html.Div([
            
            html.P('Total Pizzas Sold', className='pizzas-vendidas-title'),

            html.P(id='pizzas-dia', className='pizzas-dia'),

            html.P(id='pizzas-vendidas', className='pizzas-vendidas-count'),

            html.P('Orders', className='ordenes-vendidas-title'),

            html.P(id='ordenes-vendidas', className='ordenes-vendidas-value'),

            html.P('Revenue', className='revenue'),

            html.P(id='revenue-value', className='revenue-value'),


        ], className='row1-column2'),

        html.Div([

            html.Div([

                dcc.Graph(id='horas-graph', figure={})

            ], className='horas-graph')

        ], className='row1-column3')

    ], className='row1'),

    html.Div([

        html.Div([
            html.P('Average Price per Order', className = 'avg-price-title'),
            html.P(id='precio-promedio-pedido', className = 'avg-price-value')
        ], className = 'row2-column1'),

        html.Div([

            html.P('Best Selling Pizzas', className='tabla1-title'),

            html.Div([

                dcc.Graph(id='tabla1', figure={})
            ])

        ], className = 'row2-column2'),

        html.Div([


        ], className = 'row2-column3')

    ], className='row2'),

    html.Div([

        html.P('explicacion de la distribucion de asientos, el como se hizo',
            className = 'distribution-explain'),

        html.Div([

            dcc.Graph(id='pie-distribution', figure={})
        ], className='row3-column2'),

        html.Div([

            html.P('conclusion del por que de la grafica')

        ], className = 'row3-column3')

    ], className='row3'),

    html.Div([

        html.P('About me', className='about-me'),

        html.Div([

            html.Div([

                html.Img(src='assets/github-logo.png', className='github-logo')

            ], className = 'about-icon-1'),
            
            html.Div([

                html.Img(src='assets/linkedin-logo.png', className = 'linkedin-logo')

            ], className = 'about-icon-2')

        ], className='about-icons')

    ])

], className = 'main-container')

# titulo de semana o dia
@app.callback(
    Output('pizzas-dia', component_property='children'),
    [Input('dias_graph', component_property='clickData')]
)

def pizzas_title(clk_data):
    if clk_data == None:
        return 'During the Week'
    else:
        clk = clk_data['points'][0]['x']
        return clk

# cantidad de ordenes realizadas
@app.callback(
    Output('ordenes-vendidas', component_property='children'),
    [Input('dias_graph', component_property='clickData')]
)

def orders(clk_data):
    if clk_data == None:
        value = aux3['order_id'].count()
        return f'{value:,.0f}'
    else:
        clk = clk_data['points'][0]['x']
        value = aux3[aux3['day']==clk]['order_id'].count()
        return f'{value:,.0f}'

# total de ingresos en la semana o el dia 
@app.callback(
    Output('revenue-value', component_property='children'),
    [Input('dias_graph', component_property='clickData')]
)

def revenue(clk_data):
    if clk_data == None:
        rev = aux3['total_price'].sum()
        return f'$ {rev:,.0f}'
    else:
        clk = clk_data['points'][0]['x']
        rev = aux3[aux3['day']==clk]['total_price'].sum()
        return f'$ {rev:,.0f}'

# cantidad de pizzas vendidas en la semana o en un dia
@app.callback(
    Output('pizzas-vendidas', component_property='children'),
    [Input('dias_graph', component_property='clickData')]
)

def pizzas_sold(clk_data):
    if clk_data == None:
        cantidad_vendida = aux3['quantity'].sum()
        return f'{cantidad_vendida:,.0f} Pizzas'
    else:
        clk = clk_data['points'][0]['x']
        cantidad_vendida = aux3[aux3['day']==clk]['quantity'].sum()
        return f'{cantidad_vendida:,.0f} Pizzas'
        
# primera grafica de los dias con mas ventas
@app.callback(
    Output('dias_graph', component_property='figure'),
    [Input('dias-aux', component_property='value')],
    [Input('dias_graph', component_property='clickData')]
)

def graph_dias(value, clk_data):
    dias_mas_ocupados.columns = ['Day','Date','Quantity', 'Average']
    dias_graph = dias_mas_ocupados.sort_values(['Average'], ascending=False)
    
    colors = ['#CFA22E']*7
    if clk_data != None:
        clk = clk_data['points'][0]['x']
        list_dias = dias_graph['Day'].tolist()
        colors[list_dias.index(clk)] = '#252525'
    
    data_graph = [go.Bar(
            x = dias_graph['Day'],
            y = dias_graph['Average'],
            orientation='v',
            marker_color=colors,
            
            )]
    layout = go.Layout(
    margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin
        t=100, #top margin
        ))
    fig = go.Figure(data=data_graph, layout=layout)
    fig.update_layout({
        'plot_bgcolor': 'rgba(1, 1, 1, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'xaxis_title': '<b>Weekdays</b>',
        'yaxis_title': 'Average Pizzas Sold',
        'font_family': 'Lato',
        'font_color': 'white',
        'title_text': 'Busiest Days',
        'title_font_size': 30,
        'title_xanchor': 'center',
        'title_yanchor': 'top',
        'title_x': 0.5,
        'title_y': 0.9,
        })
    fig.update_xaxes(tickfont_size=20, title_font={'size': 20})
    fig.update_yaxes(tickfont_size=20, title_font={'size': 20})

    return fig


@app.callback(
    Output('horas-graph', component_property='figure'),
    [Input('dias_graph', component_property='clickData')]
)

def graph_horas(clk_data):
    if clk_data == None:
        # grafica 1
        agrupado_horas = aux3.groupby(['date', 'hour'], as_index=False).agg({'quantity':'sum'}).sort_values('quantity', ascending=False)
        horas_mas_ocupadas = agrupado_horas.groupby(['hour'], as_index=False).agg({'date':'count', 'quantity':'sum'})
        horas_mas_ocupadas['avg'] = round(horas_mas_ocupadas['quantity'] / horas_mas_ocupadas['date'],0)

        fig2 = go.Figure(
            {
                'data': [
                    {
                        'x': horas_mas_ocupadas['hour'],
                        'y': horas_mas_ocupadas['avg'],
                        'mode': 'lines',
                        'line': {'color': '#CFA22E'},
                        'stackgroup': 'one'
                    }
                ],

                'layout': {

                    'xaxis': dict(
                            showline=False,
                            showgrid=False,
                            zeroline=False,
                            showticklabels=True
                    ),
                    'yaxis': dict(
                            showline=False,
                            showgrid=True,
                            zeroline=False,
                            showticklabels=True
                    ),
                    'xaxis_title': '<b>Hours</b>',
                    'yaxis_title': 'Average  Pizzas  Sold',
                    'margin': go.layout.Margin(
                        l=0, #left margin
                        r=0, #right margin
                        b=0, #bottom margin
                        t=100, #top margin
                        )
                },

                'traces': {
                    'line_shape': 'spline'
                }
            }
        )
        fig2.update_layout({
            'plot_bgcolor': 'rgba(1, 1, 1, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font_family': 'Lato',
            'font_color': 'white',
            'title_text': 'Busiest Hours',
            'title_font_size': 30,
            'title_xanchor': 'center',
            'title_yanchor': 'top',
            'title_x': 0.5,
            'title_y': 0.9,
            })

        fig2.update_xaxes(tickfont_size=15, title_font={'size': 20})
        fig2.update_yaxes(tickfont_size=20, title_font={'size': 20})



        return fig2
    else:
        clk = clk_data['points'][0]['x']
        agrupado_horas = aux3[aux3['day']==clk].groupby(['date', 'hour'], as_index=False).agg({'quantity':'sum'}).sort_values('quantity', ascending=False)
        horas_mas_ocupadas = agrupado_horas.groupby(['hour'], as_index=False).agg({'date':'count', 'quantity':'sum'})
        horas_mas_ocupadas['avg'] = round(horas_mas_ocupadas['quantity'] / horas_mas_ocupadas['date'],0)

    fig2 = go.Figure(
            {
                'data': [
                    {
                        'x': horas_mas_ocupadas['hour'],
                        'y': horas_mas_ocupadas['avg'],
                        'mode': 'lines',
                        'line': {'color': '#CFA22E'},
                        'stackgroup': 'one'
                    }
                ],

                'layout': {

                    'xaxis': dict(
                            showline=False,
                            showgrid=False,
                            zeroline=False,
                            showticklabels=True
                    ),
                    'yaxis': dict(
                            showline=False,
                            showgrid=True,
                            zeroline=False,
                            showticklabels=True
                    ),
                    'xaxis_title': '<b>Hours</b>',
                    'yaxis_title': 'Average  Pizzas  Sold',
                    'margin': go.layout.Margin(
                        l=0, #left margin
                        r=0, #right margin
                        b=0, #bottom margin
                        t=100, #top margin
                        )
                },

                'traces': {
                    'line_shape': 'spline'
                }
            }
        )
    fig2.update_layout({
            'plot_bgcolor': 'rgba(1, 1, 1, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font_family': 'Lato',
            'font_color': 'white',
            'title_text': 'Busiest Hours',
            'title_font_size': 30,
            'title_xanchor': 'center',
            'title_yanchor': 'top',
            'title_x': 0.5,
            'title_y': 0.9,
            })
    fig2.update_xaxes(tickfont_size=20, title_font={'size': 20})
    fig2.update_yaxes(tickfont_size=20, title_font={'size': 20})



    return fig2


# tabla de las pizzas mas vendidas por semana y por dia
@app.callback(
    Output('tabla1', component_property='figure'),
    [Input('dias_graph', component_property='clickData')]
)

def best_selling(clk_data):
    
    fig = go.Figure(

        data = [
            
            go.Table(
                
                header = dict(values=['Name', 'Quantity_Sold']),

                cells = dict(values=[mejores_pizzas['name'], mejores_pizzas['pizza_id']])
            )
        ]
    )
    return fig

# ingresos por mes
@app.callback(
    Output('revenue-per-month', component_property='figure'),
    [Input('dias-aux', component_property='value')],
    [Input('dias-aux', component_property='value')]
)

def revenue_per_month(value, value2):
    data = aux3.groupby(['month'], as_index=False).agg({'total_price': 'sum'})
    data = data.sort_values(['total_price'], ascending=True)
    data_graph = [go.Bar(
        y = data['month'],
        x = data['total_price'],
        orientation='h',
        marker_color=['#CFA22E']*len(data),
        
        )]
    layout = go.Layout(
        margin=go.layout.Margin(
            l=0, #left margin
            r=0, #right margin
            b=0, #bottom margin
            t=100, #top margin
        ))
    fig = go.Figure(data=data_graph, layout=layout)
    fig.update_layout({
        'plot_bgcolor': 'rgba(1, 1, 1, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'xaxis_title': '<b>Total Sold</b>',
        'font_family': 'Lato',
        'font_color': 'white',
        'title_text': 'Revenue per Month',
        'title_font_size': 30,
        'title_xanchor': 'center',
        'title_yanchor': 'top',
        'title_x': 0.5,
        'title_y': 0.9,
    })
    fig.update_xaxes(tickfont_size=20, title_font={'size': 20})
    return fig












































if __name__ == ('__main__'):
    app.run_server(debug=True)