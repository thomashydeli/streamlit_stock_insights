import pandas as pd
import streamlit as st
from pandasql import sqldf
from plotly import graph_objects as go
from utils.mapper import sql_date_trunc
from utils.data_processor import get_data

# TO-DO:
# 2023-09-10: basic functionality - data processors, candlestick plots
data_origin=get_data()

def main():
    st.set_page_config(layout="wide")
    st.title('Metric Delivery')

    # two columns, left columns for inputs, right columns for rendering
    input_col, viz_col=st.columns([2,5])

    # input column takes in: SQL query, metric name, dimension for root cause, granularity, and forecasting range
    with input_col:
        st.write('Metric Configurations:')
        sql_query = st.text_area(
            'Query:', 
            value="""SELECT 
    Date AS date, 
    ticker, 
    "Adj Close" AS value 
FROM data_origin""",
            height=300, 
            key='sql_query', 
            help='make sure your query has date and value columns corresponding to datestamp and value of the metric'
        )

        metric_name = st.text_input('Metric Name:', value='my metric',key='metric_name', help='customize name of the metric')
        dimension = st.text_input('Dimension:', value='ticker', key='dimension', help='dimension for breakingdown visualizations and root cause analyses')
        granularity = st.text_input('Granularity:', value='week', key='granularity', help='granularity for aggregation, please fill week, month, quarter')
        dim_aggregations = st.text_input('Dimension Aggregation:', value='sum', key='dimension aggregations', help='ways of aggregating dimensions, please fill avg, sum, p50, p75, p95')
        time_aggregation = st.text_input('Time Aggregation:', value='avg', key='time aggregation', help='ways of aggregating time, please fill avg, sum, p50, p75, p95')
        range_forecasts = st.text_input('Days of Forecasts:', key='forecasting_days', help='how many days to the future to forecast')
        raw_data = sqldf(sql_query)
        granularity_truncker = sql_date_trunc[granularity]
        agg_across_dims=sqldf(
            f"""SELECT
    date,
    {dim_aggregations}(value) AS value
FROM raw_data
GROUP BY 1
ORDER BY 1"""
        )
        agg_data=sqldf(
            f"""WITH RankedData AS (SELECT
    date({granularity_truncker}) AS ds,
    value,
    ROW_NUMBER() OVER(PARTITION BY DATE({granularity_truncker}) ORDER BY date ASC) AS rn_asc,
    ROW_NUMBER() OVER(PARTITION BY DATE({granularity_truncker}) ORDER BY date DESC) AS rn_desc
FROM agg_across_dims
)
            
SELECT
    ds,
    {time_aggregation}(value) AS y,
    MIN(value) AS Low,
    MAX(value) AS High,
    MAX(CASE WHEN rn_asc=1 THEN value END) AS Open,
    MAX(CASE WHEN rn_desc=1 THEN value END) AS Close
FROM RankedData
GROUP BY 1
ORDER BY 1"""
        )
        print(agg_data.head())

    # visualization columns to offer the functionality of
    # line charts, candlestick plots, changepoints and anomalies, and forecasting
    with viz_col:

        if metric_name:
            st.write(f'Visualizations of {metric_name}:')

            col_candlestick, col_anomaly, col_change_point, col_forecasting = st.columns(4)
            with col_candlestick: candlestick=st.checkbox('Candlestick')
            with col_anomaly: anomaly=st.checkbox('Anomaly')
            with col_change_point: change_point=st.checkbox('Change Point')
            with col_forecasting: forecasting=st.checkbox('Forecasting')

            # basic line chart:
            fig=go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=pd.to_datetime(agg_data.ds.values),
                    y=agg_data.y.values,
                    name=metric_name
                )
            )

            if candlestick:
                fig.add_trace(
                    go.Candlestick(
                        x=pd.to_datetime(agg_data.ds.values),
                        open=agg_data['Open'],
                        high=agg_data['High'],
                        low=agg_data['Low'],
                        close=agg_data['Close'],
                        name='Candle Stick'
                    )
                )

            st.plotly_chart(fig)


if __name__=='__main__':
    main()