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

# concatenando los dataframes necesarios
aux = pd.merge(df_orders_details, df_orders, on='order_id', how='left')
aux2 = pd.merge(aux, df_pizzas, on='pizza_id', how='left')
aux3 = pd.merge(aux2, df_pizzas_types, on='pizza_type_id', how='left')


# dias de la semana mas ocupados

# buscar cual es el promedio de pizzas hechas por dia
agrupado_dias = aux3.groupby(['date', 'day'], as_index=False).agg({'quantity':'sum'})
dias_mas_ocupados = agrupado_dias.groupby(['day'], as_index=False).agg({'date':'count', 'quantity':'sum'})
dias_mas_ocupados['avg'] = round(dias_mas_ocupados['quantity'] / dias_mas_ocupados['date'],0 )

# grafica
# fig = px.bar(dias_mas_ocupados.sort_values('avg', ascending=True), y='avg', x='day', orientation='v')
# fig.show()


# hacer 2 graficas, una para las horas totales y otra para horas segun el dia

# grafica 1
agrupado_horas = aux3.groupby(['date', 'hour'], as_index=False).agg({'quantity':'sum'}).sort_values('quantity', ascending=False)
horas_mas_ocupadas = agrupado_horas.groupby(['hour'], as_index=False).agg({'date':'count', 'quantity':'sum'})
horas_mas_ocupadas['avg'] = round(horas_mas_ocupadas['quantity'] / horas_mas_ocupadas['date'],0)

# grafica 2
# agrupado_horas = aux3[aux3['day']=='Sunday'].groupby(['date', 'hour'], as_index=False).agg({'quantity':'sum'}).sort_values('quantity', ascending=False)
# horas_mas_ocupadas = agrupado_horas.groupby(['hour'], as_index=False).agg({'date':'count', 'quantity':'sum'})
# horas_mas_ocupadas['avg'] = round(horas_mas_ocupadas['quantity'] / horas_mas_ocupadas['date'],0)

# fig2 = px.bar(agrupado_horas.head(10), x='hour', y='quantity')
# fig2.show()
print(horas_mas_ocupadas)

# cuales fueron nuestras mejores y peores pizzas segun el criterio de cual fue la mas o menos vendida
# mejores pizzas
mejores_pizzas = aux3.groupby('name', as_index=False).agg({'pizza_id':'count'}).sort_values('pizza_id', ascending=False).head(5)
mejores_pizzas.columns = ['Pizza Name', 'Quantity Sold']
# peores pizzas
peores_pizzas  = aux3.groupby('name', as_index=False).agg({'pizza_id':'count'}).sort_values('pizza_id', ascending=False).tail(5)
peores_pizzas.columns = ['Pizza Name', 'Quantity Sold']


# cual es el valor promedio de un pedido, considerando el order_id
aux3['total_price'] = aux3['price'] * aux3['quantity']
valor_promedio = aux3.groupby('order_id', as_index=False).agg({'total_price':'sum'})
valor_promedio_orden = round(valor_promedio['total_price'].mean(),2)

# eficacia del uso de las mesas
# primero armamos una grafica para ver que horas tienen mas ordenes
ordenes_hora = aux3.groupby(['order_id', 'quantity'], as_index=False).agg({'quantity':'sum'})
agrupado_ordenes_hora = ordenes_hora.groupby(['quantity'],as_index=False).agg({'order_id':'count'})

agrupado_ordenes_hora['categorizado'] = agrupado_ordenes_hora['quantity'].apply(lambda x: 'Between 1 and 2' if x < 3 else 'Greater than or equal to 3')
agrupado_ordenes_hora['porcentaje'] = round(agrupado_ordenes_hora['order_id'] / agrupado_ordenes_hora['order_id'].sum() * 100, 2)

categorizado = (agrupado_ordenes_hora.groupby(['categorizado'])['porcentaje'].sum())
# nuestro modelo de organizacion de asientos entre las 15 mesas tiene una efectividad de 1/3,
# ya que 2/3 de las ordenes se componene de 1 a 2 pizzas y solo el restante estarua usando el total de asientos de una mesa
# grafica de pie
