import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd 
import plotly.graph_objs as go
import plotly.tools as tls
# import plotly.plotly as py
import pprint
import seaborn as sns 

class Contestant():

    def __init__(self, dfs):
        """
        Initialize class object.

        Parameters
        ----------
        dfs : list of pd.DataFrame

        Returns
        -------
        None
        """
        self.activities_df, self.households_df, self.legs_df, self.paths_df, self.persons_df, self.trips_df = dfs

    def change_bar_width(self, ax, new_value) :
        for patch in ax.patches:
            current_width = patch.get_width()
            diff = current_width - new_value

            # we change the bar width
            patch.set_width(new_value)

            # we recenter the bar
            patch.set_x(patch.get_x() + diff * .5)

    def set_xticklabels(self, plotly_fig, labels):
        plotly_fig['layout']['xaxis']['ticktext'] = labels
        plotly_fig['layout']['xaxis']['tickvals'] = range(len(labels))
        return plotly_fig

    def plot_travel_speed_by_mode_comparison(self, contestant_b):
        pass

    def plot_mode_choice_by_income_group(self):

        persons_cols = ['PID', 'income']
        trips_cols = ['PID', 'realizedTripMode']
        people_income_mode = self.persons_df[persons_cols].merge(self.trips_df[trips_cols], on=['PID'])
        people_income_mode['income_group'] = pd.cut(people_income_mode['income'],
                                                    [0, 10000, 25000, 50000, 75000, 100000, float('inf')],
                                                    right=False).astype(str)
        grouped = people_income_mode.groupby(by=['realizedTripMode', 'income_group']).agg('count').reset_index()

        # rename df column to num_people due to grouping
        grouped = grouped.rename(
            index=str, columns={'PID': 'num_people'})

        return {
            'data': [go.Bar(
                x=grouped[grouped['income_group'] == group]['realizedTripMode'].values, 
                y=grouped[grouped['income_group'] == group]['num_people'].values,
                name=group
                ) for group in grouped['income_group'].unique()
            ],
            'layout': go.Layout(
                title='Mode choice by income group',
                xaxis={
                    'title': 'Trip Mode'
                },
                yaxis={
                    'title': 'Number of People'
                }
            )
        }

    def plot_mode_choice_by_age_group(self):

        persons_cols = ['PID', 'Age']
        trips_cols = ['PID', 'realizedTripMode']
        people_age_mode = self.persons_df[persons_cols].merge(self.trips_df[trips_cols], on=['PID'])
        people_age_mode['age_group'] = pd.cut(people_age_mode['Age'],
                                              [0, 18, 30, 40, 50, 60, float('inf')],
                                              right=False).astype(str)
        grouped = people_age_mode.groupby(by=['realizedTripMode', 'age_group']).agg('count').reset_index()

        # rename df column to num_people due to grouping
        grouped = grouped.rename(
            index=str, columns={'PID': 'num_people'})

        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=grouped, x="realizedTripMode", y="num_people", hue="age_group")
        self.change_bar_width(ax, 1.0)
        ax.set_xlabel('Trip Mode', fontsize=14)
        ax.set_ylabel('Number of People', fontsize=14)
        ax.legend(title="Age group", bbox_to_anchor=(1.0, 1.01))
        ax.set_title("Mode choice by age group", fontsize=15)

        plotly_fig = tls.mpl_to_plotly(fig)
        plotly_fig = self.set_xticklabels(plotly_fig, grouped['realizedTripMode'].unique())
        return plotly_fig

        # return {
        #     'data': [go.Bar(
        #         x=grouped[grouped['age_group'] == group]['realizedTripMode'].values, 
        #         y=grouped[grouped['age_group'] == group]['num_people'].values,
        #         name=group
        #         ) for group in grouped['age_group'].unique()
        #     ],
        #     'layout': go.Layout(
        #         title='Mode choice by age group',
        #         xaxis={
        #             'title': 'Trip Mode'
        #         },
        #         yaxis={
        #             'title': 'Number of People'
        #         }
        #     )
        # }

    def plot_3(self, contestant_b):
        pass

    def plot_4(self, contestant_b):
        pass

    def plot_5(self, contestant_b):
        pass

    def plot_6(self, contestant_b):
        pass

# TODO:
# checkboxes to toggle on/off various div's
# add in xml parser function
# input example plot: travel time
# static image upload example