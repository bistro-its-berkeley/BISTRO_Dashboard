import matplotlib as mpl
mpl.use('Agg')

from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 
from plotly import offline
import plotly.graph_objs as go
import plotly.tools as tls
# import plotly.plotly as py
import pprint
import seaborn as sns 

class Contestant():

    def __init__(self, name, dfs):
        """
        Initialize class object.

        Parameters
        ----------
        name : str
        dfs : list of pd.DataFrame

        Returns
        -------
        None
        """
        self.name = name
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

    def showgrid(self, plotly_fig, y_gridwidth):
        plotly_fig['layout']['xaxis']['showgrid'] = True
        plotly_fig['layout']['yaxis']['showgrid'] = True
        plotly_fig['layout']['yaxis']['gridwidth'] = y_gridwidth
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

    def plot_normalized_scores(self):
        pass

    def plot_fleetmix_input(self):
        pass

    def plot_routesched_input(self):
        pass

    def plot_fares_input(self):
        pass

    def plot_modeinc_input(self, max_incentive=50, max_age=120, max_income=150000):
        pass
        # incentives = self.incentives_df
        # incentives["amount"] = incentives["amount"].astype(float)

        # # Completing the dataframe with the missing subsidized modes (so that they appear in the plot)
        # df = pd.DataFrame(["", "(0:0)", "(0:0)", 0.00]).T
        # df.columns = ["mode", "age", "income", "amount"]

        # modes = ["drive_transit", "walk_transit", "OnDemand_ride"]
        # for mode in modes:
        #     if mode not in incentives["mode"].values:
        #         df["mode"] = mode
        #         incentives = incentives.append(df)

        # # Splitting age and income columns
        # self.splitting_min_max(incentives, "age")
        # self.splitting_min_max(incentives, "income")

        # # Creating a new column with normalized incentives amount for the colormap
        # if np.max(incentives["amount"]) == 0:
        #     incentives["amount_normalized"] = 0
        # else:
        #     incentives["amount_normalized"] = incentives["amount"] / max_incentive

        # incentives["amount_normalized"] = incentives["amount_normalized"].astype('float')
        # incentives = incentives.drop(labels=["age", "income"], axis=1)

        # # Changing the type of the "mode" column to 'category' to reorder the modes
        # incentives["mode"] = incentives["mode"].astype('category').cat.reorder_categories([
        #     'OnDemand_ride',
        #     'drive_transit',
        #     'walk_transit'])

        # incentives = incentives.sort_values(by="mode")

        # fig, ax = plt.subplots(1, 2, figsize=(7, 4), sharey=True, gridspec_kw={'width_ratios': [4, 5]})

        # # color map
        # my_cmap = plt.cm.get_cmap('YlOrRd')
        # colors = my_cmap(incentives["amount_normalized"])

        # # plot
        # ax[0].barh(incentives["mode"], incentives["max_age"] - incentives["min_age"], left=incentives["min_age"], color=colors)
        # ax[1].barh(incentives["mode"], incentives["max_income"] - incentives["min_income"], left=incentives["min_income"], color=colors)

        # ax[0].set_xlabel("age", fontsize=14)
        # ax[0].set_xlim((0, max_age))

        # ax[1].set_xlabel("income", fontsize=14)
        # ax[1].set_xlim((0, max_income))

        # ax[0].set_title("Incentives by age group", fontsize=15)
        # ax[1].set_title("Incentives by income group", fontsize=15)

        # sm = ScalarMappable(cmap=my_cmap, norm=plt.Normalize(0, np.max(incentives["amount"])))
        # sm.set_array([])
        # sm.set_clim(0, max_incentive)
        # cbar = fig.colorbar(sm, ticks=[i for i in range(0, max_incentive + 1, 10)])
        # cbar.set_label('Incentive amount [$/person-trip]', rotation=270, labelpad=25)

        # plotly_fig = tls.mpl_to_plotly(fig)
        # plotly_fig = self.showgrid(plotly_fig, y_gridwidth=1)
        # return plotly_fig

    def plot_mode_pie_chart(self):
        pass

    def plot_mode_choice_by_time(self):
        pass

    def plot_mode_choice_by_distance(self):
        pass

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

        # fig, ax = plt.subplots(figsize=(7, 4))
        # sns.barplot(data=grouped, x="realizedTripMode", y="num_people", hue="age_group")
        # self.change_bar_width(ax, 1.0)
        # ax.set_xlabel('Trip Mode', fontsize=14)
        # ax.set_ylabel('Number of People', fontsize=14)
        # ax.legend(title="Age group", bbox_to_anchor=(1.0, 1.01))
        # ax.set_title("Mode choice by age group - {}".format(self.name), fontsize=15)

        # plotly_fig = tls.mpl_to_plotly(fig)
        # plotly_fig = self.set_xticklabels(plotly_fig, grouped['realizedTripMode'].unique())
        # plotly_fig = self.showgrid(plotly_fig, y_gridwidth=1)
        # return plotly_fig

        group_dict = {float(group[1:].split(',')[0]): group for group in grouped['age_group'].unique()}
        sorted_keys = sorted([float(group[1:].split(',')[0]) for group in grouped['age_group'].unique()])
        groups = [group_dict[key] for key in sorted_keys]
        return {
            'data': [go.Bar(
                x=grouped[grouped['age_group'] == group]['realizedTripMode'].values, 
                y=grouped[grouped['age_group'] == group]['num_people'].values,
                name=group
                ) for group in groups
            ],
            'layout': go.Layout(
                title='Mode choice by age group - {}'.format(self.name),
                xaxis={
                    'title': 'Trip Mode',
                    'showgrid': True
                },
                yaxis={
                    'title': 'Number of People',
                    'showgrid': True
                }
            )
        }

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

        # fig, ax = plt.subplots(figsize=(7, 4))
        # sns.barplot(data=grouped, x="realizedTripMode", y="num_people", hue="income_group")
        # self.change_bar_width(ax, 1.0)
        # ax.set_xlabel('Trip Mode', fontsize=14)
        # ax.set_ylabel('Number of People', fontsize=14)
        # ax.legend(title="Income group", bbox_to_anchor=(1.0, 1.01))
        # ax.set_title("Mode choice by income group - {}".format(self.name), fontsize=15)

        # plotly_fig = tls.mpl_to_plotly(fig)
        # plotly_fig = self.set_xticklabels(plotly_fig, grouped['realizedTripMode'].unique())
        # plotly_fig = self.showgrid(plotly_fig, y_gridwidth=2000)
        # return plotly_fig
        
        group_dict = {float(group[1:].split(',')[0]): group for group in grouped['income_group'].unique()}
        sorted_keys = sorted([float(group[1:].split(',')[0]) for group in grouped['income_group'].unique()])
        groups = [group_dict[key] for key in sorted_keys]
        return {
            'data': [go.Bar(
                x=grouped[grouped['income_group'] == group]['realizedTripMode'].values, 
                y=grouped[grouped['income_group'] == group]['num_people'].values,
                name=group
                ) for group in groups
            ],
            'layout': go.Layout(
                title='Mode choice by income group - {}'.format(self.name),
                xaxis={
                    'title': 'Trip Mode',
                    'showgrid': True
                },
                yaxis={
                    'title': 'Number of People',
                    'showgrid': True
                }
            )
        }

    def plot_congestion_travel_speed(self):
        pass

    def plot_congestion_total_vmt_by_mode(self):
        pass

    def plot_congestion_on_demand_vmt_by_phases(self):
        pass

    def plot_congestion_bus_vmt_by_ridership(self):
        pass

    def plot_congestion_delay_per_passenger(self):
        pass

    def plot_congestion_delay_per_vehicle_type(self):
        pass

    def plot_los_crowding(self):
        pass

    def plot_los_num_passengers(self):
        pass

    def plot_los_travel_expenditure(self):
        pass

    def plot_los_od_matrix(self):
        pass

    def plot_los_boarding_alighting(self):
        pass

    def plot_transit_cb(self):
        pass

    def plot_transit_inc_by_mode(self):
        pass

    def plot_sustainability_25pm_per_mode(self):
        pass

# TODO:
# static image upload example
# add in xml parser function