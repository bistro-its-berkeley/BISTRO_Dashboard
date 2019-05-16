import math
import numpy as np 
from os import listdir
from os.path import dirname, join
import pandas as pd 
# import seaborn as sns 

from bokeh.models import ColumnDataSource
from bokeh.palettes import Category10, Category20, Plasma256, YlOrRd

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
AGENCY_IDS = [217]
TRANSIT_SCALE_FACTOR = 0.1

def reset_index(df):
    '''Returns DataFrame with index as columns'''
    index_df = df.index.to_frame(index=False)
    df = df.reset_index(drop=True)
    #  In merge is important the order in which you pass the dataframes
    # if the index contains a Categorical. 
    # pd.merge(df, index_df, left_index=True, right_index=True) does not work
    return pd.merge(index_df, df, left_index=True, right_index=True)

class Run():

    def __init__(self, name, scenario):
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
        self.scenario = scenario
        self.modes = ['OnDemand_ride', 'car', 'drive_transit', 'walk', 'walk_transit']
        self.submissions_dir = join(dirname(__file__), 'data/submissions/{}/{}'.format(self.scenario, self.name))
        self.reference_dir = join(dirname(__file__), 'data/sioux_faux_bus_lines')
        self.get_data(from_csv=True)
        self.make_data_sources()

    def get_data(self, from_csv=False):

        if from_csv:
            self.frequency_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/FrequencyAdjustment.csv'))
            self.fares_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/MassTransitFares.csv'))
            self.incentives_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/ModeIncentives.csv'))
            self.fleet_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/VehicleFleetMix.csv'))

            self.scores_df = pd.read_csv(join(self.submissions_dir, 'competition/submissionScores.csv'))

            self.activities_df = pd.read_csv(join(self.submissions_dir, 'activities_dataframe.csv'))
            self.households_df = pd.read_csv(join(self.submissions_dir, 'households_dataframe.csv'))
            self.legs_df = pd.read_csv(join(self.submissions_dir, 'legs_dataframe.csv'))
            self.paths_df = pd.read_csv(join(self.submissions_dir, 'path_traversals_dataframe.csv'))
            self.persons_df = pd.read_csv(join(self.submissions_dir, 'persons_dataframe.csv'))
            self.trips_df = pd.read_csv(join(self.submissions_dir, 'trips_dataframe.csv'))
            self.mode_choice_df = pd.read_csv(join(self.submissions_dir, 'modeChoice.csv'))
            self.realized_mode_choice_df = pd.read_csv(join(self.submissions_dir, 'realizedModeChoice.csv'))

            path = join(self.submissions_dir, 'ITERS')
            iter_num = max([int(file.split('.')[1]) for file in listdir(path) if file != '.DS_Store'])
            path = join(path, 'it.{}'.format(iter_num))
            self.mode_choice_hourly_df = pd.read_csv(join(path, '{}.modeChoice.csv'.format(iter_num)), index_col=0).T
            self.travel_times_df = pd.read_csv(join(path, '{}.averageTravelTimes.csv'.format(iter_num)))

            self.seating_capacities = pd.read_csv(join(self.reference_dir, "availableVehicleTypes.csv"))[[
                "vehicleTypeId", "seatingCapacity"]].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]
            self.trip_to_route = pd.read_csv(join(self.reference_dir, "gtfs_data/trips.txt"))[[
                "trip_id", "route_id"]].set_index("trip_id", drop=True).T.to_dict('records')[0]
            self.operational_costs = pd.read_csv(join(self.reference_dir, "vehicleCosts.csv"))[[
                "vehicleTypeId", "opAndMaintCost"]].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]
        else:
            pass

    def make_data_sources(self):

        self.modeinc_input_data = self.make_modeinc_input_data()
        self.fleetmix_input_data = self.make_fleetmix_input_data()
        self.fares_input_data = self.make_fares_input_data()
        self.routesched_input_line_data, self.routesched_input_start_data, self.routesched_input_end_data = self.make_routesched_input_data()

        self.normalized_scores_data = self.make_normalized_scores_data()

        self.mode_planned_pie_chart_data = self.make_mode_pie_chart_data(self.mode_choice_df.copy())
        self.mode_realized_pie_chart_data = self.make_mode_pie_chart_data(self.realized_mode_choice_df.copy())
        self.mode_choice_by_time_data = self.make_mode_choice_by_time_data()
        self.mode_choice_by_age_group_data = self.make_mode_choice_by_age_group_data()
        self.mode_choice_by_income_group_data = self.make_mode_choice_by_income_group_data()
        self.mode_choice_by_distance_data = self.make_mode_choice_by_distance_data()

        self.congestion_travel_time_by_mode_data = self.make_congestion_travel_time_by_mode_data()
        self.congestion_travel_time_per_passenger_trip_data = self.make_congestion_travel_time_per_passenger_trip_data()
        self.congestion_miles_travelled_per_mode_data = self.make_congestion_miles_travelled_per_mode_data()
        self.congestion_bus_vmt_by_ridership_data = self.make_congestion_bus_vmt_by_ridership_data()
        self.congestion_on_demand_vmt_by_phases_data = self.make_congestion_on_demand_vmt_by_phases_data()
        self.congestion_travel_speed_data = self.make_congestion_travel_speed_data()

        self.los_travel_expenditure_data = self.make_los_travel_expenditure_data()
        self.los_crowding_data = self.make_los_crowding_data()

        self.transit_cb_costs_data, self.transit_cb_benefits_data = self.make_transit_cb_data()
        self.transit_inc_by_mode_data = self.make_transit_inc_by_mode_data()

        self.sustainability_25pm_per_mode_data = self.make_sustainability_25pm_per_mode_data()

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

    def make_normalized_scores_data(self):
        scores = self.scores_df
        scores = scores.loc[:,["Component Name","Weighted Score"]]
        scores.set_index("Component Name", inplace=True)
        #Drop the `submission score` row
        # scores.drop('Level of service: average OnDemand_ride wait times', axis = 0, inplace=True)
        scores.reset_index(inplace=True)

        scores["Component Name"] = scores["Component Name"].astype('category').cat.reorder_categories(CATEGORIES)

        scores = scores.sort_values(by="Component Name")

        palette = ["#4682b4"] * (len(scores)-1) + ["#000080"]
        scores.loc[:, 'color'] = palette

        min_score = min(scores['Weighted Score'].min(), 0.0) * 1.1
        max_score = max(scores['Weighted Score'].max(), 1.0) * 1.1

        data = scores.to_dict(orient='list')
        return data

    def make_fleetmix_input_data(self):

        fleet_mix = self.fleet_df

        if fleet_mix.empty:
            fleet_mix = pd.DataFrame(
                [[agency_id, "{}".format(route_id), "BUS-DEFAULT"] for route_id in ROUTE_IDS for agency_id in AGENCY_IDS],
                columns=["agencyId", "routeId", "vehicleTypeId"])

        df = pd.DataFrame([AGENCY_IDS[0], '1', BUSES_LIST[0]]).T
        df.columns = ["agencyId", "routeId", "vehicleTypeId"]

        # Adding the missing bus types in the dataframe so that they appear in the plot
        for bus in BUSES_LIST:
            if bus not in fleet_mix["vehicleTypeId"].values:
                df["vehicleTypeId"] = bus
                fleet_mix = fleet_mix.append(df)

        # Adding the missing bus routes in the dataframe so that they appear in the plot
        fleet_mix["routeId"] = fleet_mix["routeId"].astype(str)

        df = pd.DataFrame([AGENCY_IDS[0], "", BUSES_LIST[0]]).T
        df.columns = ["agencyId", "routeId", "vehicleTypeId"]

        for route in ROUTE_IDS:
            if route not in fleet_mix["routeId"].values:
                df["routeId"] = route
                fleet_mix = fleet_mix.append(df)

        # Reodering bus types starting by "BUS-DEFAULT" and then by ascending bus size order
        fleet_mix["vehicleTypeId"] = fleet_mix["vehicleTypeId"].astype('category').cat.reorder_categories(
            BUSES_LIST)

        fleet_mix = fleet_mix.drop(labels="agencyId", axis=1)
        fleet_mix.sort_values(by="vehicleTypeId", inplace=True)
        fleet_mix.reset_index(inplace=True, drop=True)

        data = fleet_mix.to_dict(orient='list')
        return data 

    def make_routesched_input_data(self):

        frequency = self.frequency_df
        frequency["route_id"] = frequency["route_id"].astype(str)

        # Add all missing routes (the ones that were not changed) in the DF so that they appear int he plot
        df = pd.DataFrame([0, 0, 24*3600, 0]).T
        df.columns = ["route_id", "start_time", "end_time", "headway_secs"]

        for route in ROUTE_IDS:
            if route not in frequency["route_id"].values:
                df["route_id"] = route
                frequency = frequency.append(df)

        frequency["start_time"] = (frequency["start_time"].astype(int) / 3600).round(1)
        frequency["end_time"] = (frequency["end_time"].astype(int) / 3600).round(1)
        frequency["headway_secs"] = (frequency["headway_secs"].astype(int) / 3600).round(1)

        frequency = frequency.sort_values(by="route_id").set_index("route_id")

        palette_dict = dict(zip(ROUTE_IDS, (Category20[20][::2] + Category20[20][1::2])[:len(ROUTE_IDS)]))

        line_data=dict( 
            xs=[[f_row['start_time'], f_row['end_time']] for i, f_row in frequency.iterrows()], 
            ys=[[f_row['headway_secs'], f_row['headway_secs']] for i, f_row in frequency.iterrows()],
            color=[palette_dict[i] for i, f_row in frequency.iterrows()],
            name=[i for i, f_row in frequency.iterrows()]
        )
        start_data=dict( 
            xs=[f_row['start_time'] for i, f_row in frequency.iterrows()], 
            ys=[f_row['headway_secs'] for i, f_row in frequency.iterrows()],
            color=[palette_dict[i] for i, f_row in frequency.iterrows()]
        )
        end_data=dict( 
            xs=[f_row['end_time'] for i, f_row in frequency.iterrows()], 
            ys=[f_row['headway_secs'] for i, f_row in frequency.iterrows()],
            color=[palette_dict[i] for i, f_row in frequency.iterrows()]
        )
        return line_data, start_data, end_data

    def make_fares_input_data(self, max_fare=10, max_age=120):
        fares = self.fares_df

        fares["age"] = fares["age"].astype(str)
        fares["routeId"] = fares["routeId"].astype(str)

        df = pd.DataFrame(columns=["agencyId", "routeId", "age", "amount"])

        # Replace RouteId = NaN values by all bus lines (12 rows)
        for i, fare in fares.iterrows():
            if fare['routeId'] == 'nan':
                df1 = pd.DataFrame(
                    [[fare['agencyId'], route, fare['age'], fare['amount']] for route in ROUTE_IDS],
                    columns=["agencyId", "routeId", "age", "amount"])
                df = df.append(df1)

            else:
                df = df.append(fare)

        # Splitting age ranges into 2 columns (min_age and max_age)
        fares = self.splitting_min_max(df, "age")
        fares["routeId"] = fares["routeId"].astype(str)
        fares["amount"] = fares["amount"].astype(float)

        fares = fares.drop(labels=["age"], axis=1)
        fares = fares.sort_values(by=["amount", "routeId"])
        data = fares.to_dict(orient='list')
        return data 

    def make_modeinc_input_data(self, max_incentive=50, max_age=120, max_income=150000):

        incentives = self.incentives_df
        incentives["amount"] = incentives["amount"].astype(float)

        # Completing the dataframe with the missing subsidized modes (so that they appear in the plot)
        df = pd.DataFrame(["", "(0:{})".format(max_age), "(0:{})".format(max_income), 0.00]).T
        df.columns = ["mode", "age", "income", "amount"]

        modes = ["OnDemand_ride", "drive_transit", "walk_transit"]
        for mode in modes:
            df["mode"] = mode
            incentives = incentives.append(df)
        incentives = incentives.drop_duplicates()

        # Splitting age and income columns
        incentives = self.splitting_min_max(incentives, "age")
        incentives = self.splitting_min_max(incentives, "income")

        incentives = incentives.drop(labels=["age", "income"], axis=1)

        # Changing the type of the "mode" column to 'category' to reorder the modes
        incentives["mode"] = incentives["mode"].astype('category').cat.reorder_categories(modes)

        incentives = incentives.sort_values(by=["amount", "mode"])
        data = incentives.to_dict(orient='list')
        return data

    def make_mode_pie_chart_data(self, mode_choice):

        # Select columns w/ modes
        mode_choice = mode_choice.iloc[-1].drop('iterations').reset_index(name='value').rename(columns={'index': 'Mode'})
        
        mode_choice['perc'] = mode_choice['value']/mode_choice['value'].sum() * 100.0
        mode_choice['angle'] = mode_choice['value']/mode_choice['value'].sum() * 2*math.pi
        mode_choice = mode_choice.sort_values('angle', ascending=False)
        cumangle = 0.0
        for i, row in mode_choice.iterrows():
            mode_choice.loc[i, 'start_angle'] = cumangle
            cumangle += row['angle']
            mode_choice.loc[i, 'end_angle'] = cumangle

        sorterIndex = dict(zip(self.modes + ['others'], range(len(self.modes + ['others']))))
        mode_choice.loc[:, 'Mode'].replace(to_replace='ride_hail', value='OnDemand_ride', inplace=True)
        mode_choice['Mode_order'] = mode_choice['Mode'].map(sorterIndex)
        mode_choice = mode_choice.sort_values('Mode_order')

        mode_choice['color'] = Category10[len(mode_choice)]
            
        mode_choice["label"] = mode_choice.apply(lambda x: '{}%'.format(round(x['perc'], 1)), axis=1)
        mode_choice["label"] = mode_choice["label"].str.pad(30, side = "left")
        data = mode_choice.to_dict(orient='list')
        return data

    def make_mode_choice_by_time_data(self):
        
        mode_choice_by_hour = self.mode_choice_hourly_df.reset_index().dropna()
        
        mode_choice_by_hour.loc[:, "hours"] = mode_choice_by_hour["index"].apply(lambda x: x.split("_")[1])
        mode_choice_by_hour.rename(columns={"ride_hail": "OnDemand_ride"}, inplace=True)
        mode_choice_by_hour = mode_choice_by_hour.drop(labels="index", axis=1)

        max_hour = max([int(h) for h in mode_choice_by_hour['hours']])
        if max_hour > 23:
            hours = [str(h) for h in range(max_hour + 1)]
        else:
            hours = HOURS
            max_hour = 23

        # Completing the dataframe with the missing ridership bins (so that they appear in the plot)
        df = pd.DataFrame([0, 0.0, 0.0, 0.0, 0.0, 0.0]).T
        df.columns = ["hours"] + self.modes

        for hour in range(max_hour + 1):
            if str(hour) not in mode_choice_by_hour["hours"].values:
                df["hours"] = str(hour)
                mode_choice_by_hour = mode_choice_by_hour.append(df)

        mode_choice_by_hour = mode_choice_by_hour.set_index('hours')

        max_choice = mode_choice_by_hour.sum(axis=1).max() * 1.1

        data = mode_choice_by_hour.reset_index().to_dict(orient='list')
        return data 

    def make_mode_choice_by_income_group_data(self):

        persons_cols = ['PID', 'income']
        trips_cols = ['PID', 'realizedTripMode']
        people_income_mode = self.persons_df[persons_cols].merge(self.trips_df[trips_cols], on=['PID'])
        edges = [0, 10000, 25000, 50000, 75000, 100000, float('inf')]
        bins = ['[$0, $10k)', '[$10k, $25k)', '[$25k, $50k)', '[$50k, $75k)', '[$75k, $100k)', '[$100k, inf)']
        people_income_mode['income_group'] = pd.cut(people_income_mode['income'],
                                                    bins=edges,
                                                    labels=bins,
                                                    right=False).astype(str)
        grouped = people_income_mode.groupby(by=['realizedTripMode', 'income_group']).agg('count').reset_index()
        ymax = grouped['PID'].max() * 1.1

        grouped = grouped.pivot(
            index='realizedTripMode', 
            columns='income_group', 
            values='PID').reset_index().rename(columns={'index':'realizedTripMode'})
        data = grouped.to_dict(orient='list')

        return data 

    def make_mode_choice_by_age_group_data(self):

        persons_cols = ['PID', 'Age']
        trips_cols = ['PID', 'realizedTripMode']
        people_age_mode = self.persons_df[persons_cols].merge(self.trips_df[trips_cols], on=['PID'])
        edges = [0, 18, 30, 40, 50, 60, float('inf')]
        bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]
        people_age_mode['age_group'] = pd.cut(people_age_mode['Age'],
                           bins=edges,
                           labels=bins,
                           right=False).astype(str)
        grouped = people_age_mode.groupby(by=['realizedTripMode', 'age_group']).agg('count').reset_index()
        ymax = grouped['PID'].max() * 1.1

        grouped = grouped.pivot(
            index='realizedTripMode', 
            columns='age_group', 
            values='PID').reset_index().rename(columns={'index':'realizedTripMode'})
        data = grouped.to_dict(orient='list')
        return data 

    def make_mode_choice_by_distance_data(self):
        
        mode_df = self.trips_df[['Trip_ID', 'Distance_m', 'realizedTripMode']]
        mode_df.loc[:,'Distance_miles'] = mode_df.loc[:,'Distance_m'] * 0.000621371

        edges = [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7.5, 10, 40]
        bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]
        mode_df.loc[:,'Trip Distance (miles)'] = pd.cut(mode_df['Distance_miles'],
                           bins=edges,
                           labels=bins,
                           right=False).astype(str)

        mode_df_grouped = mode_df.groupby(by=['realizedTripMode', 'Trip Distance (miles)']).agg('count').reset_index()

        # rename df column to num_people due to grouping
        mode_df_grouped = mode_df_grouped.rename(index=str, columns={'Trip_ID': 'num_trips'})

        for_plot = mode_df_grouped[['realizedTripMode', 'Trip Distance (miles)', 'num_trips']]
        max_trips = for_plot.groupby('Trip Distance (miles)')['num_trips'].sum().max() * 1.1

        for_plot = for_plot.rename(columns={'realizedTripMode': 'Trip Mode'})
        for_plot = for_plot.pivot(index='Trip Distance (miles)', columns='Trip Mode', values='num_trips').reset_index()
        
        colors = Category10[len(self.modes)]

        data = for_plot.to_dict(orient='list')
        return data 

    def make_congestion_travel_time_by_mode_data(self):

        travel_time = pd.DataFrame(self.travel_times_df.set_index("TravelTimeMode\Hour").mean(axis=1)).T

        travel_time.rename(columns={'ride_hail': 'OnDemand_ride'}, inplace=True)
        del travel_time['others']

        max_time = travel_time.max(axis=1)[0] * 1.1

        palette = Category10[len(self.modes)]

        data=dict( 
            x=self.modes,
            y=[travel_time[mode] for mode in self.modes],
            color=palette,
        )
        return data

    def make_congestion_travel_time_per_passenger_trip_data(self):

        travel_time = self.travel_times_df.set_index("TravelTimeMode\Hour").T.reset_index()
        
        travel_time.rename(columns={"ride_hail": "OnDemand_ride"}, inplace=True)
        del travel_time['others']

        max_hour = max([int(h) for h in travel_time['index']])
        if max_hour > 23:
            hours = [str(h) for h in range(max_hour + 1)]
        else:
            hours = HOURS
            max_hour = 23

        max_time = travel_time.max().max() * 1.1 

        data = travel_time.to_dict(orient='list')
        return data

    def make_congestion_miles_travelled_per_mode_data(self):

        # get_vmt_dataframe:
        vmt_walk = round(
            self.paths_df[self.paths_df["mode"] == "walk"]["length"].apply(lambda x: x * 0.000621371).sum(), 0)
        vmt_bus = round(
            self.paths_df[self.paths_df["mode"] == "bus"]["length"].apply(lambda x: x * 0.000621371).sum(), 0)
        vmt_on_demand = round(
            self.paths_df[self.paths_df["vehicle"].str.contains("rideHailVehicle")]["length"].apply(lambda x: x * 0.000621371).sum(), 0)
        vmt_car = round(self.legs_df[self.legs_df["Mode"] == "car"]["Distance_m"].apply(lambda x: x * 0.000621371).sum(), 0)
        vmt = pd.DataFrame({"bus": [vmt_bus], "car": [vmt_car], "OnDemand_ride": [vmt_on_demand], "walk" : [vmt_walk]})

        modes = ['OnDemand_ride', 'car', 'bus', 'walk']
        vmt = pd.melt(vmt, value_vars=modes)

        max_vmt = vmt['value'].max() * 1.1

        palette = Category10[len(modes)]
        data = dict(modes=modes, vmt=[vmt_bus, vmt_car, vmt_on_demand, vmt_walk], color=palette)
        return data
        # source = ColumnDataSource(data=dict(modes=modes, vmt=[vmt_bus, vmt_car, vmt_on_demand, vmt_walk], color=palette))
        # return source 

    def make_congestion_bus_vmt_by_ridership_data(self, seatingCapacity=50):
        columns = ["numPassengers", "length", "departureTime", "arrivalTime"]
        vmt_bus_ridership = self.paths_df[self.paths_df["mode"] == "bus"][columns]
        # Split the travels by hour of the day
        edges = range(0,25*3600,3600)
        vmt_bus_ridership.loc[:, "Hour"] = pd.cut(vmt_bus_ridership["departureTime"], 
                                                  bins=edges,
                                                  labels=HOURS,
                                                  right=False)

        # Group by hours of the day and number of passengers in the bus
        vmt_bus_ridership = vmt_bus_ridership.groupby(by=["Hour", "numPassengers"]).sum().reset_index()
        edges = [0, 1, seatingCapacity*0.5, seatingCapacity, seatingCapacity+1, seatingCapacity*100]
        bins = [
            'empty\n(0 passengers)', 
            'low ridership\n(< 50% seating capacity)', 
            'medium ridership\n(< seating capacity)', 
            'full\n(at capacity)', 
            'crowded\n(> seating capacity)'
        ]
        vmt_bus_ridership.loc[:, "ridership"] = pd.cut(vmt_bus_ridership["numPassengers"], 
                                                       bins=edges,
                                                       labels=bins,
                                                       right=False)
        vmt_bus_ridership.replace(np.nan, 0, inplace=True)
        vmt_bus_ridership["Hour"] = vmt_bus_ridership["Hour"].astype("int")
        del vmt_bus_ridership['numPassengers']
        del vmt_bus_ridership['departureTime']
        del vmt_bus_ridership['arrivalTime']
        # Completing the dataframe with the missing ridership bins (so that they appear in the plot)
        df = pd.DataFrame([0, 0.0, ""]).T
        df.columns = ["Hour", "length", "ridership"]

        for ridership in bins:
            for hour in range(24):
                if len(vmt_bus_ridership[(vmt_bus_ridership['Hour'] == hour) & (vmt_bus_ridership['ridership'] == ridership)].index) == 0:
                    df["ridership"] = ridership
                    df["Hour"] = hour
                    vmt_bus_ridership = vmt_bus_ridership.append(df)

        vmt_bus_ridership = vmt_bus_ridership.groupby(['Hour', 'ridership'])['length'].sum().reset_index().pivot(
            index='Hour',
            columns='ridership', 
            values='length')
        ymax = vmt_bus_ridership.sum(axis=1).max()*1.1

        colors = Category10[len(bins)]

        data = vmt_bus_ridership.reset_index().to_dict(orient='list')
        return data 

    def make_congestion_on_demand_vmt_by_phases_data(self):

        columns = ["numPassengers", "departureTime", "length"]
        vmt_on_demand = self.paths_df[self.paths_df["vehicle"].str.contains("rideHailVehicle")][columns]
        # Split the travels by hour of the day
        edges = range(0,25*3600,3600)
        vmt_on_demand.loc[:, "Hour"] = pd.cut(vmt_on_demand["departureTime"],
                                              bins=edges,
                                              labels=HOURS,
                                              right=False)
        driving_states = ["fetch", "fare"]
        vmt_on_demand.loc[:, "drivingState"] = pd.cut(vmt_on_demand["numPassengers"], 
                                                      bins=[0, 1, 2], 
                                                      labels=driving_states,
                                                      right=False)

        vmt_on_demand = vmt_on_demand.groupby(by=["Hour", "drivingState"])['length'].sum().reset_index()
        vmt_on_demand.replace(np.nan, 0, inplace=True)
        vmt_on_demand["Hour"] = vmt_on_demand["Hour"].astype("int")
        vmt_on_demand = vmt_on_demand.pivot(
            index='Hour', 
            columns='drivingState',
            values='length')
        ymax = vmt_on_demand.sum(axis=1).max()*1.1

        colors = Category10[10][:len(driving_states)]

        data = vmt_on_demand.reset_index().to_dict(orient='list')
        return data 

    def make_congestion_travel_speed_data(self):

        trips = self.trips_df[self.trips_df['Duration_sec'] > 0]
        
        trips.loc[:, 'average speed (meters/sec)'] = trips['Distance_m'] / trips['Duration_sec']
        trips.loc[:, 'Average Speed (miles/hour)'] = 2.23694 * trips['average speed (meters/sec)']
        trips.loc[:, 'Start_time_hour'] = trips['Start_time'] / 3600
        
        edges = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
        bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]
        trips.loc[:, 'time_interval'] = pd.cut(trips['Start_time_hour'],
                                                    bins=edges,
                                                    labels=bins,
                                                    right=False).astype(str)

        trips = trips.rename(index=str, columns={"time_interval": "Start time interval (hour)"})

        grouped = trips.groupby(by=['Start time interval (hour)', 'realizedTripMode'])['Average Speed (miles/hour)'].mean().reset_index()
        max_speed = grouped['Average Speed (miles/hour)'].max() * 1.2

        grouped = grouped.pivot(
            index='Start time interval (hour)', 
            columns='realizedTripMode', 
            values='Average Speed (miles/hour)')
        grouped = grouped.reset_index().rename(columns={'index':'Start time interval (hour)'})

        data = grouped.to_dict(orient='list')
        return data 

    def make_los_travel_expenditure_data(self):

        trips = self.trips_df
        trips.loc[:, 'trip_cost'] = np.zeros(trips.shape[0])

        trips.loc[trips['realizedTripMode'] == 'car', 'trip_cost'] = \
            trips.loc[trips['realizedTripMode'] == 'car', :].FuelCost.values

        fare_modes = ['walk_transit', 'drive_transit', 'OnDemand_ride']
        trips[trips['realizedTripMode'].isin(fare_modes)].loc[:, 'trip_cost'] = \
            trips[trips['realizedTripMode'].isin(fare_modes)].Fare.values - \
            trips[trips['realizedTripMode'].isin(fare_modes)].Incentive.values

        trips[trips['realizedTripMode'] == 'drive_transit'].loc[:, 'trip_cost'] = \
            trips[trips['realizedTripMode'] == 'drive_transit'].trip_cost.values + \
            trips[trips['realizedTripMode'] == 'drive_transit'].FuelCost.values

        trips.loc[trips['trip_cost'] < 0,:] = 0
        trips.loc[:, "hour_of_day"] = np.floor(trips.Start_time/3600)

        grouped = trips.groupby(by=["realizedTripMode", "hour_of_day"])["trip_cost"].mean().reset_index()
        grouped = grouped[grouped['realizedTripMode'] != 0]
        max_cost = grouped['trip_cost'].max() * 1.1

        grouped = grouped.pivot(
            index='hour_of_day', 
            columns='realizedTripMode', 
            values='trip_cost')
        grouped = grouped.reset_index().rename(columns={'index':'hour_of_day'})

        data = grouped.to_dict(orient='list')
        return data 

    def make_los_crowding_data(self):

        columns = ["vehicle", "numPassengers", "departureTime", "arrivalTime", "vehicleType"]
        bus_slice_df = self.paths_df[self.paths_df["mode"] == "bus"][columns]

        bus_slice_df.loc[:, "route_id"] = bus_slice_df['vehicle'].apply(lambda x: self.trip_to_route[x.split(":")[1].split('-')[0]])
        bus_slice_df.loc[:, "serviceTime"] = (bus_slice_df['arrivalTime'] - bus_slice_df['departureTime']) / 3600
        bus_slice_df.loc[:, "seatingCapacity"] = bus_slice_df['vehicleType'].apply(
            lambda x: TRANSIT_SCALE_FACTOR * self.seating_capacities[x])
        bus_slice_df.loc[:, "passengerOverflow"] = bus_slice_df['numPassengers'] > bus_slice_df['seatingCapacity']
        # AM peak = 7am-10am, PM Peak = 5pm-8pm, Early Morning, Midday, Late Evening = in between
        bins = [0, 25200, 36000, 61200, 72000, 86400]
        labels = ["Early Morning (12a-7a)", "AM Peak (7a-10a)", "Midday (10a-5p)", "PM Peak (5p-8p)", "Late Evening (8p-12a)"]
        bus_slice_df.loc[:, "servicePeriod"] = pd.cut(bus_slice_df['departureTime'],
                                                      bins=bins,
                                                      labels=labels)
        grouped_data = bus_slice_df[bus_slice_df['passengerOverflow']].groupby([
            "route_id", "servicePeriod"])["serviceTime"].sum().fillna(0).reset_index()
        max_crowding = grouped_data['serviceTime'].max() * 1.1

        grouped_data = reset_index(grouped_data.pivot(
            index='route_id', 
            columns='servicePeriod', 
            values='serviceTime')).rename(columns={'index':'route_id'})

        # Completing the dataframe with the missing service periods and route_ids (so that they appear in the plot)
        for label in labels:
            if label not in grouped_data.columns:
                grouped_data.loc[:, label] = 0.0
        
        df = pd.DataFrame(['', 0.0, 0.0, 0.0, 0.0, 0.0]).T
        df.columns = ["route_id"] + labels

        for route_id in ROUTE_IDS:
            if route_id not in grouped_data['route_id'].values:
                df["route_id"] = route_id
                grouped_data = grouped_data.append(df)

        grouped_data.loc[:, 'route_id'] = grouped_data.loc[:, 'route_id'].astype(str)
        data = grouped_data.to_dict(orient='list')
        return data 

    def make_transit_cb_data(self):

        columns = ["vehicle", "numPassengers", "departureTime", "arrivalTime", "FuelCost", "vehicleType"]
        bus_slice_df = self.paths_df.loc[self.paths_df["mode"] == "bus"][columns]

        bus_slice_df.loc[:, "route_id"] = bus_slice_df['vehicle'].apply(lambda x: self.trip_to_route[x.split(":")[-1].split('-')[0]])
        bus_slice_df.loc[:, "operational_costs_per_bus"] = bus_slice_df['vehicleType'].apply(lambda x: self.operational_costs[x])
        bus_slice_df.loc[:, "serviceTime"] = (bus_slice_df['arrivalTime'] - bus_slice_df['departureTime']) / 3600
        bus_slice_df.loc[:, "OperationalCosts"] = bus_slice_df['operational_costs_per_bus'] * bus_slice_df['serviceTime']

        columns = ["Veh", "Fare"]
        bus_fare_df = self.legs_df.loc[self.legs_df["Mode"] == "bus"][columns]

        bus_fare_df.loc[:, "route_id"] = bus_fare_df['Veh'].apply(
            lambda x: self.trip_to_route[x.split(":")[-1].split('-')[0].split('-')[0]])
        
        merged_df = pd.merge(bus_slice_df, bus_fare_df, on=["route_id"])

        labels = ["OperationalCosts", "FuelCost", "Fare"]
        costs_labels = labels[:2]
        benefits_labels = ["Fare"]

        grouped_data = merged_df.groupby(by="route_id")[labels].sum()

        max_cost = grouped_data.sum(axis=1).max() * 1.1
        grouped_data.reset_index(inplace=True)

        # Completing the dataframe with the missing route_ids (so that they appear in the plot)
        df = pd.DataFrame(['', 0.0, 0.0, 0.0]).T
        df.columns = ["route_id"] + labels

        for route_id in ROUTE_IDS:
            if int(route_id) not in grouped_data['route_id'].values:
                df["route_id"] = int(route_id)
                grouped_data = grouped_data.append(df)
        grouped_data.sort_values('route_id', inplace=True)

        grouped_data.loc[:, 'route_id'] = grouped_data.loc[:, 'route_id'].astype(str)
        grouped_data.loc[:, 'OperationalCosts'] *= -1
        grouped_data.loc[:, 'FuelCost'] *= -1

        colors = Category10[len(labels)]

        costs_data = grouped_data[['route_id'] + costs_labels].to_dict(orient='list')
        benefits_data = grouped_data[['route_id'] + benefits_labels].to_dict(orient='list')
        return costs_data, benefits_data

    def make_transit_inc_by_mode_data(self):
        
        columns = ['FuelCost', 'Fare', 'Start_time', 'realizedTripMode', 'Incentive']
        trips = self.trips_df[columns]

        trips.loc[:, 'trip_cost'] = np.zeros(trips.shape[0])
        trips.loc[:, 'ride_expenditure'] = trips['Fare'] - trips['Incentive']
        ride_modes = set(['walk_transit', 'drive_transit', 'OnDemand_ride'])

        trips.loc[trips['realizedTripMode'] == 'car', 'trip_cost'] = trips.loc[trips['realizedTripMode'] == 'car', 'FuelCost'].values
        trips.loc[trips['realizedTripMode'].isin(ride_modes), 'trip_cost'] = trips.loc[trips['realizedTripMode'].isin(ride_modes), 'ride_expenditure'].values
        trips.loc[trips['realizedTripMode'] == 'drive_transit', 'trip_cost'] += trips.loc[trips['realizedTripMode'] == 'drive_transit', 'FuelCost'].values

        trips.loc[:, 'Incentives distributed'] = trips['Incentive'].values
        trips.loc[trips['trip_cost'] < 0, 'Incentives distributed'] -= trips.loc[trips['trip_cost'] < 0, 'trip_cost'].values

        trips.loc[:, "hour_of_day"] = np.floor(trips['Start_time'] / 3600).astype(int)
        grouped = trips.groupby(by=["realizedTripMode", "hour_of_day"])["Incentives distributed"].sum().reset_index()

        max_incentives = grouped['Incentives distributed'].max() * 1.1
        if max_incentives == 0:
            max_incentives = 100

        grouped = grouped.pivot(
            index='hour_of_day', 
            columns='realizedTripMode', 
            values='Incentives distributed')
        grouped = grouped.reset_index().rename(columns={'index':'hour_of_day'})

        data = grouped.to_dict(orient='list')
        return data 

    def make_sustainability_25pm_per_mode_data(self):
        
        columns = ["vehicle", "mode", "length", "departureTime"]
        vmt = self.paths_df[columns]

        # emissions for each mode
        emissions_bus = round(
            vmt[vmt["mode"] == "bus"]["length"].apply(lambda x: x * 0.000621371 * 0.259366648).sum(), 0)
        emissions_on_demand = round(
            vmt[vmt["vehicle"].str.contains("rideHailVehicle")]["length"].apply(
                lambda x: x * 0.000621371 * 0.001716086).sum(), 0)
        emissions_car = round(
            self.legs_df[self.legs_df["Mode"] == "car"]["Distance_m"].apply(lambda x: x * 0.000621371 * 0.001716086).sum(), 0)

        emissions = pd.DataFrame({"bus": [emissions_bus], "car": [emissions_car], "OnDemand_ride": [emissions_on_demand]})

        modes = ['OnDemand_ride', 'car', 'bus']
        emissions = pd.melt(emissions, value_vars=modes)

        max_emissions = emissions['value'].max() * 1.1
        
        palette = Category10[len(modes)]
        data=dict(modes=modes, emissions=[emissions_on_demand, emissions_car, emissions_bus], color=palette)
        return data

# TODO:
# add in xml parser function