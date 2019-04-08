from os import listdir
from os.path import dirname, join

import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column, layout, widgetbox
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.models.widgets import CheckboxButtonGroup, Div, Panel, Tabs
from bokeh.plotting import figure, show

from scenario import Scenario

def update_scenario1(attrname, old, new):
    scenario1 = Scenario(name=new)
    scenario1_inputs_plots, scenario1_scores_plots, scenario1_outputs_mode_plots, scenario1_outputs_congestion_plots, scenario1_outputs_los_plots, scenario1_outputs_transitcb_plots, scenario1_outputs_sustainability_plots = scenario1.make_all_plots()
    inputs_plots.children[0] = column(scenario1_inputs_plots)
    scores_plots.children[0] = column(scenario1_scores_plots)
    outputs_mode_plots.children[0] = column(scenario1_outputs_mode_plots)
    outputs_congestion_plots.children[0] = column(scenario1_outputs_congestion_plots)
    outputs_los_plots.children[0] = column(scenario1_outputs_los_plots)
    outputs_transitcb_plots.children[0] = column(scenario1_outputs_transitcb_plots)
    outputs_sustainability_plots.children[0] = column(scenario1_outputs_sustainability_plots)

def update_scenario2(attrname, old, new):
    scenario2 = Scenario(name=new)
    scenario2_inputs_plots, scenario2_scores_plots, scenario2_outputs_mode_plots, scenario2_outputs_congestion_plots, scenario2_outputs_los_plots, scenario2_outputs_transitcb_plots, scenario2_outputs_sustainability_plots = scenario2.make_all_plots()
    inputs_plots.children[1] = column(scenario2_inputs_plots)
    scores_plots.children[1] = column(scenario2_scores_plots)
    outputs_mode_plots.children[1] = column(scenario2_outputs_mode_plots)
    outputs_congestion_plots.children[1] = column(scenario2_outputs_congestion_plots)
    outputs_los_plots.children[1] = column(scenario2_outputs_los_plots)
    outputs_transitcb_plots.children[1] = column(scenario2_outputs_transitcb_plots)
    outputs_sustainability_plots.children[1] = column(scenario2_outputs_sustainability_plots)

# def update_output_plots(new):
#     scenario1_outputs_plots = []
#     scenario2_outputs_plots = []

#     if 0 in checkbox_button_group.active:
#         scenario1_outputs_plots.append(scenario1_outputs_mode_plots)
#         scenario2_outputs_plots.append(scenario2_outputs_mode_plots)

#     if 1 in checkbox_button_group.active:
#         scenario1_outputs_plots.append(scenario1_outputs_congestion_plots)
#         scenario2_outputs_plots.append(scenario2_outputs_congestion_plots)

#     if 2 in checkbox_button_group.active:
#         scenario1_outputs_plots.append(scenario1_outputs_los_plots)
#         scenario2_outputs_plots.append(scenario2_outputs_los_plots)

#     if 3 in checkbox_button_group.active:
#         scenario1_outputs_plots.append(scenario1_outputs_transitcb_plots)
#         scenario2_outputs_plots.append(scenario2_outputs_transitcb_plots)

#     if 4 in checkbox_button_group.active:
#         scenario1_outputs_plots.append(scenario1_outputs_sustainability_plots)
#         scenario2_outputs_plots.append(scenario2_outputs_sustainability_plots)

#     outputs_plots = row(column(scenario1_outputs_plots), column(scenario2_outputs_plots))

title_div = Div(text="<img src='Dashboard_Uber_Prize/static/uber.svg' height='18'><b>Prize Visualization Dashboard</b>", width=800, height=10, style={'font-size': '200%'})


path = join(dirname(__file__), 'data/submissions/')
scenarios = [file for file in listdir(path) if '.' not in file and file != '.DS_Store']

if 'warm-start' in scenarios:
    scenario1_key = 'warm-start'
else:
    scenario1_key = scenarios[0]

if 'example_run' in scenarios:
    scenario2_key = 'example_run'
else:
    scenario2_key = scenarios[1]

scenario1 = Scenario(name=scenario1_key)
scenario1_inputs_plots, scenario1_scores_plots, scenario1_outputs_mode_plots, scenario1_outputs_congestion_plots, scenario1_outputs_los_plots, scenario1_outputs_transitcb_plots, scenario1_outputs_sustainability_plots = scenario1.make_all_plots()
# print(scenario1_inputs_plots[0].children[1].source)

scenario2 = Scenario(name=scenario2_key)
scenario2_inputs_plots, scenario2_scores_plots, scenario2_outputs_mode_plots, scenario2_outputs_congestion_plots, scenario2_outputs_los_plots, scenario2_outputs_transitcb_plots, scenario2_outputs_sustainability_plots = scenario2.make_all_plots()

inputs_plots = row(column(scenario1_inputs_plots), column(scenario2_inputs_plots))
scores_plots = column(column(scenario1_scores_plots), column(scenario2_scores_plots))
outputs_mode_plots = row(column(scenario1_outputs_mode_plots), column(scenario2_outputs_mode_plots))
outputs_los_plots = row(column(scenario1_outputs_los_plots), column(scenario2_outputs_los_plots))
outputs_congestion_plots = row(column(scenario1_outputs_congestion_plots), column(scenario2_outputs_congestion_plots))
outputs_transitcb_plots = row(column(scenario1_outputs_transitcb_plots), column(scenario2_outputs_transitcb_plots))
outputs_sustainability_plots = row(column(scenario1_outputs_sustainability_plots), column(scenario2_outputs_sustainability_plots))

scenario1_select = Select(value=scenario1_key, title='Scenario 1', options=sorted(scenarios))
scenario2_select = Select(value=scenario2_key, title='Scenario 2', options=sorted(scenarios))

pulldowns = row(scenario1_select, scenario2_select)

# checkbox_button_group = CheckboxButtonGroup(
#         labels=["Mode Choice", "Congestion", "Level of Service", "Transit C/B", "Sustainability"], active=[0])

scenario1_select.on_change('value', update_scenario1)
scenario2_select.on_change('value', update_scenario2)
# checkbox_button_group.on_click(update_output_plots)

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