import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportRequest, Dimension, Metric, OrderBy, DateRange
from datetime import date, timedelta
import os

# Configurar credenciales
property_id = ""
json_cred = ""
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_cred
client = BetaAnalyticsDataClient()

# Función para formatear el reporte
def format_report(request):
    response = client.run_report(request)
    
    row_index_names = [header.name for header in response.dimension_headers]
    row_header = []
    for i in range(len(row_index_names)):
        row_header.append([row.dimension_values[i].value for row in response.rows])

    row_index_named = pd.MultiIndex.from_arrays(np.array(row_header), names=np.array(row_index_names))
    
    metric_names = [header.name for header in response.metric_headers]
    data_values = []
    for i in range(len(metric_names)):
        data_values.append([row.metric_values[i].value for row in response.rows])

    output = pd.DataFrame(data=np.transpose(np.array(data_values, dtype='f')), index=row_index_named, columns=metric_names)
    return output

# Función para calcular la fecha de inicio
def calc_start_date(end_date, no_days):
    if end_date == "today":
        start_date = date.today() - timedelta(days=no_days)
    else:
        start_date = end_date - timedelta(days=no_days)  # end_date ya es objeto date
    return start_date.strftime("%Y-%m-%d") 

# Función principal para generar el reporte
def produce_report(end_date, no_days, property_id=property_id, client=client, metric="activeUsers"):
    daily_traffic_request = RunReportRequest(
            property='properties/'+property_id,
            dimensions=[Dimension(name="date"), Dimension(name="sessionMedium")],
            metrics=[Metric(name=metric)],
            order_bys=[OrderBy(dimension={'dimension_name': 'date'}), OrderBy(dimension={'dimension_name': 'sessionMedium'})],
            date_ranges=[DateRange(start_date=calc_start_date(end_date, no_days), end_date=end_date.strftime("%Y-%m-%d"))]  # Convertir end_date a string
        )

    daily_traffic = format_report(daily_traffic_request).reset_index()
    active_users_pivot = pd.pivot_table(daily_traffic, 
                                     columns=['sessionMedium'], 
                                     index=['date'], 
                                     values=[metric], 
                                     aggfunc='sum',
                                     fill_value=0).droplevel(0, axis=1)
    daily_traffic['date'] = pd.to_datetime(daily_traffic['date'], errors='coerce').dt.strftime('%Y-%m-%d')

    active_users_pivot.index = active_users_pivot.index.str.slice(start=4)

    # Gráfico de torta (Pie chart) con Plotly
    pie_data = daily_traffic.groupby('sessionMedium', as_index=False)[metric].sum().sort_values(by=metric, ascending=False)
    pie_chart = px.pie(pie_data, names='sessionMedium', values=metric, title=f'{metric.capitalize()} by Medium')

    # Gráfico de líneas (Line chart) con Plotly
    line_chart = go.Figure()
    for column in active_users_pivot.columns:
        line_chart.add_trace(go.Scatter(x=active_users_pivot.index, y=active_users_pivot[column],
                                        mode='lines', name=column))
    line_chart.update_layout(title=f'{metric.capitalize()} by Day', xaxis_title='Date', yaxis_title=metric)

    # Mostrar gráficos en Streamlit
    st.plotly_chart(pie_chart)
    st.plotly_chart(line_chart)

# Interacción con el usuario en Streamlit
st.title("Google Analytics Data Report")

# Selección de fecha por el usuario
end_date = st.date_input("Select End Date", value=date.today())  # end_date es un objeto date
no_days = st.slider("Select the number of days", 30, 365, value=90)

# Selección de la métrica
metric = st.selectbox("Select Metric", ["activeUsers", "sessions", "newUsers"])

# Botón para generar el reporte
if st.button("Generate Report"):
    produce_report(end_date, no_days, metric=metric)
