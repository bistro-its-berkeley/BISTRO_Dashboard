import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from contestant import Contestant

EXTERNAL_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def get_data(contestant, from_csv=False):

    if from_csv:
        frequency_df = pd.read_csv('data/{}/submission-inputs/FrequencyAdjustment.csv'.format(contestant))
        fares_df = pd.read_csv('data/{}/submission-inputs/MassTransitFares.csv'.format(contestant))
        incentives_df = pd.read_csv('data/{}/submission-inputs/ModeIncentives.csv'.format(contestant))
        fleet_df = pd.read_csv('data/{}/submission-inputs/VehicleFleetMix.csv'.format(contestant))

        activities_df = pd.read_csv('data/{}/activities_dataframe.csv'.format(contestant))
        households_df = pd.read_csv('data/{}/households_dataframe.csv'.format(contestant))
        legs_df = pd.read_csv('data/{}/legs_dataframe.csv'.format(contestant))
        paths_df = pd.read_csv('data/{}/path_traversals_dataframe.csv'.format(contestant))
        persons_df = pd.read_csv('data/{}/persons_dataframe.csv'.format(contestant))
        trips_df = pd.read_csv('data/{}/trips_dataframe.csv'.format(contestant))
    else:
        pass

    return activities_df, households_df, legs_df, paths_df, persons_df, trips_df, frequency_df, fares_df, incentives_df, fleet_df

def main():    

    app = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)

    dropdown_options = [{'label': 'Leader {}'.format(n+1), 'value': 'leader_{}'.format(n+1)} for n in xrange(10)]
    dropdown_options.append({'label': 'Example Run', 'value': 'example_run'})
    dropdown_options.append({'label': 'BAU', 'value': 'bau'})

    contestant_dict = {}
    for value, label in {inner_dict['value']: inner_dict['label'] for inner_dict in dropdown_options}.iteritems():
        try:
            dfs = get_data(value, from_csv=True)
            contestant_dict[value] = Contestant(name=label, dfs=dfs)
        except:
            continue

    app.layout = html.Div(children=[
        html.H1(children='Contestant Visualization Dashboard'),

        html.Div(children='''
            Select contestants below for pairwise comparison.
        '''),

        html.Div([
            html.Div(
                dcc.Dropdown(
                    id='dropdown-a',
                    options=dropdown_options,
                    value='example_run'
                ),
                style={'width': '48%', 'display': 'inline-block'}),
            html.Div(
                dcc.Dropdown(
                    id='dropdown-b',
                    options=dropdown_options,
                    value='bau'
                ),
                style={'width': '48%', 'float': 'right', 'display': 'inline-block'})]),

        html.Div([
            dcc.Tabs(id="tabs", value='tab-inputs', children=[
                dcc.Tab(label='Scores Overview', value='tab-scores'),
                dcc.Tab(label='Inputs', value='tab-inputs'),
                dcc.Tab(label='Outputs', value='tab-outputs'),
            ]),
            dcc.Checklist(id='checkboxes', values=['mode', 'inc'], labelStyle={'display': 'inline-block'})
        ]),

        # Scores: normalized scores
        html.Div([
            html.Div(dcc.Graph(id='score-graph-1'), className="six columns"),
        ], id='score-div', className="row"),
        # Inputs: bar charts of fleet mix, route schedules, fares, mode incentives
        html.Div([
            html.Div([
                html.Div(dcc.Graph(id='inputs-fleetmix-graph-a'), className="six columns"),
                html.Div(dcc.Graph(id='inputs-fleetmix-graph-b'), className="six columns"),
            ], id='fleetmix-div', className="row"),
            html.Div([
                html.Div(dcc.Graph(id='inputs-routesched-graph-a'), className="six columns"),
                html.Div(dcc.Graph(id='inputs-routesched-graph-b'), className="six columns"),
            ], id='routessched-div', className="row"),
            html.Div([
                html.Div(dcc.Graph(id='inputs-fares-graph-a'), className="six columns"),
                html.Div(dcc.Graph(id='inputs-fares-graph-b'), className="six columns"),
            ], id='fares-div', className="row"),
            html.Div([
                html.Div(dcc.Graph(id='inputs-modeinc-graph-a'), className="six columns"),
                html.Div(dcc.Graph(id='inputs-modeinc-graph-b'), className="six columns"),
            ], id='modeinc-div', className="row")
        ], id='inputs-div', className="row"),
        # Outputs: Mode Choice, Congestion, Level of Service, Mass Transit C/B, Sustainability
        html.Div([
            # Mode Choice
            html.Div([
                html.Div([
                    html.Div(dcc.Graph(id='outputs-mode-pie-chart-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-mode-pie-chart-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-mode-by-time-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-mode-by-time-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-mode-by-distance-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-mode-by-distance-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-mode-by-age-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-mode-by-age-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-mode-by-income-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-mode-by-income-b'), className="six columns"),
                ], className="row"),
            ], id='mode-div'),
            # Congestion
            html.Div([
                html.Div([
                    html.Div(dcc.Graph(id='outputs-congestion-travel-speed-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-congestion-travel-speed-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-congestion-total-vmt-by-mode-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-congestion-total-vmt-by-mode-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-congestion-on-demand-vmt-by-phases-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-congestion-on-demand-vmt-by-phases-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-congestion-bus-vmt-by-ridership-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-congestion-bus-vmt-by-ridership-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-congestion-delay-per-passenger-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-congestion-delay-per-passenger-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-congestion-delay-per-vehicle-type-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-congestion-delay-per-vehicle-type-b'), className="six columns"),
                ], className="row"),
            ], id='congestion-div'),
            # Level of Service
            html.Div([
                html.Div([
                    html.Div(dcc.Graph(id='outputs-los-crowding-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-los-crowding-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-los-num-passengers-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-los-num-passengers-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-los-travel-expenditure-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-los-travel-expenditure-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-los-od-matrix-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-los-od-matrix-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-los-boarding-alighting-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-los-boarding-alighting-b'), className="six columns"),
                ], className="row"),
            ], id='los-div'),
            # Mass Transit C/B
            html.Div([
                html.Div([
                    html.Div(dcc.Graph(id='outputs-transit-cb-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-transit-cb-b'), className="six columns"),
                ], className="row"),
                html.Div([
                    html.Div(dcc.Graph(id='outputs-transit-inc-by-mode-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-transit-inc-by-mode-b'), className="six columns"),
                ], className="row"),
            ], id='transit-div'),
            # Sustainability
            html.Div([
                html.Div([
                    html.Div(dcc.Graph(id='outputs-sustainability-25pm-per-mode-a'), className="six columns"),
                    html.Div(dcc.Graph(id='outputs-sustainability-25pm-per-mode-b'), className="six columns"),
                ], className="row")
            ], id='sustainability-div')
        ], id='outputs-div')
    ])

    @app.callback(
        dash.dependencies.Output('checkboxes', 'options'),
        [dash.dependencies.Input('tabs', 'value')])
    def render_content(tab):
        if tab == 'tab-scores':
            return []
        elif tab == 'tab-inputs':
            return [
                    {'label': 'Frequency', 'value': 'freq'},
                    {'label': 'Fares', 'value': 'fares'},
                    {'label': 'Incentives', 'value': 'inc'},
                    {'label': 'Fleet Mix', 'value': 'fleet'}
                ]
        elif tab == 'tab-outputs':
            return [
                    {'label': 'Mode', 'value': 'mode'},
                    {'label': 'Congestion', 'value': 'congestion'},
                    {'label': 'Level of Service', 'value': 'los'},
                    {'label': 'Mass Transit C/B', 'value': 'transit'},
                    {'label': 'Sustainability', 'value': 'sustainability'},
                ]
    #######################################################################

    ############################### TOGGLES ###############################
    @app.callback(
        dash.dependencies.Output('score-div', 'style'),
        [dash.dependencies.Input('tabs', 'value')])
    def render_content(tab):
        if tab == 'tab-scores':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('fleetmix-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-inputs' and 'fleet' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('routessched-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-inputs' and 'freq' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('fares-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-inputs' and 'fares' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('modeinc-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-inputs' and 'inc' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('mode-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-outputs' and 'mode' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('congestion-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-outputs' and 'congestion' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('los-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-outputs' and 'los' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('transit-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-outputs' and 'transit' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}

    @app.callback(
        dash.dependencies.Output('sustainability-div', 'style'),
        [dash.dependencies.Input('tabs', 'value'), dash.dependencies.Input('checkboxes', 'values')])
    def render_content(tab, checklist):
        if tab == 'tab-outputs' and 'sustainability' in checklist:
            return {'display': 'initial'}
        else:
            return {'display': 'none'}
    ######################################################################

    ############################ INPUT GRAPHS ############################
    # @app.callback(
    #     dash.dependencies.Output('inputs-fleetmix-graph-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_fleetmix_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-fleetmix-graph-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_fleetmix_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-routesched-graph-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_routesched_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-routesched-graph-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_routesched_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-fares-graph-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_fares_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-fares-graph-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_fares_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-modeinc-graph-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_modeinc_input()

    # @app.callback(
    #     dash.dependencies.Output('inputs-modeinc-graph-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_modeinc_input()
    ######################################################################

    ########################### OUTPUT GRAPHS ###########################
    # @app.callback(
    #     dash.dependencies.Output('outputs-mode-pie-chart-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_mode_pie_chart()
    
    # @app.callback(
    #     dash.dependencies.Output('outputs-mode-pie-chart-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_mode_pie_chart()

    # @app.callback(
    #     dash.dependencies.Output('outputs-mode-by-time-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_mode_choice_by_time()

    # @app.callback(
    #     dash.dependencies.Output('outputs-mode-by-time-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_mode_choice_by_time()

    # @app.callback(
    #     dash.dependencies.Output('outputs-mode-by-distance-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_mode_choice_by_distance()

    # @app.callback(
    #     dash.dependencies.Output('outputs-mode-by-distance-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_mode_choice_by_distance()

    @app.callback(
        dash.dependencies.Output('outputs-mode-by-age-a', 'figure'), 
        [dash.dependencies.Input('dropdown-a', 'value')])
    def update_graph1(value):
        return contestant_dict[value].plot_mode_choice_by_age_group()

    @app.callback(
        dash.dependencies.Output('outputs-mode-by-age-b', 'figure'), 
        [dash.dependencies.Input('dropdown-b', 'value')])
    def update_graph2(value):
        return contestant_dict[value].plot_mode_choice_by_age_group()

    @app.callback(
        dash.dependencies.Output('outputs-mode-by-income-a', 'figure'), 
        [dash.dependencies.Input('dropdown-a', 'value')])
    def update_graph3(value):
        return contestant_dict[value].plot_mode_choice_by_income_group()

    @app.callback(
        dash.dependencies.Output('outputs-mode-by-income-b', 'figure'), 
        [dash.dependencies.Input('dropdown-b', 'value')])
    def update_graph4(value):
        return contestant_dict[value].plot_mode_choice_by_income_group()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-travel-speed-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_travel_speed()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-travel-speed-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_travel_speed()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-total-vmt-by-mode-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_total_vmt_by_mode()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-total-vmt-by-mode-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_total_vmt_by_mode()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-on-demand-vmt-by-phases-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_on_demand_vmt_by_phases()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-on-demand-vmt-by-phases-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_on_demand_vmt_by_phases()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-bus-vmt-by-ridership-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_bus_vmt_by_ridership()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-bus-vmt-by-ridership-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_bus_vmt_by_ridership()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-delay-per-passenger-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_delay_per_passenger()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-delay-per-passenger-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_delay_per_passenger()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-delay-per-vehicle-type-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_delay_per_vehicle_type()

    # @app.callback(
    #     dash.dependencies.Output('outputs-congestion-delay-per-vehicle-type-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_congestion_delay_per_vehicle_type()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-crowding-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_crowding()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-crowding-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_crowding()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-num-passengers-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_num_passengers()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-num-passengers-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_num_passengers()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-travel-expenditure-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_travel_expenditure()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-travel-expenditure-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_travel_expenditure()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-od-matrix-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_od_matrix()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-od-matrix-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_od_matrix()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-boarding-alighting-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_boarding_alighting()

    # @app.callback(
    #     dash.dependencies.Output('outputs-los-boarding-alighting-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_los_boarding_alighting()

    # @app.callback(
    #     dash.dependencies.Output('outputs-transit-cb-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_transit_cb()

    # @app.callback(
    #     dash.dependencies.Output('outputs-transit-cb-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_transit_cb()

    # @app.callback(
    #     dash.dependencies.Output('outputs-transit-inc-by-mode-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_transit_inc_by_mode()

    # @app.callback(
    #     dash.dependencies.Output('outputs-transit-inc-by-mode-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_transit_inc_by_mode()

    # @app.callback(
    #     dash.dependencies.Output('outputs-sustainability-25pm-per-mode-a', 'figure'), 
    #     [dash.dependencies.Input('dropdown-a', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_sustainability_25pm_per_mode()

    # @app.callback(
    #     dash.dependencies.Output('outputs-sustainability-25pm-per-mode-b', 'figure'), 
    #     [dash.dependencies.Input('dropdown-b', 'value')])
    # def update_graph(value):
    #     return contestant_dict[value].plot_sustainability_25pm_per_mode()
    ######################################################################

    app.run_server(debug=True)

if __name__ == '__main__':
    main()
