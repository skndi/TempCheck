import pandas as pd
from db import database
from util import get_up_to_date, Period
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_image_bytes(period: Period):
    up_to = pd.Timestamp(get_up_to_date(period))

    sensor_data_df = pd.read_sql_table(
        'sensor_data',
        con=database.engine,
        parse_dates=["timestamp"]
    )

    filter_mask = sensor_data_df['timestamp'] > up_to
    df = sensor_data_df[filter_mask]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['temperature'], name="Temperature", marker=dict(color="darksalmon")),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['humidity'], name="Humidity", marker=dict(color="purple")),
        secondary_y=True,
    )

    fig.update_layout(
        title_text="Temperature and humidity"
    )

    fig.update_xaxes(title_text="Timestamp")

    fig.update_yaxes(title_text="Temperature", secondary_y=False)
    fig.update_yaxes(title_text="Humidity", secondary_y=True)

    return fig.to_image(format="png")
