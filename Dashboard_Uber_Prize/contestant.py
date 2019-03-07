import matplotlib as mpl
mpl.use('Agg')

from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt
import numpy as np 
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
        self.activities_df, self.households_df, self.legs_df, self.paths_df, self.persons_df, self.trips_df, self.frequency_df, self.fares_df, self.incentives_df, self.fleet_df = dfs

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

    def splitting_min_max(self, df, name_column):
        """ Parsing and splitting the ranges in the "age" (or "income") columns into two new columns:
        "min_age" (or "min_income") with the bottom value of the range and "max_age" (or "max_income") with the top value
        of the range. Ex: [0:120] --> 0, 120

        Parameters
        ----------
        df: pandas dataframe
            ModeIncentives.csv or MassTransitFares.csv input file

        name_column: str
            Column containing the range values to parse

        Returns
        -------
        df: pandas dataframe
            New input dataframe with two "min" and "max" columns with floats int values instead of ranges values

        """
        # Parsing the ranges and creating two new columns with the min and max values of the range
        if df.empty:
            df["min_{0}".format(name_column)] = [0]
            df["max_{0}".format(name_column)] = [0]
        else:
            min_max = df[name_column].str.replace("[", "").str.replace("]", "").str.replace("(", "").str.replace(")", "")\
                .str.split(":", expand=True)
            df["min_{0}".format(name_column)] = min_max.iloc[:, 0].astype(int)
            df["max_{0}".format(name_column)] = min_max.iloc[:, 1].astype(int)

        return df

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

    def plot_incentives_input(self, max_incentive=50, max_age=120, max_income=150000):
        incentives = self.incentives_df
        incentives["amount"] = incentives["amount"].astype(float)

        # Completing the dataframe with the missing subsidized modes (so that they appear in the plot)
        df = pd.DataFrame(["", "(0:0)", "(0:0)", 0.00]).T
        df.columns = ["mode", "age", "income", "amount"]

        modes = ["drive_transit", "walk_transit", "OnDemand_ride"]
        for mode in modes:
            if mode not in incentives["mode"].values:
                df["mode"] = mode
                incentives = incentives.append(df)

        # Splitting age and income columns
        self.splitting_min_max(incentives, "age")
        self.splitting_min_max(incentives, "income")

        # Creating a new column with normalized incentives amount for the colormap
        if np.max(incentives["amount"]) == 0:
            incentives["amount_normalized"] = 0
        else:
            incentives["amount_normalized"] = incentives["amount"] / max_incentive

        incentives["amount_normalized"] = incentives["amount_normalized"].astype('float')
        incentives = incentives.drop(labels=["age", "income"], axis=1)

        # Changing the type of the "mode" column to 'category' to reorder the modes
        incentives["mode"] = incentives["mode"].astype('category').cat.reorder_categories([
            'OnDemand_ride',
            'drive_transit',
            'walk_transit'])

        incentives = incentives.sort_values(by="mode")

        fig, ax = plt.subplots(1, 2, figsize=(14, 4), sharey=True, gridspec_kw={'width_ratios': [4, 5]})

        # color map
        my_cmap = plt.cm.get_cmap('YlOrRd')
        colors = my_cmap(incentives["amount_normalized"])

        # plot
        ax[0].barh(incentives["mode"], incentives["max_age"] - incentives["min_age"], left=incentives["min_age"], color=colors)
        ax[1].barh(incentives["mode"], incentives["max_income"]-incentives["min_income"], left=incentives["min_income"], color=colors)

        ax[0].set_xlabel("age", fontsize=14)
        ax[0].set_xlim((0, max_age))

        ax[1].set_xlabel("income", fontsize=14)
        ax[1].set_xlim((0, max_income))

        ax[0].set_title("Incentives by age group", fontsize=15)
        ax[1].set_title("Incentives by income group", fontsize=15)

        sm = ScalarMappable(cmap=my_cmap, norm=plt.Normalize(0, np.max(incentives["amount"])))
        sm.set_array([])
        sm.set_clim(0, max_incentive)
        cbar = fig.colorbar(sm, ticks=[i for i in range(0, max_incentive + 1, 10)])
        cbar.set_label('Incentive amount [$/person-trip]', rotation=270, labelpad=25)

        plotly_fig = tls.mpl_to_plotly(fig)
        return plotly_fig

    def plot_5(self, contestant_b):
        pass

    def plot_6(self, contestant_b):
        pass

# TODO:
# checkboxes to toggle on/off various div's
# static image upload example
# add in xml parser function