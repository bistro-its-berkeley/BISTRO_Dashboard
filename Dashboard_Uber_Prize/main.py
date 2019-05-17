import glob
import math
from os import listdir
from os.path import dirname, isdir, join
import pandas as pd

from bokeh.core.properties import value
from bokeh.io import curdoc, show, output_file
from bokeh.layouts import row, column, gridplot, layout, widgetbox
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, DataRange1d, LabelSet, Legend, LinearColorMapper, Select
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.models.widgets import CheckboxButtonGroup, Div, Panel, Tabs
from bokeh.palettes import Category10, Category20, Plasma256, YlOrRd
from bokeh.plotting import figure, show
from bokeh.transform import dodge, transform

from run import Run

CATEGORIES = [
    'Accessibility: Number of secondary locations accessible within 15 minutes',
    'Accessibility: Number of work locations accessible within 15 minutes',
    'Congestion: average vehicle delay per passenger trip',
    'Congestion: total vehicle miles traveled',
    'Level of service: average bus crowding experienced',
    'Level of service: average trip expenditure - secondary',
    'Level of service: average trip expenditure - work',
    'Level of service: costs and benefits',
    'Sustainability: Total PM 2.5 Emissions',
    'Submission Score'
]
HOURS = [str(h) for h in range(24)]
ROUTE_IDS = ['1340', '1341', '1342', '1343', '1344', '1345', '1346', '1347', '1348', '1349', '1350', '1351']
BUSES_LIST = ['BUS-DEFAULT', 'BUS-SMALL-HD', 'BUS-STD-HD', 'BUS-STD-ART']
MODES = ['OnDemand_ride', 'car', 'drive_transit', 'walk', 'walk_transit']

def plot_normalized_scores(source, num=1):
    
    p = figure(x_range=(0, 10), y_range=CATEGORIES[::-1], 
               plot_height=350, plot_width=1200, title="Weighted subscores and Submission score - Run {}".format(num),
               toolbar_location=None, tools="")

    p.hbar(y='Component Name', height=0.5, 
           left=0,
           right='Weighted Score',
           source=source,
           color='color') 

    p.xaxis.axis_label = 'Weighted Score'
    p.yaxis.axis_label = 'Score Component'

    return p

def plot_fleetmix_input(source, num=1):

    p = figure(x_range=BUSES_LIST, y_range=[str(route_id) for route_id in ROUTE_IDS], 
               plot_height=350, plot_width=600, title="Bus fleet mix - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(x='vehicleTypeId', y='routeId', source=source, size=8)

    p.xaxis.axis_label = 'Bus Type'
    p.yaxis.axis_label = 'Bus Route'

    return p

def plot_routesched_input(line_source, start_source, end_source, num=1):

    p = figure(x_range=(0, 24), y_range=(0, 2), 
               plot_height=350, plot_width=600, title="Frequency adjustment - Run {}".format(num),
               toolbar_location=None, tools="")

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

    return p

def plot_fares_input(source, max_fare=10, max_age=120, num=1):

    mapper = LinearColorMapper(palette=Plasma256[:120:-1], low=0.0, high=max_fare)

    p = figure(x_range=(0, max_age), y_range=ROUTE_IDS, 
               plot_height=350, plot_width=475, title="Mass transit fares - Run {}".format(num),
               toolbar_location=None, tools="")

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

    return row(p, color_bar_plot)

def plot_modeinc_input(source, max_incentive=50, max_age=120, max_income=150000, num=1):

    mapper = LinearColorMapper(palette=Plasma256[:120:-1], low=0.0, high=max_incentive)
    inc_modes = ['OnDemand_ride', 'drive_transit', 'walk_transit']

    p1 = figure(x_range=(0, max_age), y_range=inc_modes, 
               plot_height=175, plot_width=475, title="Incentives by age group - Run {}".format(num),
               toolbar_location=None, tools="")

    p1.hbar(y='mode', height=0.5, 
           left='min_age',
           right='max_age',
           source=source,
           color=transform('amount', mapper)) 

    p1.xaxis.axis_label = 'Age'
    p1.yaxis.axis_label = 'Mode Choice'

    p2 = figure(x_range=(0, max_income), y_range=inc_modes, 
               plot_height=175, plot_width=475, title="Incentives by income group - Run {}".format(num),
               toolbar_location=None, tools="")

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

    return row(p, color_bar_plot)

def plot_mode_pie_chart(source, choice_type='planned', num=1):

    title = 'Overall {} mode choice - Run {}'.format(choice_type, num)
    p = figure(plot_height=350, title=title, toolbar_location=None,
               x_range=(-0.5, 1.0))

    p.circle(-0.5, 1.0, size=0.00000001, color="#ffffff", legend='Mode Choice')

    p.wedge(x=0, y=1, radius=0.4,
            start_angle='start_angle', end_angle='end_angle',
            line_color="white", fill_color='color', legend='Mode', source=source)

    labels = LabelSet(x=0, y=1, text='label', level='glyph',
                      angle='start_angle', text_font_size='8pt', text_color='white',
                      source=source, render_mode='canvas')

    p.add_layout(labels)

    p.axis.axis_label=None
    p.axis.visible=False
    p.legend.label_text_font_size = '8pt'
    p.grid.grid_line_color = None

    return p

def plot_mode_choice_by_time(source, num=1):

    p = figure(x_range=HOURS, y_range=(0, 6000), 
               plot_height=350, plot_width=600, title="Mode choice by hour - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    p.vbar_stack(MODES,
                 x='hours',
                 width=0.85,
                 source=source,
                 color=Category10[len(MODES)],
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

    return p

def plot_mode_choice_by_income_group(source, num=1):

    bins = ['[$0, $10k)', '[$10k, $25k)', '[$25k, $50k)', '[$50k, $75k)', '[$75k, $100k)', '[$100k, inf)']

    p = figure(x_range=MODES, y_range=(0, 12000), plot_height=350, title="Mode choice by income group - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Income Group')

    nbins = len(bins)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

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

    return p

def plot_mode_choice_by_age_group(source, num=1):

    edges = [0, 18, 30, 40, 50, 60, float('inf')]
    bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]

    p = figure(x_range=MODES, y_range=(0, 8000), plot_height=350, title="Mode choice by age group - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Age Group')

    nbins = len(bins)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

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

    return p

def plot_mode_choice_by_distance(source, num=1):

    edges = [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7.5, 10, 40]
    bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]

    p = figure(x_range=bins, y_range=(0, 7000), 
               plot_height=350, title="Mode choice by trip distance - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    p.vbar_stack(MODES,
                 x='Trip Distance (miles)', 
                 width=0.5, 
                 source=source,
                 color=Category10[len(MODES)],
                 legend=[value(x) for x in MODES])
    
    p.xaxis.axis_label = 'Trip Distance (miles)'
    p.yaxis.axis_label = 'Number of Trips'
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    return p

def plot_congestion_travel_time_by_mode(source, num=1):

    p = figure(x_range=MODES, y_range=(0, 45), 
               plot_height=350, plot_width=700, title="Average travel time per trip and by mode - Run {}".format(num),
               toolbar_location=None, tools="")

    p.vbar(x='x', top='y', width=0.8, source=source, color='color')
    
    p.xaxis.axis_label = 'Mode'
    p.yaxis.axis_label = 'Travel time [min]'
    p.xaxis.major_label_orientation = math.pi / 6
    
    return p

def plot_congestion_travel_time_per_passenger_trip(source, num=1):

    p = figure(x_range=HOURS, y_range=(0, 150), 
               plot_height=350, plot_width=800, title="Average travel time per passenger-trip over the day - Run {}".format(num),
               toolbar_location=None, tools="")

    nbins = len(MODES)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

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

    return p

def plot_congestion_miles_travelled_per_mode(source, num=1):

    p = figure(x_range=MODES, y_range=(0, 70000), 
               plot_height=350, plot_width=700, title="Daily miles travelled per mode - Run {}".format(num),
               toolbar_location=None, tools="")

    p.vbar(x='modes', top='vmt', color='color', source=source, width=0.8)
    
    p.xaxis.axis_label = 'Mode'
    p.yaxis.axis_label = 'Miles travelled'
    p.yaxis[0].formatter = NumeralTickFormatter(format="0a")
    p.xaxis.major_label_orientation = math.pi / 6
    
    return p

def plot_congestion_bus_vmt_by_ridership(source, seatingCapacity=50, num=1):
    
    bins = [
        'empty\n(0 passengers)', 
        'low ridership\n(< 50% seating capacity)', 
        'medium ridership\n(< seating capacity)', 
        'full\n(at capacity)', 
        'crowded\n(> seating capacity)'
    ]
    p = figure(x_range=HOURS, y_range=(0, 800000), 
               plot_height=350, plot_width=600, title="Bus vehicle miles travelled by ridership by time of day - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Ridership')

    p.vbar_stack(bins,
                 x='Hour',
                 width=0.85,
                 source=source,
                 color=Category10[len(bins)],
                 legend=[value(x) for x in bins])
    
    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Vehicle miles travelled'
    p.yaxis[0].formatter = NumeralTickFormatter(format="0a")
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')
    
    return p

def plot_congestion_on_demand_vmt_by_phases(source, num=1):

    driving_states = ["fetch", "fare"]
    p = figure(x_range=HOURS, y_range=(0, 1000000), 
               plot_height=350, plot_width=700, title="Vehicle miles travelled by on-demand ride vehicles by driving state - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Driving State')

    p.vbar_stack(driving_states,
                 x='Hour', 
                 width=0.85, 
                 source=source,
                 color=Category10[10][:len(driving_states)],
                 legend=[value(x) for x in driving_states])
    
    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Vehicle miles travelled'
    p.yaxis[0].formatter = NumeralTickFormatter(format="0a")
    p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    return p

def plot_congestion_travel_speed(source, num=1):

    edges = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]

    p = figure(x_range=bins, y_range=(0, 20), 
               plot_height=350, plot_width=700, title="Average travel speed by time of day per mode - Run {}".format(num),
               toolbar_location=None, tools="")

    nbins = len(MODES)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

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

    return p

def plot_los_travel_expenditure(source, num=1):

    p = figure(x_range=HOURS, y_range=(0, 10), 
               plot_height=350, plot_width=600, title="Average travel expenditure per trip and by mode over the day - Run {}".format(num),
               toolbar_location=None, tools="")

    nbins = len(MODES)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    for i, mode_i in enumerate(MODES):
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

    return p

def plot_los_crowding(source, num=1):

    # AM peak = 7am-10am, PM Peak = 5pm-8pm, Early Morning, Midday, Late Evening = in between
    labels = ["Early Morning (12a-7a)", "AM Peak (7a-10a)", "Midday (10a-5p)", "PM Peak (5p-8p)", "Late Evening (8p-12a)"]
    p = figure(x_range=ROUTE_IDS, y_range=(0, 10), 
               plot_height=350, plot_width=600, title="Average hours of bus crowding by bus route and period of day - Run {}".format(num),
               toolbar_location=None, tools="")

    nbins = len(labels)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

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

    return p

def plot_transit_cb(costs_source, benefits_source, num=1):

    costs_labels = ["OperationalCosts", "FuelCost"]
    benefits_label = ["Fare"]
    p = figure(x_range=ROUTE_IDS, y_range=(-4e6, 4e6), 
               plot_height=350, plot_width=600, title="Costs and Benefits of Mass Transit Level of Service Intervention by bus route - Run {}".format(num),
               toolbar_location=None, tools="")

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Costs and Benefits')

    p.vbar_stack(benefits_label,
                 x='route_id',
                 width=0.85,
                 source=benefits_source,
                 color=Category10[3][2],
                 legend=value("Fare"))

    p.vbar_stack(costs_labels,
                 x='route_id',
                 width=0.85,
                 source=costs_source,
                 color=Category10[3][:2],
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

    return p

def plot_transit_inc_by_mode(source, num=1):

    p = figure(x_range=HOURS, y_range=(0, 500), 
               plot_height=350, plot_width=600, title="Total incentives distributed by time of day per mode - Run {}".format(num),
               toolbar_location=None, tools="")

    nbins = len(MODES)
    total_width = 0.85
    bin_width = total_width / nbins
    bin_loc = -total_width / 2 + bin_width / 2
    palette = Category10[nbins]

    p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Trip Mode')

    for i, mode_i in enumerate(MODES):
        p.vbar(x=dodge('hour_of_day', bin_loc, range=p.x_range), top=mode_i, width=bin_width-0.04, source=source,
               color=palette[i], legend=value(mode_i))
        bin_loc += bin_width

    p.xaxis.axis_label = 'Hour of day'
    p.yaxis.axis_label = 'Incentives distributed [$]'
    p.legend.label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = math.pi / 6

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    return p

def plot_sustainability_25pm_per_mode(source, num=1):
 
    modes = ['OnDemand_ride', 'car', 'bus']
    p = figure(x_range=modes, y_range=(0, 300), 
               plot_height=350, title="Daily PM2.5 emissions per mode - Run {}".format(num),
               toolbar_location=None, tools="")

    p.vbar(x='modes', top='emissions', color='color', source=source, width=0.8)
    
    p.xaxis.axis_label = 'Mode'
    p.yaxis.axis_label = 'Emissions [g]'
    p.xaxis.major_label_orientation = math.pi / 6
    
    return p

def find_runs():

    path = join(dirname(__file__), 'data/submissions/')
    new_dirs = {'/'.join(f.split('/')[-2:]) for f in glob.glob(join(path, '*/*')) if isdir(f)}

    cols = ['run_dir', 'show']
    try:
        run_dirs = pd.read_csv(join(dirname(__file__), 'run_files.csv'))
    except IOError:
        run_dirs = pd.DataFrame(columns=cols)

    old_dirs = set(run_dirs['run_dir'])

    removed_dirs = old_dirs.difference(new_dirs)
    added_dirs = new_dirs.difference(old_dirs)

    added = pd.DataFrame.from_records([(added_dir, 1) for added_dir in added_dirs], columns=cols)
    run_dirs = run_dirs.append(added, ignore_index=True, sort=False)
    run_dirs.loc[run_dirs['run_dir'].isin(removed_dirs), 'show'] = 0

    run_dirs.to_csv(join(dirname(__file__), 'run_files.csv'), index=False)

    if len(removed_dirs):
        print("Can't find the following runs, hiding for now:")
        print('\n'.join(['\t{}'.format(removed_dir) for removed_dir in removed_dirs]))

    if len(added_dirs):
        print('The following runs were added:')
        print('\n'.join(['\t{}'.format(added_dir) for added_dir in added_dirs]))

    return run_dirs


def update_run1(attrname, old, new):
    scenario_key, run_key = new.split('/')
    run1_normalized_scores_source.data = run_dict[scenario_key][run_key].normalized_scores_data
    run1_fleetmix_input_source.data = run_dict[scenario_key][run_key].fleetmix_input_data
    run1_routesched_input_line_source.data = run_dict[scenario_key][run_key].routesched_input_line_data
    run1_routesched_input_start_source.data = run_dict[scenario_key][run_key].routesched_input_start_data
    run1_routesched_input_end_source.data = run_dict[scenario_key][run_key].routesched_input_end_data
    run1_fares_input_source.data = run_dict[scenario_key][run_key].fares_input_data
    run1_modeinc_input_source.data = run_dict[scenario_key][run_key].modeinc_input_data
    run1_mode_planned_pie_chart_source.data = run_dict[scenario_key][run_key].mode_planned_pie_chart_data
    run1_mode_realized_pie_chart_source.data = run_dict[scenario_key][run_key].mode_realized_pie_chart_data
    run1_mode_choice_by_time_source.data = run_dict[scenario_key][run_key].mode_choice_by_time_data
    run1_mode_choice_by_income_group_source.data = run_dict[scenario_key][run_key].mode_choice_by_income_group_data
    run1_mode_choice_by_age_group_source.data = run_dict[scenario_key][run_key].mode_choice_by_age_group_data
    run1_mode_choice_by_distance_source.data = run_dict[scenario_key][run_key].mode_choice_by_distance_data
    run1_congestion_travel_time_by_mode_source.data = run_dict[scenario_key][run_key].congestion_travel_time_by_mode_data
    run1_congestion_travel_time_per_passenger_trip_source.data = run_dict[scenario_key][run_key].congestion_travel_time_per_passenger_trip_data
    run1_congestion_miles_travelled_per_mode_source.data = run_dict[scenario_key][run_key].congestion_miles_travelled_per_mode_data
    run1_congestion_bus_vmt_by_ridership_source.data = run_dict[scenario_key][run_key].congestion_bus_vmt_by_ridership_data
    run1_congestion_on_demand_vmt_by_phases_source.data = run_dict[scenario_key][run_key].congestion_on_demand_vmt_by_phases_data
    run1_congestion_travel_speed_source.data = run_dict[scenario_key][run_key].congestion_travel_speed_data
    run1_los_travel_expenditure_source.data = run_dict[scenario_key][run_key].los_travel_expenditure_data
    run1_los_crowding_source.data = run_dict[scenario_key][run_key].los_crowding_data
    run1_transit_cb_costs_source.data = run_dict[scenario_key][run_key].transit_cb_costs_data
    run1_transit_cb_benefits_source.data = run_dict[scenario_key][run_key].transit_cb_benefits_data
    run1_transit_inc_by_mode_source.data = run_dict[scenario_key][run_key].transit_inc_by_mode_data
    run1_sustainability_25pm_per_mode_source.data = run_dict[scenario_key][run_key].sustainability_25pm_per_mode_data

def update_run2(attrname, old, new):
    scenario_key, run_key = new.split('/')
    run2_normalized_scores_source.data = run_dict[scenario_key][run_key].normalized_scores_data
    run2_fleetmix_input_source.data = run_dict[scenario_key][run_key].fleetmix_input_data
    run2_routesched_input_line_source.data = run_dict[scenario_key][run_key].routesched_input_line_data
    run2_routesched_input_start_source.data = run_dict[scenario_key][run_key].routesched_input_start_data
    run2_routesched_input_end_source.data = run_dict[scenario_key][run_key].routesched_input_end_data
    run2_fares_input_source.data = run_dict[scenario_key][run_key].fares_input_data
    run2_modeinc_input_source.data = run_dict[scenario_key][run_key].modeinc_input_data
    run2_mode_planned_pie_chart_source.data = run_dict[scenario_key][run_key].mode_planned_pie_chart_data
    run2_mode_realized_pie_chart_source.data = run_dict[scenario_key][run_key].mode_realized_pie_chart_data
    run2_mode_choice_by_time_source.data = run_dict[scenario_key][run_key].mode_choice_by_time_data
    run2_mode_choice_by_income_group_source.data = run_dict[scenario_key][run_key].mode_choice_by_income_group_data
    run2_mode_choice_by_age_group_source.data = run_dict[scenario_key][run_key].mode_choice_by_age_group_data
    run2_mode_choice_by_distance_source.data = run_dict[scenario_key][run_key].mode_choice_by_distance_data
    run2_congestion_travel_time_by_mode_source.data = run_dict[scenario_key][run_key].congestion_travel_time_by_mode_data
    run2_congestion_travel_time_per_passenger_trip_source.data = run_dict[scenario_key][run_key].congestion_travel_time_per_passenger_trip_data
    run2_congestion_miles_travelled_per_mode_source.data = run_dict[scenario_key][run_key].congestion_miles_travelled_per_mode_data
    run2_congestion_bus_vmt_by_ridership_source.data = run_dict[scenario_key][run_key].congestion_bus_vmt_by_ridership_data
    run2_congestion_on_demand_vmt_by_phases_source.data = run_dict[scenario_key][run_key].congestion_on_demand_vmt_by_phases_data
    run2_congestion_travel_speed_source.data = run_dict[scenario_key][run_key].congestion_travel_speed_data
    run2_los_travel_expenditure_source.data = run_dict[scenario_key][run_key].los_travel_expenditure_data
    run2_los_crowding_source.data = run_dict[scenario_key][run_key].los_crowding_data
    run1_transit_cb_costs_source.data = run_dict[scenario_key][run_key].transit_cb_costs_data
    run1_transit_cb_benefits_source.data = run_dict[scenario_key][run_key].transit_cb_benefits_data
    run2_transit_inc_by_mode_source.data = run_dict[scenario_key][run_key].transit_inc_by_mode_data
    run2_sustainability_25pm_per_mode_source.data = run_dict[scenario_key][run_key].sustainability_25pm_per_mode_data

title_div = Div(text="<img src='Dashboard_Uber_Prize/static/uber.svg' height='18'><b>Prize Visualization Dashboard</b>", width=800, height=10, style={'font-size': '200%'})

### Instantiate all run objects and generate data sources ###
path = join(dirname(__file__), 'data/submissions/')
scenarios = [f.split('/')[-1] for f in glob.glob(join(path, '*')) if isdir(f)]
try:
    run_dirs = pd.read_csv(join(dirname(__file__), 'run_files_override.csv'))
except IOError:
    run_dirs = find_runs()
runs = run_dirs.loc[run_dirs['show'] == 1, 'run_dir'].to_list()

run_dict = {}
for scenario_run in runs:
    scenario, run = scenario_run.split('/')
    if scenario not in run_dict:
        run_dict[scenario] = {
            run: Run(name=run, scenario=scenario)
        }
    else:
        run_dict[scenario][run] = Run(name=run, scenario=scenario)

if 'S0' in scenarios:
    scenario_key = 'S0'
else:
    scenario_key = scenarios[0]

if 'warm-start' in run_dict[scenario_key]:
    run1_key = 'warm-start'
else:
    run1_key = run_dict[scenario_key][0]

if 'example_run' in run_dict[scenario_key]:
    run2_key = 'example_run'
else:
    run2_key = run_dict[scenario_key][1]
##############################################################

### Convert data sources into ColumnDataSources ###
run1_normalized_scores_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].normalized_scores_data)
run1_fleetmix_input_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].fleetmix_input_data)
run1_routesched_input_line_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].routesched_input_line_data)
run1_routesched_input_start_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].routesched_input_start_data)
run1_routesched_input_end_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].routesched_input_end_data)
run1_fares_input_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].fares_input_data)
run1_modeinc_input_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].modeinc_input_data)
run1_mode_planned_pie_chart_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].mode_planned_pie_chart_data)
run1_mode_realized_pie_chart_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].mode_realized_pie_chart_data)
run1_mode_choice_by_time_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].mode_choice_by_time_data)
run1_mode_choice_by_income_group_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].mode_choice_by_income_group_data)
run1_mode_choice_by_age_group_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].mode_choice_by_age_group_data)
run1_mode_choice_by_distance_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].mode_choice_by_distance_data)
run1_congestion_travel_time_by_mode_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].congestion_travel_time_by_mode_data)
run1_congestion_travel_time_per_passenger_trip_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].congestion_travel_time_per_passenger_trip_data)
run1_congestion_miles_travelled_per_mode_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].congestion_miles_travelled_per_mode_data)
run1_congestion_bus_vmt_by_ridership_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].congestion_bus_vmt_by_ridership_data)
run1_congestion_on_demand_vmt_by_phases_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].congestion_on_demand_vmt_by_phases_data)
run1_congestion_travel_speed_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].congestion_travel_speed_data)
run1_los_travel_expenditure_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].los_travel_expenditure_data)
run1_los_crowding_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].los_crowding_data)
run1_transit_cb_costs_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].transit_cb_costs_data)
run1_transit_cb_benefits_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].transit_cb_benefits_data)
run1_transit_inc_by_mode_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].transit_inc_by_mode_data)
run1_sustainability_25pm_per_mode_source = ColumnDataSource(data=run_dict[scenario_key][run1_key].sustainability_25pm_per_mode_data)

run2_normalized_scores_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].normalized_scores_data)
run2_fleetmix_input_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].fleetmix_input_data)
run2_routesched_input_line_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].routesched_input_line_data)
run2_routesched_input_start_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].routesched_input_start_data)
run2_routesched_input_end_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].routesched_input_end_data)
run2_fares_input_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].fares_input_data)
run2_modeinc_input_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].modeinc_input_data)
run2_mode_planned_pie_chart_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].mode_planned_pie_chart_data)
run2_mode_realized_pie_chart_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].mode_realized_pie_chart_data)
run2_mode_choice_by_time_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].mode_choice_by_time_data)
run2_mode_choice_by_income_group_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].mode_choice_by_income_group_data)
run2_mode_choice_by_age_group_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].mode_choice_by_age_group_data)
run2_mode_choice_by_distance_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].mode_choice_by_distance_data)
run2_congestion_travel_time_by_mode_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].congestion_travel_time_by_mode_data)
run2_congestion_travel_time_per_passenger_trip_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].congestion_travel_time_per_passenger_trip_data)
run2_congestion_miles_travelled_per_mode_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].congestion_miles_travelled_per_mode_data)
run2_congestion_bus_vmt_by_ridership_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].congestion_bus_vmt_by_ridership_data)
run2_congestion_on_demand_vmt_by_phases_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].congestion_on_demand_vmt_by_phases_data)
run2_congestion_travel_speed_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].congestion_travel_speed_data)
run2_los_travel_expenditure_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].los_travel_expenditure_data)
run2_los_crowding_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].los_crowding_data)
run2_transit_cb_costs_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].transit_cb_costs_data)
run2_transit_cb_benefits_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].transit_cb_benefits_data)
run2_transit_inc_by_mode_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].transit_inc_by_mode_data)
run2_sustainability_25pm_per_mode_source = ColumnDataSource(data=run_dict[scenario_key][run2_key].sustainability_25pm_per_mode_data)
###################################################

### Generate plots from ColumnDataSource's ###
normalized_scores_1_plot = plot_normalized_scores(source=run1_normalized_scores_source)
fleetmix_input_1_plot = plot_fleetmix_input(source=run1_fleetmix_input_source)
routesched_input_1_plot = plot_routesched_input(
    line_source=run1_routesched_input_line_source, 
    start_source=run1_routesched_input_start_source,
    end_source=run1_routesched_input_end_source)
fares_input_1_plot = plot_fares_input(source=run1_fares_input_source)
modeinc_input_1_plot = plot_modeinc_input(source=run1_modeinc_input_source)
mode_planned_pie_chart_1_plot = plot_mode_pie_chart(source=run1_mode_planned_pie_chart_source, choice_type='planned')
mode_realized_pie_chart_1_plot = plot_mode_pie_chart(source=run1_mode_realized_pie_chart_source, choice_type='realized')
mode_choice_by_time_1_plot = plot_mode_choice_by_time(source=run1_mode_choice_by_time_source)
mode_choice_by_income_group_1_plot = plot_mode_choice_by_income_group(source=run1_mode_choice_by_income_group_source)
mode_choice_by_age_group_1_plot = plot_mode_choice_by_age_group(source=run1_mode_choice_by_age_group_source)
mode_choice_by_distance_1_plot = plot_mode_choice_by_distance(source=run1_mode_choice_by_distance_source)
congestion_travel_time_by_mode_1_plot = plot_congestion_travel_time_by_mode(source=run1_congestion_travel_time_by_mode_source)
congestion_travel_time_per_passenger_trip_1_plot = plot_congestion_travel_time_per_passenger_trip(source=run1_congestion_travel_time_per_passenger_trip_source)
congestion_miles_travelled_per_mode_1_plot = plot_congestion_miles_travelled_per_mode(source=run1_congestion_miles_travelled_per_mode_source)
congestion_bus_vmt_by_ridership_1_plot = plot_congestion_bus_vmt_by_ridership(source=run1_congestion_bus_vmt_by_ridership_source)
congestion_on_demand_vmt_by_phases_1_plot = plot_congestion_on_demand_vmt_by_phases(source=run1_congestion_on_demand_vmt_by_phases_source)
congestion_travel_speed_1_plot = plot_congestion_travel_speed(source=run1_congestion_travel_speed_source)
los_travel_expenditure_1_plot = plot_los_travel_expenditure(source=run1_los_travel_expenditure_source)
los_crowding_1_plot = plot_los_crowding(source=run1_los_crowding_source)
transit_cb_1_plot = plot_transit_cb(costs_source=run1_transit_cb_costs_source, benefits_source=run1_transit_cb_benefits_source)
transit_inc_by_mode_1_plot = plot_transit_inc_by_mode(source=run1_transit_inc_by_mode_source)
sustainability_25pm_per_mode_1_plot = plot_sustainability_25pm_per_mode(source=run1_sustainability_25pm_per_mode_source)

normalized_scores_2_plot = plot_normalized_scores(source=run2_normalized_scores_source, num=2)
fleetmix_input_2_plot = plot_fleetmix_input(source=run2_fleetmix_input_source, num=2)
routesched_input_2_plot = plot_routesched_input(
    line_source=run2_routesched_input_line_source, 
    start_source=run2_routesched_input_start_source,
    end_source=run2_routesched_input_end_source, num=2)
fares_input_2_plot = plot_fares_input(source=run2_fares_input_source, num=2)
modeinc_input_2_plot = plot_modeinc_input(source=run2_modeinc_input_source, num=2)
mode_planned_pie_chart_2_plot = plot_mode_pie_chart(source=run2_mode_planned_pie_chart_source, choice_type='planned', num=2)
mode_realized_pie_chart_2_plot = plot_mode_pie_chart(source=run2_mode_realized_pie_chart_source, choice_type='realized', num=2)
mode_choice_by_time_2_plot = plot_mode_choice_by_time(source=run2_mode_choice_by_time_source, num=2)
mode_choice_by_income_group_2_plot = plot_mode_choice_by_income_group(source=run2_mode_choice_by_income_group_source, num=2)
mode_choice_by_age_group_2_plot = plot_mode_choice_by_age_group(source=run2_mode_choice_by_age_group_source, num=2)
mode_choice_by_distance_2_plot = plot_mode_choice_by_distance(source=run2_mode_choice_by_distance_source, num=2)
congestion_travel_time_by_mode_2_plot = plot_congestion_travel_time_by_mode(source=run2_congestion_travel_time_by_mode_source, num=2)
congestion_travel_time_per_passenger_trip_2_plot = plot_congestion_travel_time_per_passenger_trip(source=run2_congestion_travel_time_per_passenger_trip_source, num=2)
congestion_miles_travelled_per_mode_2_plot = plot_congestion_miles_travelled_per_mode(source=run2_congestion_miles_travelled_per_mode_source, num=2)
congestion_bus_vmt_by_ridership_2_plot = plot_congestion_bus_vmt_by_ridership(source=run2_congestion_bus_vmt_by_ridership_source, num=2)
congestion_on_demand_vmt_by_phases_2_plot = plot_congestion_on_demand_vmt_by_phases(source=run2_congestion_on_demand_vmt_by_phases_source, num=2)
congestion_travel_speed_2_plot = plot_congestion_travel_speed(source=run2_congestion_travel_speed_source, num=2)
los_travel_expenditure_2_plot = plot_los_travel_expenditure(source=run2_los_travel_expenditure_source, num=2)
los_crowding_2_plot = plot_los_crowding(source=run2_los_crowding_source, num=2)
transit_cb_2_plot = plot_transit_cb(costs_source=run2_transit_cb_costs_source, benefits_source=run2_transit_cb_benefits_source, num=2)
transit_inc_by_mode_2_plot = plot_transit_inc_by_mode(source=run2_transit_inc_by_mode_source, num=2)
sustainability_25pm_per_mode_2_plot = plot_sustainability_25pm_per_mode(source=run2_sustainability_25pm_per_mode_source, num=2)
##############################################

### Gather plot objects into lists ###
run1_inputs_plots = [
    fleetmix_input_1_plot,
    routesched_input_1_plot,
    fares_input_1_plot,
    modeinc_input_1_plot
]
run1_scores_plots = [normalized_scores_1_plot]
run1_outputs_mode_plots = [
    mode_planned_pie_chart_1_plot,
    mode_realized_pie_chart_1_plot,
    mode_choice_by_time_1_plot,
    mode_choice_by_income_group_1_plot,
    mode_choice_by_age_group_1_plot,
    mode_choice_by_distance_1_plot
]
run1_outputs_congestion_plots = [
    congestion_travel_time_by_mode_1_plot,
    congestion_travel_time_per_passenger_trip_1_plot,
    congestion_miles_travelled_per_mode_1_plot,
    congestion_bus_vmt_by_ridership_1_plot,
    congestion_on_demand_vmt_by_phases_1_plot,
    congestion_travel_speed_1_plot
]
run1_outputs_los_plots = [
    los_travel_expenditure_1_plot,
    los_crowding_1_plot
]
run1_outputs_transitcb_plots = [
    transit_cb_1_plot,
    transit_inc_by_mode_1_plot
]
run1_outputs_sustainability_plots = [sustainability_25pm_per_mode_1_plot]

run2_inputs_plots = [
    fleetmix_input_2_plot,
    routesched_input_2_plot,
    fares_input_2_plot,
    modeinc_input_2_plot
]
run2_scores_plots = [normalized_scores_2_plot]
run2_outputs_mode_plots = [
    mode_planned_pie_chart_2_plot,
    mode_realized_pie_chart_2_plot,
    mode_choice_by_time_2_plot,
    mode_choice_by_income_group_2_plot,
    mode_choice_by_age_group_2_plot,
    mode_choice_by_distance_2_plot
]
run2_outputs_congestion_plots = [
    congestion_travel_time_by_mode_2_plot,
    congestion_travel_time_per_passenger_trip_2_plot,
    congestion_miles_travelled_per_mode_2_plot,
    congestion_bus_vmt_by_ridership_2_plot,
    congestion_on_demand_vmt_by_phases_2_plot,
    congestion_travel_speed_2_plot
]
run2_outputs_los_plots = [
    los_travel_expenditure_2_plot,
    los_crowding_2_plot
]
run2_outputs_transitcb_plots = [
    transit_cb_2_plot,
    transit_inc_by_mode_2_plot
]
run2_outputs_sustainability_plots = [sustainability_25pm_per_mode_2_plot]
######################################

inputs_plots = row(column(run1_inputs_plots), column(run2_inputs_plots))
scores_plots = column(column(run1_scores_plots), column(run2_scores_plots))
outputs_mode_plots = row(column(run1_outputs_mode_plots), column(run2_outputs_mode_plots))
outputs_los_plots = row(column(run1_outputs_los_plots), column(run2_outputs_los_plots))
outputs_congestion_plots = row(column(run1_outputs_congestion_plots), column(run2_outputs_congestion_plots))
outputs_transitcb_plots = row(column(run1_outputs_transitcb_plots), column(run2_outputs_transitcb_plots))
outputs_sustainability_plots = row(column(run1_outputs_sustainability_plots), column(run2_outputs_sustainability_plots))

run1_select = Select(value='{}/{}'.format(scenario_key, run1_key),
                     title='Run 1', 
                     options=sorted(runs))
run2_select = Select(value='{}/{}'.format(scenario_key, run2_key),
                     title='Run 2', 
                     options=sorted(runs))

pulldowns = row(run1_select, run2_select)

run1_select.on_change('value', update_run1)
run2_select.on_change('value', update_run2)

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