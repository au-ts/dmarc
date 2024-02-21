#! /usr/bin/env python3
# Derived from code at
# https://www.c-sharpcorner.com/article/how-to-build-a-dmarc-report-dashboard-with-python/
#
import os
import xml.etree.ElementTree as ET
import pandas as pd
import dash
from datetime import datetime
from dash import dcc
from dash import html
import matplotlib.pyplot as plt
import plotly.express as px
from dash.dependencies import Input, Output
report_dir = "/var/cache/dmarc"

app = dash.Dash(__name__)


def timestamp_to_datetime(timestamp):
    """
    Converts a UNIX/DMARC timestamp to a Python ``datetime`` object

    Args:
        timestamp (int): The timestamp

    Returns:
        datetime: The converted timestamp as a Python ``datetime`` object
    """
    return datetime.fromtimestamp(int(timestamp))


def timestamp_to_human(timestamp):
    """
    Converts a UNIX/DMARC timestamp to a human-readable string

    Args:
        timestamp: The timestamp

    Returns:
        str: The converted timestamp in ``YYYY-MM-DD HH:MM:SS`` format
    """
    return timestamp_to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S")



# Function to parse DMARC report
def parse_dmarc_report(report_xml):
    ret = []
    root = ET.fromstring(report_xml)
    Date = timestamp_to_human(root.find(".//date_range/begin").text) + "--" + timestamp_to_human(root.find(".//date_range/end").text),
    for report in root.findall('record'):
        ret.append({
            "Source IP": report.find(".//row/source_ip").text,
            "Count": int(report.find(".//row/count").text),
            "Date": Date,
            "SPF Result": report.find(".//row/policy_evaluated/spf").text,
            "DKIM Result": report.find(".//row/policy_evaluated/dkim").text,
            "DMARC Result": report.find(".//row/policy_evaluated/disposition").text
            })
    return ret

# Function to process DMARC reports
def process_dmarc_reports(report_dir):
    data = []

    for filename in os.listdir(report_dir):
        if filename.endswith(".xml"):
            with open(os.path.join(report_dir, filename), "r") as report_file:
                report_xml = report_file.read()
                parsed_data = parse_dmarc_report(report_xml)
                data = data + parsed_data

    df = pd.DataFrame(sorted(data, key=lambda record: record["Date"]))
    return df

# Process the DMARC reports
df = process_dmarc_reports(report_dir)

# Create a pie chart for pass vs. fail percentages
def create_pass_fail_pie_chart():
    dmarc_result_counts = df["DMARC Result"].value_counts()
    pass_fail_counts = dmarc_result_counts.get("none", 0), dmarc_result_counts.get("quarantine", 0)

    labels = ['Pass', 'Fail']
    print("Pass %d, Fail %d\n" % pass_fail_counts)
    fig = px.pie(names=labels, values=pass_fail_counts, title='DMARC Pass vs. Fail')
    return fig

# Define the layout for the Dash app
app.layout = html.Div([
    html.H1("DMARC Report Dashboard"),

    # Display the table-like graphical output
    html.Div([
        dcc.Graph(
            id='dmarc-table',
            config={'displayModeBar': False},
            figure={
                'data': [
                    {
                        'type': 'table',
                        'header': {
                            'values': df.columns,
                            'fill': {'color': '#f2f2f2'},
                            'align': 'center',
                            'font': {'size': 14}
                        },
                        'cells': {
                            'values': df.values.T,
                            'align': 'center',
                            'font': {'size': 12}
                        }
                    }
                ],
                'layout': {'autosize': True}
            }
        )
    ]),

    # Display the DMARC pass vs. fail pie chart
    html.Div([
        dcc.Graph(figure=create_pass_fail_pie_chart(), id='dmarc-pie-chart')
    ])
])

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0",
                   port=5002)

