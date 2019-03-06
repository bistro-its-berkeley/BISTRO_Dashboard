import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd 

from contestant import Contestant

EXTERNAL_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def get_data(contestant, from_csv=False):

    if from_csv:
        activities_df = pd.read_csv('data/{}/activities_dataframe.csv'.format(contestant))
        households_df = pd.read_csv('data/{}/households_dataframe.csv'.format(contestant))
        legs_df = pd.read_csv('data/{}/legs_dataframe.csv'.format(contestant))
        paths_df = pd.read_csv('data/{}/path_traversals_dataframe.csv'.format(contestant))
        persons_df = pd.read_csv('data/{}/persons_dataframe.csv'.format(contestant))
        trips_df = pd.read_csv('data/{}/trips_dataframe.csv'.format(contestant))
    else:
        pass

    return activities_df, households_df, legs_df, paths_df, persons_df, trips_df

def main():    

    app = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)

    dropdown_options = [{'label': 'Leader {}'.format(n+1), 'value': 'leader_{}'.format(n+1)} for n in xrange(10)]
    dropdown_options.append({'label': 'Example Run', 'value': 'example_run'})

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
                    options=dropdown_options + [{'label': 'BAU', 'value': 'bau'}],
                    value='bau'
                ),
                style={'width': '48%', 'float': 'right', 'display': 'inline-block'})]),

        html.Div([
            html.Div(dcc.Graph(id='graph-1'), className="three columns"),
            html.Div(dcc.Graph(id='graph-2'), className="three columns"),
            html.Div(dcc.Graph(id='graph-3'), className="three columns"),
            html.Div(dcc.Graph(id='graph-4'), className="three columns")
        ], className="row"),
        html.Div([
            html.Div(dcc.Graph(id='graph-5'), className="three columns"),
            html.Div(dcc.Graph(id='graph-6'), className="three columns"),
            html.Div(dcc.Graph(id='graph-7'), className="three columns"),
            html.Div(dcc.Graph(id='graph-8'), className="three columns")
        ], className="row"),

        # hidden intermediate value
        html.Div(id='intermediate-value', style={'display': 'none'})
    ])

    @app.callback(
        dash.dependencies.Output('intermediate-value', 'children'), 
        [dash.dependencies.Input('dropdown-a', 'value'), dash.dependencies.Input('dropdown-b', 'value')])
    def pull_dfs(value_a, value_b):
        '''
        This function pulls the data and generates the Contestant classes.

        Whenever the dropdown menus are accessed, this will automatically rerun
        and pull the correct datasets.

        Parameters
        ----------
        value_a : str (which contestant is a)
        value_b : str (which contestant is b)

        Returns
        -------
        list of Contestant classes (contestant_a and contestant_b)
        '''
        dfs_a = get_data(contestant=value_a, from_csv=True)
        dfs_b = get_data(contestant=value_b, from_csv=True)
        contestant_a = Contestant(dfs=dfs_a)
        contestant_b = Contestant(dfs=dfs_b)
        return [contestant_a, contestant_b]

    @app.callback(
        dash.dependencies.Output('graph-1', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_travel_speed_by_mode_comparison(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_travel_speed_by_mode_comparison(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-2', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_2(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_2(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-3', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_3(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_3(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-4', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_4(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_4(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-5', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_5(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_5(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-6', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_6(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_6(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-7', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_7(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_7(contestant_b)

    @app.callback(
        dash.dependencies.Output('graph-8', 'figure'), 
        [dash.dependencies.Input('intermediate-value', 'children')])
    def update_graph_8(contestant_list):
        contestant_a, contestant_b = contestant_list
        return contestant_a.plot_8(contestant_b)

    app.run_server(debug=True)

if __name__ == '__main__':
    main()
