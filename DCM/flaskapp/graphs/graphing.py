"""
Graphing Library
-------------------------
A collection of graphiung functions 
used by the app to generate both data
points to be rendered live, as well as
publish a graphs history to a csv file.
"""

import os, inspect, sys, multiprocessing, time, json, csv, datetime

import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_pdf import PdfPages
from time import time
from random import random
from math import sin, cos

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

from config.config_manager import Config

style.use('fivethirtyeight')

current_time_milli = lambda: int(round(time() * 1000))

__data = []
__start = current_time_milli()

def set_start_time():
    """set_start_time Sets the start time for the graph

    Called when starting a new graph, will reset the running
    timer allowing the new graph to start at the zero value.
    """
    __start = current_time_milli()

def update_data():
    """update_data Returns a new data point for the graph

    Called to request a new data point for the live graph.
    Will return a list of lists, each internal list containing
    a point with a timestamp (x-value) and parameter value (y-value).
    The timestamp is determined by the time difference between 'now' and
    when the set_start_time() function was last called.

    :return: A list of lists containing a new point to be added to each line being rendered by the live graph
    :rtype: list
    """
    values = temp_serial_placeholder()
    time = current_time_milli() - __start
    points = [ [time, values[0]], [time, values[1]] ]
    __data.append(points)
    return points

def publish_data(username):
    """publish_data Publishes the current (or most recent) live graphs data to a csv file

    Will generate a csv file containing all the data from when the current (or most recent)
    graph was started.
    """
    x1 = []
    x2 = []
    y1 = []
    y2 = []

    for point_set in __data:
        x1.append(point_set[0][0])
        y1.append(point_set[0][1])

        x2.append(point_set[1][0])
        y2.append(point_set[1][1])

    figure = plt.figure()
    plt.plot(x1, y1, label='Atrium')
    plt.plot(x2, y2, label='Ventrical')
    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (V)')
    plt.title("'{0}' Live Egram Data".format(username))
    plt.legend()

    timestamp = datetime.datetime.now().strftime(Config.getInstance().get('Database', 'db.timestamp')).replace(' ', '_').replace('/', '-').replace(':', '-')
    graph_doc_name = "{0}_Live_Egram_Data_From_{1}.pdf".format(username, timestamp)
    pp = PdfPages(os.path.join(parentfolder, 'downloads', graph_doc_name))
    pp.savefig(figure)
    pp.close()

    csv_output = list(zip(x1, y1, x2, y2))

    csv_doc_name = "{0}_Live_Egram_Data_From_{1}.csv".format(username, timestamp)
    with open(os.path.join(parentfolder, 'downloads', csv_doc_name), 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Atrium Timestamp', 'Atrium Value', 'Ventrical Timestamp', 'Ventrical Value'])
        for line in csv_output:
            writer.writerow(line)

def temp_serial_placeholder():
    """temp_serial_placeholder Placeholder for serial functionality

    Generates a sine and cosine point output to be rendered to the 
    live graphs to test their functionality without relying on the 
    serial communications.

    :return: A list containing a sine and cosine point in this format [ sine(current_time), cos(current_time)]
    :rtype: list
    """
    return [sin(current_time_milli()/1000), cos(current_time_milli()/1000)]