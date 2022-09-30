import pandas as pd
import plotly.express as px

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
df_orders['day'] = pd.to_datetime(df_orders['date']).dt.day_name()
df_orders['hour'] = pd.to_datetime(df_orders['time']).dt.hour

# agrupando df_orders para mostrar los dias mas ocupados y las horas mas ocupadas
# monday, tuesday ... 0, 1, ...
dias_ocupados = df_orders.groupby('day', as_index=False).agg({'order_id':'count'})
horas_ocupadas = df_orders.groupby('hour', as_index=False).agg({'order_id':'count'})

# estas graficas muestran cuantas pizzas estamos haciendo durante cada uno de las horas
# fig = px.bar(dias_ocupados, x='day', y='order_id')

# buscamos nuestras mejores y peores pizzas vendidas
# el criterio usado es que es mejor la mas vendida y peor la menos vendida

pizzas_aux = pd.merge(df_orders_details, df_pizzas, left_on='pizza_id', right_on='pizza_id', how='left')
pizzas_aux2 = pd.merge(pizzas_aux, df_pizzas_types, left_on='pizza_type_id', right_on='pizza_type_id', how='left')
mas_vendida = pizzas_aux2.groupby('name', as_index=False).agg({'quantity':'sum'})

# fig3 = px.pie(values=[mas_vendida.max().values[1], mas_vendida.min().values[1]],
#               names=[mas_vendida.max().values[0], mas_vendida.min().values[0]])
# fig3.show()

# buscamos cual es el valor promedio de un pedido

pizzas_aux2['order_price'] = pizzas_aux2['quantity'] * pizzas_aux2['price']
valor_promedio = pizzas_aux2.groupby('order_id', as_index=False).agg({'order_price':'sum'})
valor_promedio_pedido = valor_promedio['order_price'].mean()

# print(pizzas_aux2.groupby(['order_id'], as_index=False).agg({'order_price':'sum'}))
capacidad = pd.merge(df_orders_details, df_orders, left_on='order_id', right_on='order_id', how='left')
# demo = capacidad.groupby(['hour','order_id','quantity'], as_index=False)
demo = capacidad.sort_values(['hour','order_id'])
# demo['aux'] = demo['quantity'] / demo['order_id']

demo2 = (demo[['hour', 'order_id', 'order_details_id']])

demo3 = (demo2.groupby(['hour', 'order_id'], as_index=False).agg({'order_details_id':'count'}))

demo4 = (demo3.groupby(['hour'], as_index=False).agg({'order_id':'count', 'order_details_id':'sum'}))
demo4['avg'] = demo4['order_id'] / 15

print(demo4)
