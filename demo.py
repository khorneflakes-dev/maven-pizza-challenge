import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# # grafica 1
# agrupado_horas = aux3.groupby(['date', 'hour'], as_index=False).agg({'quantity':'sum'}).sort_values('quantity', ascending=False)
# horas_mas_ocupadas = agrupado_horas.groupby(['hour'], as_index=False).agg({'date':'count', 'quantity':'sum'})
# horas_mas_ocupadas['avg'] = round(horas_mas_ocupadas['quantity'] / horas_mas_ocupadas['date'],0)

# grafica 2
agrupado_horas = aux3[aux3['day']=='Sunday'].groupby(['date', 'hour'], as_index=False).agg({'quantity':'sum'}).sort_values('quantity', ascending=False)
horas_mas_ocupadas = agrupado_horas.groupby(['hour'], as_index=False).agg({'date':'count', 'quantity':'sum'})
horas_mas_ocupadas['avg'] = round(horas_mas_ocupadas['quantity'] / horas_mas_ocupadas['date'],0)


# cuales fueron nuestras mejores y peores pizzas segun el criterio de cual fue la mas o menos vendida
# mejores pizzas
mejores_pizzas = aux3.groupby('name', as_index=False).agg({'pizza_id':'count'}).sort_values('pizza_id', ascending=False).head(5)
# peores pizzas
peores_pizzas  = aux3.groupby('name', as_index=False).agg({'pizza_id':'count'}).sort_values('pizza_id', ascending=False).tail(5)

# cual es el valor promedio de un pedido, considerando el order_id
aux3['total_price'] = aux3['price'] * aux3['quantity']
valor_promedio = aux3.groupby('order_id', as_index=False).agg({'total_price':'sum'})
valor_promedio_orden = round(valor_promedio['total_price'].mean(),2)

# eficacia del uso de las mesas
# primero armamos una grafica para ver que horas tienen mas ordenes
ordenes_hora = aux3.groupby(['order_id', 'quantity', 'hour'], as_index=False).agg({'quantity':'sum'})
agrupado_ordenes_hora = ordenes_hora.groupby(['hour','quantity'],as_index=False).agg({'order_id':'count'})
agrupado_ordenes_hora['description'] = agrupado_ordenes_hora['quantity'].apply(lambda x: 'between 1 and 2' if x < 3 else 'greater than 3')

demo = agrupado_ordenes_hora.groupby(['quantity'], as_index=False).agg({'order_id':'sum'})

demo['description'] = demo['quantity'].apply(lambda x: 'between 1 and 2' if x < 3 else 'greater than 3')
demo['percentage'] = demo['order_id'] / demo['order_id'].sum()
demo_group = demo.groupby(['description'], as_index=False).agg({'percentage':'sum'})
agrupado_ordenes_hora2 =agrupado_ordenes_hora.groupby(['hour','description'], as_index=False).agg({'order_id':'sum'})
# fig = px.pie(demo, values='order_id', names='description')

# fig.show()


# fig2 = px.bar(agrupado_ordenes_hora2.sort_values('description'), x='hour', y='order_id', color='description', barmode='group')
# fig2.update_traces(width=0.4)
# fig2.update_layout(
#     xaxis = dict(
        
#         tick0 = 0,
#         dtick = 1
#     )
# )
# fig2.show()

# df = px.data.tips()
# # fig = px.histogram(df, x="sex", y="total_bill",
# #              color='smoker', barmode='group',
# #              histfunc='avg',
# #              height=400)
# # fig.show()
# print(df)
# print(agrupado_ordenes_hora.groupby(['hour','description'], as_index=False).agg({'order_id':'sum'}))

pizza_size = aux3.groupby(['size'], as_index=False).agg({'quantity':'sum'})
print(pizza_size)

# fig = go.Figure(data=go.Scatterpolar(
#   r=pizza_size['quantity'].tolist(),
#   theta=pizza_size['size'].tolist(),
#   fill='toself'
# ))

# fig.update_layout(
#   polar=dict(
#     radialaxis=dict(
#       visible=True
#     ),
#   ),
#   showlegend=False
# )

# fig.show()


# pizza_size = pizza_size.sort_values('quantity', ascending=False)

# fig = go.Figure(go.Funnel(
#     y = pizza_size['size'].tolist(),
#     x = pizza_size['quantity'].tolist()))

# fig.show()

fig = px.pie(pizza_size, values='quantity', names='size')

fig.show()

# cantidad_vendidas = aux3.groupby(['name'], as_index=False).agg({'total_price':'sum'}).sort_values('total_price', ascending=False)

# print(cantidad_vendidas)