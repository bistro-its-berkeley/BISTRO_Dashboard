import pdb

import glob
import math
from os import listdir, makedirs
from os.path import dirname, isdir, join
import pandas as pd
import yaml

from bokeh.core.properties import value
from bokeh.io import curdoc, show, output_file, export_png, export_svgs
from bokeh.layouts import row, column, gridplot, layout, widgetbox
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, DataRange1d, LabelSet, Legend, LinearColorMapper, Select, Title
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.models.widgets import CheckboxButtonGroup, Div, Panel, Tabs
from bokeh.palettes import Dark2, Category10, Category20, Plasma256, YlOrRd
from bokeh.plotting import figure, show
from bokeh.transform import dodge, transform

from submission import Submission
from db_loader import BistroDB


HOURS = [str(h) for h in range(24)]
#ROUTE_IDS = ['1340', '1341', '1342', '1343', '1344', '1345', '1346', '1347', '1348', '1349', '1350', '1351']

BUSES_LIST = ['BUS-DEFAULT', 'BUS-SMALL-HD', 'BUS-STD-HD', 'BUS-STD-ART']
MODES = ['ride_hail', 'car', 'drive_transit', 'walk', 'walk_transit']#, 'mixed_mode']

SOURCE_NAME_DATA_PAIR = [
('normalized_scores_source', 'normalized_scores_data'),
('fleetmix_input_source', 'fleetmix_input_data'),
('routesched_input_line_source', 'routesched_input_line_data'),
('routesched_input_start_source', 'routesched_input_start_data'),
('routesched_input_end_source', 'routesched_input_end_data'),
('fares_input_source', 'fares_input_data'),
('modeinc_input_source', 'modeinc_input_data'),
('mode_planned_pie_chart_source', 'mode_planned_pie_chart_data'),
('mode_realized_pie_chart_source', 'mode_realized_pie_chart_data'),
('mode_choice_by_time_source', 'mode_choice_by_time_data'),
('mode_choice_by_income_group_source', 'mode_choice_by_income_group_data'),
('mode_choice_by_age_group_source', 'mode_choice_by_age_group_data'),
('mode_choice_by_distance_source', 'mode_choice_by_distance_data'),
('congestion_travel_time_by_mode_source',
    'congestion_travel_time_by_mode_data'),
('congestion_travel_time_per_passenger_trip_source',
    'congestion_travel_time_per_passenger_trip_data'),
('congestion_miles_traveled_per_mode_source',
    'congestion_miles_traveled_per_mode_data'),
('congestion_bus_vmt_by_ridership_source',
    'congestion_bus_vmt_by_ridership_data'),
('congestion_on_demand_vmt_by_phases_source',
    'congestion_on_demand_vmt_by_phases_data'),
('congestion_travel_speed_source', 'congestion_travel_speed_data'),
('los_travel_expenditure_source', 'los_travel_expenditure_data'),
('los_crowding_source', 'los_crowding_data'),
('transit_cb_costs_source', 'transit_cb_costs_data'),
('transit_cb_benefits_source', 'transit_cb_benefits_data'),
('transit_inc_by_mode_source', 'transit_inc_by_mode_data'),
('sustainability_25pm_per_mode_source', 'sustainability_25pm_per_mode_data')
]


def plot_normalized_scores(source, sub_key=1, savefig='None'):
    
    p = figure(#x_range=(-6, 2), 
               y_range=CATEGORIES[::-1], 
               plot_height=350, plot_width=1200,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Weighted subscores and Submission score", text_font_size="14pt"), 'above')

    p.hbar(y='Component Name', height=0.5, 
           left=0,
           right='Weighted Score',
           source=source,
           color='color') 

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.outline_line_width = 1
    p.outline_line_color = "black"
    p.xaxis.axis_label = 'Weighted Score'
    p.yaxis.axis_label = 'Score Component'
    p.xaxis.axis_label_text_font_size = "12pt"
    p.yaxis.axis_label_text_font_size = "12pt"
    p.xaxis.major_label_text_font_size = "10pt"
    p.yaxis.major_label_text_font_size = "10pt"

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/scores.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/normalized_scores.png".format(sub_key))

    return p

def plot_fleetmix_input(source, sub_key=1, savefig='None', route_ids=[]):

    p = figure(x_range=BUSES_LIST, y_range=[str(route_id) for route_id in route_ids], 
               plot_height=350, plot_width=600,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Bus fleet mix", text_font_size="14pt"), 'above')

    p.circle(x='vehicleTypeId', y='routeId', source=source, size=8)

    p.xaxis.axis_label = 'Bus Type'
    p.yaxis.axis_label = 'Bus Route'

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/inputs/fleetmix_input.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/inputs/fleetmix_input.png".format(sub_key))

    return p

def plot_routesched_input(line_source, start_source, end_source, sub_key=1, savefig='None'):

    p = figure(x_range=(0, 24), y_range=(-0.1, 2.1), 
               plot_height=450, plot_width=600,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Frequency adjustment", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Bus Route')

    p.multi_line(xs='xs', ys='ys', source=line_source, color='color', line_width=4, legend='name') 
    p.square(x='xs', y='ys', source=start_source, fill_color='color', line_color='color', size=8)
    p.circle(x='xs', y='ys', source=end_source, fill_color='color', line_color='color', size=8)

    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Headway [h]'
    p.xaxis.ticker = BasicTicker(max_interval=4)
    p.xgrid.ticker = BasicTicker(max_interval=4)
    p.legend.label_text_font_size = '8pt'

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')
    
    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/inputs/routesched_input.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/inputs/routesched_input.png".format(sub_key))

    return p

def plot_fares_input(source, max_fare=10, max_age=121, sub_key=1, savefig='None', route_ids=[]):

    mapper = LinearColorMapper(palette=Plasma256[:120:-1], low=0.0, high=max_fare)

    p = figure(x_range=(0, max_age), y_range=route_ids, 
               plot_height=350, plot_width=475,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Mass transit fares", text_font_size="14pt"), 'above')

    p.hbar(y='routeId', height=0.5, 
           left='min_age',
           right='max_age',
           source=source,
           color=transform('amount', mapper)) 

    p.xaxis.axis_label = 'Age'
    p.yaxis.axis_label = 'Bus Route'

    color_bar = ColorBar(color_mapper=mapper, ticker=BasicTicker(),
                 label_standoff=12, border_line_color=None, location=(0,0))

    color_bar_plot = figure(title="Fare Amount [$]",
                            title_location="right", 
                            height=350, width=125, 
                            toolbar_location=None, tools="", min_border=0, 
                            outline_line_color=None)

    color_bar_plot.add_layout(color_bar, 'right')
    color_bar_plot.title.align="center"
    color_bar_plot.title.text_font_size = '10pt'

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(row(p, color_bar_plot), filename="figures/{}/inputs/fares_input.svg".format(sub_key))
    elif savefig == 'png':
      export_png(row(p, color_bar_plot), filename="figures/{}/inputs/fares_input.png".format(sub_key))

    return row(p, color_bar_plot)

def plot_modeinc_input(source, max_incentive=50, max_age=121, max_income=150000, sub_key=1, savefig='None'):

    mapper = LinearColorMapper(palette=Plasma256[:120:-1], low=0.0, high=max_incentive)
    inc_modes = ['ride_hail', 'drive_transit', 'walk_transit']

    p1 = figure(x_range=(0, max_age), y_range=inc_modes, 
               plot_height=175, plot_width=475,
               toolbar_location=None, tools="")
    p1.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p1.add_layout(Title(text="Incentives by age group", text_font_size="14pt"), 'above')

    p1.hbar(y='mode', height=0.5, 
           left='min_age',
           right='max_age',
           source=source,
           color=transform('amount', mapper)) 

    p1.xaxis.axis_label = 'Age'
    p1.yaxis.axis_label = 'Mode Choice'

    p2 = figure(x_range=(0, max_income), y_range=inc_modes, 
               plot_height=175, plot_width=475,
               toolbar_location=None, tools="")
    p2.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p2.add_layout(Title(text="Incentives by income group", text_font_size="14pt"), 'above')

    p2.hbar(y='mode', height=0.5, 
           left='min_income',
           right='max_income',
           source=source,
           color=transform('amount', mapper)) 

    p2.xaxis[0].formatter = NumeralTickFormatter(format="$0a")
    p2.xaxis.axis_label = 'Income'
    p2.yaxis.axis_label = 'Mode Choice'

    p = column(p1, p2)

    color_bar = ColorBar(color_mapper=mapper, ticker=BasicTicker(),
                 label_standoff=12, border_line_color=None, location=(0,0))

    color_bar_plot = figure(title="Incentive Amount [$/person-trip]",
                            title_location="right", 
                            height=350, width=125, 
                            toolbar_location=None, tools="", min_border=0, 
                            outline_line_color=None)

    color_bar_plot.add_layout(color_bar, 'right')
    color_bar_plot.title.align="center"
    color_bar_plot.title.text_font_size = '10pt'

    if savefig == 'svg':
      p1.output_backend = "svg"
      p2.output_backend = "svg"
      export_svgs(row(p, color_bar_plot), filename="figures/{}/inputs/modeinc_input.svg".format(sub_key))
    elif savefig == 'png':
      export_png(row(p, color_bar_plot), filename="figures/{}/inputs/modeinc_input.png".format(sub_key))

    return row(p, color_bar_plot)

def plot_mode_pie_chart(source, choice_type='planned', sub_key=1, savefig='None'):

    title = 'Overall {} mode choice'.format(choice_type)
    p = figure(plot_height=400, toolbar_location=None,
               x_range=(-0.5, 1.0))
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text=title, text_font_size="14pt"), 'above')

    p.circle(-0.5, 1.0, size=0.00000001, color="#ffffff", legend='Mode Choice')

    p.wedge(x=0, y=1, radius=0.4,
            start_angle='start_angle', end_angle='end_angle',
            line_color="white", fill_color='color', legend='Mode', source=source)

    # labels = LabelSet(x='x_loc', y='y_loc', text='label', level='glyph',
    #                   text_font_size='8pt', text_color='white',
    #                   source=source, render_mode='canvas', text_align='left')
    labels = LabelSet(x=0, y=1, text='label', level='glyph',
                      angle='start_angle', text_font_size='8pt', text_color='white',
                      source=source, render_mode='canvas')

    p.add_layout(labels)
    
    p.axis.axis_label=None
    p.axis.visible=False
    p.legend.label_text_font_size = '8pt'
    p.grid.grid_line_color = None

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/mode_{}_pie_chart.svg".format(sub_key, choice_type))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/mode_{}_pie_chart.png".format(sub_key, choice_type))

    return p

def plot_mode_choice_by_time(source, sub_key=1, savefig='None'):

    p = figure(x_range=HOURS, y_range=(0, 14000), 
               plot_height=350, plot_width=600,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Mode choice by hour", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    p.vbar_stack(MODES,
                 x='hours',
                 width=0.85,
                 source=source,
                 color=Dark2[len(MODES)],
                 legend=[value(x) for x in MODES])
    
    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Number of trips'
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.legend.location = 'top_left'
    p.xaxis.major_label_orientation = math.pi / 6

    # new_legend = p.legend[0]
    # p.legend[0].plot = None
    # p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/mode_choice_by_time.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/mode_choice_by_time.png".format(sub_key))

    return p

def plot_mode_choice_by_income_group(source, sub_key=1, savefig='None'):

    bins = ['[$0, $10k)', '[$10k, $25k)', '[$25k, $50k)', '[$50k, $75k)', '[$75k, $100k)', '[$100k, inf)']

    p = figure(x_range=MODES, #y_range=(0, 9000), 
               plot_height=350,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Mode choice by income group", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Income Group')

    nbins = len(bins)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[nbins]

    for i, bin_i in enumerate(bins):
        p.vbar(x=dodge('realizedTripMode', bin_loc, range=p.x_range), top=bin_i, width=bin_width-0.03, source=source,
               color=palette[i], legend=value(bin_i))
        bin_loc += bin_width

    p.x_range.range_padding = bin_width
    p.xgrid.grid_line_color = None
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.axis_label = 'Mode Choice'
    p.yaxis.axis_label = 'Number of People'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/mode_choice_by_income_group.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/mode_choice_by_income_group.png".format(sub_key))

    return p

def plot_mode_choice_by_age_group(source, sub_key=1, savefig='None'):

    edges = [0, 18, 30, 40, 50, 60, float('inf')]
    bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]

    p = figure(x_range=MODES, #y_range=(0, 6000), 
               plot_height=350,
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Mode choice by age group", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Age Group')

    nbins = len(bins)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[nbins]

    for i, bin_i in enumerate(bins):
        p.vbar(x=dodge('realizedTripMode', bin_loc, range=p.x_range), top=bin_i, width=bin_width-0.03, source=source,
               color=palette[i], legend=value(bin_i))
        bin_loc += bin_width

    p.x_range.range_padding = bin_width
    p.xgrid.grid_line_color = None
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.axis_label = 'Mode Choice'
    p.yaxis.axis_label = 'Number of People'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/mode_choice_by_age_group.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/mode_choice_by_age_group.png".format(sub_key))

    return p

def plot_mode_choice_by_distance(source, sub_key=1, savefig='None'):

    edges = [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7.5, 10, 40]
    bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]

    p = figure(x_range=bins, #y_range=(0, 6000), 
               plot_height=350, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Mode choice by trip distance", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    p.vbar_stack(MODES,
                 x='Trip Distance (miles)', 
                 width=0.5, 
                 source=source,
                 color=Dark2[len(MODES)],
                 legend=[value(x) for x in MODES])
    
    p.xaxis.axis_label = 'Trip Distance (miles)'
    p.yaxis.axis_label = 'Number of Trips'
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/mode_choice_by_distance.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/mode_choice_by_distance.png".format(sub_key))

    return p

def plot_congestion_travel_time_by_mode(source, sub_key=1, savefig='None'):

    p = figure(x_range=MODES, #y_range=(0, 60), 
               plot_height=350, plot_width=700, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Average travel time per trip and by mode", text_font_size="14pt"), 'above')

    p.vbar(x='x', top='y', width=0.8, source=source, color='color')
    
    p.xaxis.axis_label = 'Mode'
    p.yaxis.axis_label = 'Travel time [min]'
    p.xaxis.major_label_orientation = math.pi / 6

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/congestion_travel_time_by_mode.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/congestion_travel_time_by_mode.png".format(sub_key))

    return p

def plot_congestion_travel_time_per_passenger_trip(source, sub_key=1, savefig='None'):

    p = figure(x_range=HOURS, #y_range=(0, 350), 
               plot_height=350, plot_width=800, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Average travel time per passenger-trip over the day", text_font_size="14pt"), 'above')

    nbins = len(MODES)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[nbins]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    for i, mode_i in enumerate(MODES):
        p.vbar(x=dodge('index', bin_loc, range=p.x_range), top=mode_i, width=bin_width-0.04, source=source,
               color=palette[i], legend=value(mode_i))
        bin_loc += bin_width

    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Travel time [min]'
    p.legend.label_text_font_size = '8pt'
    p.legend.location = 'top_left'
    p.xaxis.major_label_orientation = math.pi / 6

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/congestion_travel_time_per_passenger_trip.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/congestion_travel_time_per_passenger_trip.png".format(sub_key))

    return p

def plot_congestion_miles_traveled_per_mode(source, sub_key=1, savefig='None'):

    p = figure(x_range=['ride_hail', 'car', 'walk', 'bus'], #y_range=(0, 90000), 
               plot_height=350, plot_width=600, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Daily miles traveled per mode", text_font_size="14pt"), 'above')

    p.vbar(x='modes', top='vmt', color='color', source=source, width=0.8)
    
    # p.xgrid.grid_line_color = None
    # p.ygrid.grid_line_color = None
    # p.outline_line_width = 1
    # p.outline_line_color = "black"
    p.xaxis.axis_label = 'Mode'
    p.yaxis.axis_label = 'Miles traveled'
    p.yaxis[0].formatter = NumeralTickFormatter(format="0a")
    p.xaxis.major_label_orientation = math.pi / 6
    # p.xaxis.axis_label_text_font_size = "12pt"
    # p.yaxis.axis_label_text_font_size = "12pt"
    # p.xaxis.major_label_text_font_size = "10pt"
    # p.yaxis.major_label_text_font_size = "10pt"
    
    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/congestion_miles_traveled_per_mode.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/congestion_miles_traveled_per_mode.png".format(sub_key))

    return p

def plot_congestion_bus_vmt_by_ridership(source, sub_key=1, savefig='None'):
    
    bins = [
        'empty\n(0 passengers)', 
        'low ridership\n(< 50% seating capacity)', 
        'medium ridership\n(< seating capacity)', 
        'high ridership\n(< 50% standing capacity)',
        'crowded\n(<= standing capacity)'
    ]
    p = figure(x_range=HOURS, #y_range=(0, 1200000), 
               plot_height=350, plot_width=600, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Bus vehicle miles traveled by ridership by time of day", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Ridership')

    p.vbar_stack(bins,
                 x='Hour',
                 width=0.85,
                 source=source,
                 color=Dark2[len(bins)],
                 legend=[value(x) for x in bins])
    
    # p.xgrid.grid_line_color = None
    # p.ygrid.grid_line_color = None
    # p.outline_line_width = 1
    # p.outline_line_color = "black"
    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Vehicle miles traveled'
    p.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '10pt'
    p.xaxis.major_label_orientation = math.pi / 2
    # p.xaxis.axis_label_text_font_size = "12pt"
    # p.yaxis.axis_label_text_font_size = "12pt"
    # p.xaxis.major_label_text_font_size = "10pt"
    # p.yaxis.major_label_text_font_size = "10pt"

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')
    
    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/congestion_bus_vmt_by_ridership.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/congestion_bus_vmt_by_ridership.png".format(sub_key))

    return p

def plot_congestion_on_demand_vmt_by_phases(source, sub_key=1, savefig='None'):

    driving_states = ["fetch", "fare"]
    p = figure(x_range=HOURS, #y_range=(0, 2500000), 
               plot_height=350, plot_width=700, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Vehicle miles traveled by on-demand ride vehicles by driving state", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Driving State')

    p.vbar_stack(driving_states,
                 x='Hour', 
                 width=0.85, 
                 source=source,
                 color=Dark2[3][:len(driving_states)],
                 legend=[value(x) for x in driving_states])
    
    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Vehicle miles traveled'
    p.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/congestion_on_demand_vmt_by_phases.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/congestion_on_demand_vmt_by_phases.png".format(sub_key))

    return p

def plot_congestion_travel_speed(source, sub_key=1, savefig='None'):

    edges = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]

    p = figure(x_range=bins, #y_range=(0, 12), 
               plot_height=350, plot_width=700, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Average travel speed by time of day per mode", text_font_size="14pt"), 'above')

    nbins = len(MODES)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[nbins]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    for i, mode_i in enumerate(MODES):
        p.vbar(x=dodge('Start time interval (hour)', bin_loc, range=p.x_range), top=mode_i, width=bin_width-0.04, source=source,
               color=palette[i], legend=value(mode_i))
        bin_loc += bin_width

    p.xaxis.axis_label = 'Start time interval (hour of day)'
    p.yaxis.axis_label = 'Average speed (miles per hour)'
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/congestion_travel_speed.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/congestion_travel_speed.png".format(sub_key))

    return p

def plot_los_travel_expenditure(source, sub_key=1, savefig='None'):

    p = figure(x_range=HOURS, #y_range=(0, 6.0), 
               plot_height=350, plot_width=600, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Average travel expenditure per trip and by mode over the day", text_font_size="14pt"), 'above')

    spend_modes = set(['walk_transit', 'drive_transit', 'car', 'ride_hail'])
    nbins = len(spend_modes)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[len(MODES)]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    for i, mode_i in enumerate(MODES):
        if mode_i in spend_modes:
            p.vbar(x=dodge('hour_of_day', bin_loc, range=p.x_range), top=mode_i, width=bin_width-0.04, source=source,
                   color=palette[i], legend=value(mode_i))
            bin_loc += bin_width

    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Average cost [$]'
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/los_travel_expenditure.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/los_travel_expenditure.png".format(sub_key))

    return p

def plot_los_crowding(source, sub_key=1, savefig='None', route_ids=[]):

    # AM peak = 7am-10am, PM Peak = 5pm-8pm, Early Morning, Midday, Late Evening = in between
    labels = ["Early Morning (12a-7a)", "AM Peak (7a-10a)", "Midday (10a-5p)", "PM Peak (5p-8p)", "Late Evening (8p-12a)"]
    p = figure(x_range=route_ids, #y_range=(0, 15), 
               plot_height=350, plot_width=600, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Average hours of bus crowding by bus route and period of day", text_font_size="14pt"), 'above')

    nbins = len(labels)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[nbins]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Service Period')

    for i, label_i in enumerate(labels):
        p.vbar(x=dodge('route_id', bin_loc, range=p.x_range), top=label_i, width=bin_width-0.04, source=source,
               color=palette[i], legend=value(label_i))
        bin_loc += bin_width

    p.xaxis.axis_label = 'Bus route'
    p.yaxis.axis_label = 'Hours of bus crowding'
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/los_crowding.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/los_crowding.png".format(sub_key))

    return p

def plot_transit_cb(costs_source, benefits_source, sub_key=1, savefig='None', route_ids=[]):

    costs_labels = ["OperationalCosts", "FuelCost"]
    benefits_label = ["Fare"]
    p = figure(x_range=route_ids, #y_range=(-20e6, 25e6), 
               plot_height=350, plot_width=600, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Costs and Benefits of Mass Transit Level of Service Intervention by bus route", text_font_size="14pt"), 'above')

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Costs and Benefits')

    p.vbar_stack(benefits_label,
                 x='route_id',
                 width=0.85,
                 source=benefits_source,
                 color=Dark2[3][2],
                 legend=value("Fare"))

    p.vbar_stack(costs_labels,
                 x='route_id',
                 width=0.85,
                 source=costs_source,
                 color=Dark2[3][:2],
                 legend=[value(x) for x in costs_labels])
    
    p.xaxis.axis_label = 'Bus route'
    p.yaxis.axis_label = 'Amount [$]'
    p.yaxis[0].formatter = NumeralTickFormatter(format="$0a")
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/transit_cb.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/transit_cb.png".format(sub_key))

    return p

def plot_transit_inc_by_mode(source, sub_key=1, savefig='None'):

    p = figure(x_range=HOURS, #y_range=(0, 35000), 
               plot_height=350, plot_width=600, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Total incentives distributed by time of day per mode", text_font_size="14pt"), 'above')

    ride_modes = set(['walk_transit', 'drive_transit', 'ride_hail'])
    nbins = len(ride_modes)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Dark2[len(MODES)]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    for i, mode_i in enumerate(MODES):
        if mode_i in ride_modes:
            p.vbar(x=dodge('hour_of_day', bin_loc, range=p.x_range), top=mode_i, width=bin_width-0.04, source=source,
                   color=palette[i], legend=value(mode_i))
            bin_loc += bin_width

    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Incentives distributed [$]'
    p.yaxis[0].formatter = NumeralTickFormatter(format="$0a")
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/transit_inc_by_mode.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/transit_inc_by_mode.png".format(sub_key))

    return p

def plot_sustainability_25pm_per_mode(source, sub_key=1, savefig='None'):
 
    modes = ['ride_hail', 'car', 'bus']
    p = figure(x_range=modes, #y_range=(0, 2500), 
               plot_height=350, 
               toolbar_location=None, tools="")
    p.add_layout(Title(text=sub_key, text_font_style="italic"), 'above')
    p.add_layout(Title(text="Daily PM2.5 emissions per mode", text_font_size="14pt"), 'above')

    p.vbar(x='modes', top='emissions', color='color', source=source, width=0.8)
    
    p.xaxis.axis_label = 'Mode'
    p.yaxis.axis_label = 'Emissions [g]'
    p.xaxis.major_label_orientation = math.pi / 6
    
    if savefig == 'svg':
      p.output_backend = "svg"
      export_svgs(p, filename="figures/{}/outputs/sustainability_25pm_per_mode.svg".format(sub_key))
    elif savefig == 'png':
      export_png(p, filename="figures/{}/outputs/sustainability_25pm_per_mode.png".format(sub_key))

    return p

def find_submissions():

    path = join(dirname(__file__), 'data/submissions/')
    new_dirs = {'/'.join(f.split('/')[-2:]) for f in glob.glob(join(path, '*/*')) if isdir(f)}

    cols = ['submission_dir', 'show']
    try:
        submission_dirs = pd.read_csv(join(dirname(__file__), 'submission_files.csv'))
    except IOError:
        submission_dirs = pd.DataFrame(columns=cols)

    old_dirs = set(submission_dirs['submission_dir'])

    removed_dirs = old_dirs.difference(new_dirs)
    added_dirs = new_dirs.difference(old_dirs)

    added = pd.DataFrame.from_records([(added_dir, 1) for added_dir in added_dirs], columns=cols)
    submission_dirs = submission_dirs.append(added, ignore_index=True, sort=False)
    submission_dirs.loc[submission_dirs['submission_dir'].isin(removed_dirs), 'show'] = 0

    submission_dirs.to_csv(join(dirname(__file__), 'submission_files.csv'), index=False)

    if len(removed_dirs):
        print("Can't find the following submissions, hiding for now:")
        print('\n'.join(['\t{}'.format(removed_dir) for removed_dir in removed_dirs]))

    if len(added_dirs):
        print('The following submissions were added:')
        print('\n'.join(['\t{}'.format(added_dir) for added_dir in added_dirs]))

    return submission_dirs


def create_dir_tree(sub_key):
    
    try:
        makedirs("figures/{}".format(sub_key))
    except OSError:
        pass

    try:
        makedirs("figures/{}/inputs".format(sub_key))
    except OSError:
        pass

    try:
        makedirs("figures/{}/outputs".format(sub_key))
    except OSError:
        pass

def update_submission(submission_sources, sub_order):

    def update_sub_order(attrname, old, new):
        # This function updates the data source for plots whenever people select
        # a different submission from the dropdown
        scenario_key, submission_key = new.split('/')
        create_dir_tree(submission_key)
        if sub_order == 'submission1':
            submission1_key = submission_key
        else:
            submission2_key = submission_key

        submission = submission_dict[scenario_key]['submissions'][submission_key]
        submission.get_data()
        submission.make_data_sources()
        for source_name, data_name in SOURCE_NAME_DATA_PAIR:
            submission_sources[sub_order][source_name].data = \
                getattr(submission, data_name)

    return update_sub_order

title_div = Div(text="<img src='Dashboard_Uber_Prize/static/uber.svg' height='18'><b>Prize Visualization Dashboard</b>", width=800, height=10, style={'font-size': '200%'})

### Instantiate all submission objects and generate data sources ###
# try:
#     submission_dirs = pd.read_csv(join(dirname(__file__), 'submission_files_override.csv'))
# except IOError:
#     submission_dirs = find_submissions()
# submissions = submission_dirs.loc[submission_dirs['show'] == 1, 'submission_dir'].to_list()
bistro_db = BistroDB(
    db_name='bistro', user_name='bistroclt', db_key='client',
    host='13.56.123.155')
simulations = bistro_db.load_simulation_df()

submissions = []
submission_dict = {}
for _, simulation in simulations.iterrows():
    simulation_id, datetime, scenario, name = (
        simulation['simulation_id'], str(simulation['datetime']),
        simulation['scenario'], simulation['name'])
    submissions += [scenario+'/'+name+'@'+datetime]
    submission_name = name+'@'+datetime
    if scenario not in submission_dict:
        submission_dict[scenario] = {
            'submissions': {
            submission_name: Submission(
                name=submission_name, scenario=scenario, simulation_id=simulation_id)
            },
            'categories': yaml.safe_load(
                open(join(dirname(__file__), 'kpis.yaml')))
        }
    else:
        submission_dict[scenario]['submissions'][submission_name] = Submission(
            name=datetime, scenario=scenario, simulation_id=simulation_id)
# for scenario_submission in submissions:
#     scenario, submission = scenario_submission.split('/')
#     if scenario not in submission_dict:
#         submission_dict[scenario] = {
#             'submissions': {submission: Submission(name=submission, scenario=scenario)},
#             'categories': yaml.safe_load(open(join(dirname(__file__), 'kpis.yaml')))
#         }
#     else:
#         submission_dict[scenario]['submissions'][submission] = Submission(name=submission, scenario=scenario)

try:
    makedirs("figures")
except OSError:
    pass


if 'S0' in submission_dict.keys():
    scenario_key = 'S0'
else:
    scenario_key = sorted(list(submission_dict.keys()))[0]

CATEGORIES = submission_dict[scenario_key]['categories']

if 'warm-start' in submission_dict[scenario_key]['submissions']:
    submission1_key = 'warm-start'
else:
    submission1_key = sorted(list(submission_dict[scenario_key]['submissions'].keys()))[0]
create_dir_tree(submission1_key)

if 'example_submission' in submission_dict[scenario_key]['submissions']:
    submission2_key = 'example_submission'
else:
    submission2_key = sorted(list(submission_dict[scenario_key]['submissions'].keys()))[-1]
create_dir_tree(submission2_key)
##############################################################

### Convert data sources into ColumnDataSources ###

# submission_sources basically construct data source for the plots from each
# submission 1 and 2, grouping them with 'submission1' and 'submission2' for the
# ploting process to find the right data more easily 
submission_sources = {'submission1':{}, 'submission2':{}}
for sub_order, submission_key in \
        [('submission1', submission1_key), ('submission2', submission2_key)]:
    submission = submission_dict[scenario_key]['submissions'][submission_key]
    submission.get_data()
    submission.make_data_sources()
    for source_name, data_name in SOURCE_NAME_DATA_PAIR:
        submission_sources[sub_order][source_name] = ColumnDataSource(
            data=getattr(submission, data_name))
###################################################

### Generate plots from ColumnDataSource's ###
plots = {'submission1': {}, 'submission2': {}}
for sub_order, sub_key in \
        [('submission1',submission1_key), ('submission2',submission2_key)]:
    sources = submission_sources[sub_order]
    submission = submission_dict[scenario_key]['submissions'][sub_key]
    plots[sub_order]['normalized_scores_plot'] = plot_normalized_scores(
        source=sources['normalized_scores_source'], sub_key=sub_key)
    plots[sub_order]['fleetmix_input_plot'] = plot_fleetmix_input(
        source=sources['fleetmix_input_source'], sub_key=sub_key,
        route_ids=submission.route_ids)
    plots[sub_order]['routesched_input_plot'] = plot_routesched_input(
        line_source=sources['routesched_input_line_source'],
        start_source=sources['routesched_input_start_source'],
        end_source=sources['routesched_input_end_source'],
        sub_key=sub_key)
    plots[sub_order]['fares_input_plot'] = plot_fares_input(
        source=sources['fares_input_source'], sub_key=sub_key,
        route_ids=submission.route_ids)
    plots[sub_order]['modeinc_input_plot'] = plot_modeinc_input(
        source=sources['modeinc_input_source'], sub_key=sub_key)
    plots[sub_order]['mode_planned_pie_chart_plot'] = plot_mode_pie_chart(
        source=sources['mode_planned_pie_chart_source'],
        choice_type='planned', sub_key=sub_key)
    plots[sub_order]['mode_realized_pie_chart_plot'] = plot_mode_pie_chart(
        source=sources['mode_realized_pie_chart_source'],
        choice_type='realized', sub_key=sub_key)
    plots[sub_order]['mode_choice_by_time_plot'] = plot_mode_choice_by_time(
        source=sources['mode_choice_by_time_source'], sub_key=sub_key)
    plots[sub_order]['mode_choice_by_income_group_plot'] = \
        plot_mode_choice_by_income_group(
            source=sources['mode_choice_by_income_group_source'],
            sub_key=sub_key)
    plots[sub_order]['mode_choice_by_age_group_plot'] = \
        plot_mode_choice_by_age_group(
            source=sources['mode_choice_by_age_group_source'],
            sub_key=sub_key)
    plots[sub_order]['mode_choice_by_distance_plot'] = \
        plot_mode_choice_by_distance(
            source=sources['mode_choice_by_distance_source'],
            sub_key=sub_key)
    plots[sub_order]['congestion_travel_time_by_mode_plot'] = \
        plot_congestion_travel_time_by_mode(
            source=sources['congestion_travel_time_by_mode_source'],
            sub_key=sub_key)
    plots[sub_order]['congestion_travel_time_per_passenger_trip_plot'] = \
        plot_congestion_travel_time_per_passenger_trip(
            source=sources['congestion_travel_time_per_passenger_trip_source'],
            sub_key=sub_key)
    plots[sub_order]['congestion_miles_traveled_per_mode_plot'] = \
        plot_congestion_miles_traveled_per_mode(
            source=sources['congestion_miles_traveled_per_mode_source'],
            sub_key=sub_key)
    plots[sub_order]['congestion_bus_vmt_by_ridership_plot'] = \
        plot_congestion_bus_vmt_by_ridership(
            source=sources['congestion_bus_vmt_by_ridership_source'],
            sub_key=sub_key)
    plots[sub_order]['congestion_on_demand_vmt_by_phases_plot'] = \
        plot_congestion_on_demand_vmt_by_phases(
            source=sources['congestion_on_demand_vmt_by_phases_source'],
            sub_key=sub_key)
    plots[sub_order]['congestion_travel_speed_plot'] = \
        plot_congestion_travel_speed(
            source=sources['congestion_travel_speed_source'], sub_key=sub_key)
    plots[sub_order]['los_travel_expenditure_plot'] = \
        plot_los_travel_expenditure(
            source=sources['los_travel_expenditure_source'],
            sub_key=sub_key)
    plots[sub_order]['los_crowding_plot'] = plot_los_crowding(
        source=sources['los_crowding_source'], sub_key=sub_key,
        route_ids=submission.route_ids)
    plots[sub_order]['transit_cb_plot'] = plot_transit_cb(
        costs_source=sources['transit_cb_costs_source'],
        benefits_source=sources['transit_cb_benefits_source'], sub_key=sub_key,
        route_ids=submission.route_ids)
    plots[sub_order]['transit_inc_by_mode_plot'] = plot_transit_inc_by_mode(
        source=sources['transit_inc_by_mode_source'], sub_key=sub_key)
    plots[sub_order]['sustainability_25pm_per_mode_plot'] = \
        plot_sustainability_25pm_per_mode(
            source=sources['sustainability_25pm_per_mode_source'],
            sub_key=sub_key)
##############################################

### Gather plot objects into lists ###

submission_inputs_plots = [
    'fleetmix_input_plot',
    'routesched_input_plot',
    'fares_input_plot',
    'modeinc_input_plot'
]
submission_scores_plots = ['normalized_scores_plot']
submission_outputs_mode_plots = [
    'mode_planned_pie_chart_plot',
    'mode_realized_pie_chart_plot',
    'mode_choice_by_time_plot',
    'mode_choice_by_income_group_plot',
    'mode_choice_by_age_group_plot',
    'mode_choice_by_distance_plot'
]
submission_outputs_congestion_plots = [
    'congestion_travel_time_by_mode_plot',
    'congestion_travel_time_per_passenger_trip_plot',
    'congestion_miles_traveled_per_mode_plot',
    'congestion_bus_vmt_by_ridership_plot',
    'congestion_on_demand_vmt_by_phases_plot',
    'congestion_travel_speed_plot'
]
submission_outputs_los_plots = [
    'los_travel_expenditure_plot',
    'los_crowding_plot'
]
submission_outputs_transitcb_plots = [
    'transit_cb_plot',
    'transit_inc_by_mode_plot'
]
submission_outputs_sustainability_plots = ['sustainability_25pm_per_mode_plot']

######################################
sub_orders = ['submission1','submission2']
# 
# the code below is equivalent to:
# row(column([plots['submission1'][p1], plots['submission1'][p2]], ...),
#     column([plots['submission2'][p1], ...])
#     ...)
inputs_plots = row(
    *[column([plots[sub_order][p] for p in submission_inputs_plots])
    for sub_order in sub_orders])
scores_plots = column(
    *[column([plots[sub_order][p] for p in submission_scores_plots])
    for sub_order in sub_orders])
outputs_mode_plots = row(
    *[column([plots[sub_order][p] for p in submission_outputs_mode_plots])
    for sub_order in sub_orders])
outputs_los_plots = row(
    *[column([plots[sub_order][p] for p in submission_outputs_los_plots])
    for sub_order in sub_orders])
outputs_congestion_plots = row(
    *[column([plots[sub_order][p] for p in submission_outputs_congestion_plots])
    for sub_order in sub_orders])
outputs_transitcb_plots = row(
    *[column([plots[sub_order][p] for p in submission_outputs_transitcb_plots])
    for sub_order in sub_orders])
outputs_sustainability_plots = row(
    *[column([plots[sub_order][p] for p in submission_outputs_sustainability_plots])
    for sub_order in sub_orders])

submission1_select = Select(value='{}/{}'.format(scenario_key, submission1_key),
                     title='Submission 1', 
                     options=sorted(submissions))
submission2_select = Select(value='{}/{}'.format(scenario_key, submission2_key),
                     title='Submission 2', 
                     options=sorted(submissions))

pulldowns = row(submission1_select, submission2_select)

# update_submission it self isn't a real 'function', it returns another function
# that will update plot data source for either submission1 or 2 depends on the
# inputs name.
submission1_select.on_change(
    'value', update_submission(submission_sources, 'submission1'))
submission2_select.on_change(
    'value', update_submission(submission_sources, 'submission2'))

inputs = layout([inputs_plots], sizing_mode='fixed')
scores = layout([[scores_plots]], sizing_mode='fixed')
outputs_mode = layout([outputs_mode_plots], sizing_mode='fixed')
outputs_los = layout([outputs_los_plots], sizing_mode='fixed')
outputs_congestion = layout([outputs_congestion_plots], sizing_mode='fixed')
outputs_transitcb = layout([outputs_transitcb_plots], sizing_mode='fixed')
outputs_sustainability = layout([outputs_sustainability_plots], sizing_mode='fixed')

inputs_tab = Panel(child=inputs,title="Inputs")
scores_tab = Panel(child=scores,title="Scores")
outputs_mode_tab = Panel(child=outputs_mode,title="Outputs - Mode Choice")
outputs_los_tab = Panel(child=outputs_los,title="Outputs - Level of Service")
outputs_congestion_tab = Panel(child=outputs_congestion,title="Outputs - Congestion")
outputs_transitcb_tab = Panel(child=outputs_transitcb,title="Outputs - Cost/Benefit")
outputs_sustainability_tab = Panel(child=outputs_sustainability,title="Outputs - Sustainability")

tabs=[
    inputs_tab, 
    scores_tab, 
    outputs_mode_tab, 
    outputs_los_tab, 
    outputs_congestion_tab, 
    outputs_transitcb_tab, 
    outputs_sustainability_tab
]
tabs = Tabs(tabs=tabs, width=1200)

curdoc().add_root(column([title_div, pulldowns, tabs]))
curdoc().title = "UberPrize Dashboard"
