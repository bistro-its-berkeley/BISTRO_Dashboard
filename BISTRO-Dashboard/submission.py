import pdb
import math
import numpy as np 
from os import listdir
from os.path import dirname, join
import pandas as pd 
# import seaborn as sns 

from bokeh.models import ColumnDataSource
from bokeh.palettes import Dark2, Category10, Category20, Plasma256, YlOrRd

from db_loader import BistroDB

HOURS = [str(h) for h in range(24)]

BUSES_LIST = ['BUS-DEFAULT', 'BUS-SMALL-HD', 'BUS-STD-HD', 'BUS-STD-ART']

TRANSIT_SCALE_FACTOR = 0.1

def reset_index(df):
    '''Returns DataFrame with index as columns'''
    index_df = df.index.to_frame(index=False)
    df = df.reset_index(drop=True)
    #  In merge is important the order in which you pass the dataframes
    # if the index contains a Categorical. 
    # pd.merge(df, index_df, left_index=True, right_index=True) does not work
    return pd.merge(index_df, df, left_index=True, right_index=True)


def calc_ridership_perc(row):
    if row['numPassengers'] > row['seatingCapacity']:
        return 100.0 + (row['numPassengers'] - row['seatingCapacity']) * 100.0 / row['standingRoomCapacity']
    else:
        return row['numPassengers'] * 100.0 / row['seatingCapacity']


def merc(lat, lon):
    # https://gis.stackexchange.com/questions/156035/calculating-mercator-coordinates-from-lat-lon
    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x/lon
    y = (180.0/math.pi * math.log(math.tan(math.pi/4.0 +
        lat * (math.pi/180.0)/2.0)) * scale)
    return (x, y)


class Submission():

    links = dict()

    @classmethod
    def load_links(cls, db, scenario):
        if scenario in cls.links:
            return cls.links[scenario]
        else:
            cls.links[scenario] = db.load_links(scenario)
            return cls.links[scenario]

    def __init__(self, name, scenario, simulation_ids=None):
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
        self.simulation_ids = simulation_ids
#        self.scenario = 'sioux_faux-15k'
#        self.simulation_id = '5673feca-f45a-11e9-ba19-acde48001122'
        self.modes = ['ride_hail', 'car', 'drive_transit', 'walk', 'walk_transit']
        self.data_loaded = False
        self.data_source_made = False

        if simulation_ids is None:
            self.simulation_count = 1
            self.submissions_dir = join(
                dirname(__file__),
                'data/submissions/{}/{}'.format(self.scenario, self.name))
            self.reference_dir = join(
                dirname(__file__), 'data/sioux_faux_bus_lines')
        else:
            self.simulation_count = len(simulation_ids)
        # self.get_data()
        # self.make_data_sources()

    def get_data(self):
        if self.data_loaded:
            return

        if self.simulation_ids is None:
            self.links_df = pd.read_csv(join(self.submissions_dir, 'network.csv'))
            self.frequency_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/FrequencyAdjustment.csv'))
            self.fares_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/MassTransitFares.csv'))
            self.incentives_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/ModeIncentives.csv'))
            self.fleet_df = pd.read_csv(join(self.submissions_dir, 'competition/submission-inputs/VehicleFleetMix.csv'))
            self.tollcircle_df = None
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
            self.standing_room_capacities = pd.read_csv(join(self.reference_dir, "availableVehicleTypes.csv"))[[
                "vehicleTypeId", "standingRoomCapacity"]].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]
            self.trip_to_route = pd.read_csv(join(self.reference_dir, "gtfs_data/trips.txt"))[[
                "trip_id", "route_id"]].set_index("trip_id", drop=True).T.to_dict('records')[0]
            self.operational_costs = pd.read_csv(join(self.reference_dir, "vehicleCosts.csv"))[[
                "vehicleTypeId", "opAndMaintCost"]].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]
            self.data_loaded = True
        else:
            #TODO(Robert) set ENV variable for db key
            db = BistroDB(
                db_name='', user_name='', db_key='',host='')
            self.links_df = self.load_links(db, self.scenario)
            self.frequency_df = db.load_frequency(self.simulation_ids[0])
            self.fares_df = db.load_fares(self.simulation_ids[0])
            self.incentives_df = db.load_incentives(self.simulation_ids[0])
            self.fleet_df = db.load_fleet(self.simulation_ids[0])
            self.scores_df = db.load_scores(self.simulation_ids)
            self.activities_df = None
            self.households_df = None
            self.legs_df = db.load_legs(self.simulation_ids)
            self.paths_df = db.load_paths(self.simulation_ids, self.scenario)
            self.persons_df = db.load_person(self.scenario)
            self.trips_df = db.load_trips(self.simulation_ids)
            self.mode_choice_df = db.load_mode_choice(self.simulation_ids)
            self.realized_mode_choice_df = db.load_mode_choice(
                self.simulation_ids, realized=True)
            self.tollcircle_df = db.load_tollcircle(self.simulation_ids[0])
            self.mode_choice_hourly_df = db.load_hourly_mode_choice(
                self.simulation_ids)

            self.travel_times_df = db.load_travel_times(self.simulation_ids)
            vehicle_type = db.load_vehicle_types(self.scenario)

            self.seating_capacities = vehicle_type[
                ["vehicleTypeId", "seatingCapacity"]
            ].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]

            self.standing_room_capacities = vehicle_type[
                ["vehicleTypeId", "standingRoomCapacity"]
            ].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]

            self.agency_ids = db.load_agency(self.scenario)
            self.route_ids = [str(r_id) for r_id in db.load_route_ids(self.scenario)]

            self.trip_to_route = db.load_trip_to_route(self.scenario)[
                ["trip_id", "route_id"]
            ].set_index("trip_id", drop=True).T.to_dict('records')[0]

            self.operational_costs = db.load_vehicle_cost(self.scenario)[
                ["vehicleTypeId", "opAndMaintCost"]
            ].set_index("vehicleTypeId", drop=True).T.to_dict("records")[0]
            self.data_loaded = True

    def make_data_sources(self):
        if self.data_source_made:
            return
        
        self.modeinc_input_data = self.make_modeinc_input_data()
        self.fleetmix_input_data = self.make_fleetmix_input_data()
        self.fares_input_data = self.make_fares_input_data()
        (self.routesched_input_line_data, self.routesched_input_start_data,
         self.routesched_input_end_data) = self.make_routesched_input_data()
        self.link_data = self.make_link_data()
        self.tollcircle_data = self.make_tollcircle_data()
        self.normalized_scores_data = self.make_normalized_scores_data()

        self.mode_planned_pie_chart_data = self.make_mode_pie_chart_data(
            self.mode_choice_df.copy())
        self.mode_realized_pie_chart_data = self.make_mode_pie_chart_data(
            self.realized_mode_choice_df.copy())
        self.mode_choice_by_time_data = self.make_mode_choice_by_time_data()
        self.mode_choice_by_age_group_data = \
            self.make_mode_choice_by_age_group_data()
        self.mode_choice_by_income_group_data = \
            self.make_mode_choice_by_income_group_data()
        self.mode_choice_by_distance_data = \
            self.make_mode_choice_by_distance_data()

        self.congestion_travel_time_by_mode_data = \
            self.make_congestion_travel_time_by_mode_data()
        self.congestion_travel_time_per_passenger_trip_data = \
            self.make_congestion_travel_time_per_passenger_trip_data()
        self.congestion_miles_traveled_per_mode_data = \
            self.make_congestion_miles_traveled_per_mode_data()
        self.congestion_bus_vmt_by_ridership_data = \
            self.make_congestion_bus_vmt_by_ridership_data()
        self.congestion_on_demand_vmt_by_phases_data = \
            self.make_congestion_on_demand_vmt_by_phases_data()
        self.congestion_travel_speed_data = \
            self.make_congestion_travel_speed_data()

        self.los_travel_expenditure_data = \
            self.make_los_travel_expenditure_data()
        self.los_crowding_data = self.make_los_crowding_data()

        self.transit_cb_costs_data, self.transit_cb_benefits_data = \
            self.make_transit_cb_data()
        self.transit_inc_by_mode_data = self.make_transit_inc_by_mode_data()
        self.toll_revenue_by_time_data = self.make_toll_revenue_by_time_data()
        
        self.sustainability_25pm_per_mode_data = \
            self.make_sustainability_25pm_per_mode_data()
        self.data_source_made = True

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
            min_max = df[name_column].str.replace(r"[\[\]\(\)]","").str.split(
                ":", expand=True)
            df["min_{0}".format(name_column)] = min_max.iloc[:, 0].astype(int)
            df["max_{0}".format(name_column)] = min_max.iloc[:, 1].astype(int)

        return df

    def make_normalized_scores_data(self):
        scores = self.scores_df
        scores = scores.loc[:,["Component Name", "Weighted Score"]]
        scores.set_index("Component Name", inplace=True)
        scores.reset_index(inplace=True)

        scores.loc[:, "Component Name"] = scores["Component Name"].astype('category')#.cat.reorder_categories(CATEGORIES)

        scores = scores.sort_values(by="Component Name")

        scores.loc[:, 'color'] = "#4682b4"
        scores.loc[scores["Component Name"] == 'Submission Score', 'color'] = "#000080"

        # min_score = min(scores['Weighted Score'].min(), 0.0) * 1.1
        # max_score = max(scores['Weighted Score'].max(), 1.0) * 1.1

        data = scores.to_dict(orient='list')
        return data

    def make_fleetmix_input_data(self):

        fleet_mix = self.fleet_df

        if fleet_mix.empty:
            fleet_mix = pd.DataFrame(
                [[agency_id, "{}".format(route_id), "BUS-DEFAULT"]
                  for route_id in self.route_ids
                  for agency_id in self.agency_ids],
                columns=["agencyId", "routeId", "vehicleTypeId"])

        df = pd.DataFrame([self.agency_ids[0], '1', BUSES_LIST[0]]).T
        df.columns = ["agencyId", "routeId", "vehicleTypeId"]

        # Adding the missing bus types in the dataframe so that they appear in the plot
        for bus in BUSES_LIST:
            if bus not in fleet_mix["vehicleTypeId"].values:
                df.loc[0, "vehicleTypeId"] = bus
                fleet_mix = fleet_mix.append(df, ignore_index=True, sort=False)

        # Adding the missing bus routes in the dataframe so that they appear in the plot
        fleet_mix.loc[:, "routeId"] = fleet_mix["routeId"].astype(str)

        df = pd.DataFrame([self.agency_ids[0], "", BUSES_LIST[0]]).T
        df.columns = ["agencyId", "routeId", "vehicleTypeId"]

        for route in self.route_ids:
            if route not in fleet_mix["routeId"].values:
                df.loc[0, "routeId"] = route
                fleet_mix = fleet_mix.append(df, ignore_index=True, sort=False)

        # Reodering bus types starting by "BUS-DEFAULT" and then by ascending bus size order
        fleet_mix.loc[:, "vehicleTypeId"] = fleet_mix["vehicleTypeId"].astype(
            'category').cat.reorder_categories(BUSES_LIST)

        fleet_mix = fleet_mix.drop(labels="agencyId", axis=1)
        fleet_mix.sort_values(by="vehicleTypeId", inplace=True)
        fleet_mix.reset_index(inplace=True, drop=True)

        data = fleet_mix.to_dict(orient='list')
        return data 

    def make_routesched_input_data(self):

        frequency = self.frequency_df
        frequency.loc[:, "route_id"] = frequency["route_id"].astype(str)

        # Add all missing routes (the ones that were not changed) in the DF so that they appear int he plot
        df = pd.DataFrame([0, 0, 24*3600, 10800]).T
        df.columns = ["route_id", "start_time", "end_time", "headway_secs"]

        for route in self.route_ids:
            if route not in frequency["route_id"].values:
                df.loc[0, "route_id"] = route
                frequency = frequency.append(df, ignore_index=True, sort=False)

        frequency.loc[:, "start_time"] = (
            frequency["start_time"].astype(int) / 3600).round(1)
        frequency.loc[:, "end_time"] = (
            frequency["end_time"].astype(int) / 3600).round(1)
        frequency.loc[:, "headway_secs"] = (
            frequency["headway_secs"].astype(int) / 3600).round(1)

        frequency = frequency.sort_values(by="route_id").set_index("route_id")

        # palette_dict = dict(zip(ROUTE_IDS, (Category20[20][::2] + Category20[20][1::2])[:len(ROUTE_IDS)]))
        palette_dict = dict(zip(self.route_ids, Plasma256[:len(self.route_ids)]))
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

        fares.loc[:, "age"] = fares["age"].astype(str)
        fares.loc[:, "routeId"] = fares["routeId"].astype(str)

        df = pd.DataFrame(columns=["agencyId", "routeId", "age", "amount"])

        # Replace RouteId = NaN values by all bus lines (12 rows)
        for i, fare in fares.iterrows():
            if fare['routeId'] == 'nan':
                df1 = pd.DataFrame(
                    [[fare['agencyId'], route, fare['age'], fare['amount']]
                     for route in self.route_ids],
                    columns=["agencyId", "routeId", "age", "amount"])
                df = df.append(df1, ignore_index=True, sort=False)

            else:
                df = df.append(fare, ignore_index=True, sort=False)

        # Splitting age ranges into 2 columns (min_age and max_age)
        fares = self.splitting_min_max(df, "age")
        fares.loc[:, "routeId"] = fares["routeId"].astype(str)
        fares.loc[:, "amount"] = fares["amount"].astype(float)

        fares = fares.drop(labels=["age"], axis=1)
        fares = fares.sort_values(by=["amount", "routeId"])
        data = fares.to_dict(orient='list')
        return data 

    def make_link_data(self):
        links = self.links_df.copy()
        from_x = []
        from_y = []
        to_x = []
        to_y = []
        for _, row in links.iterrows():
            x0, y0 = merc(row['fromLocationX'],row['fromLocationY'])
            x1, y1 = merc(row['toLocationX'],row['toLocationY'])
            from_x.append(x0)
            from_y.append(y0)
            to_x.append(x1)
            to_y.append(y1)

        links['from_x'], links['from_y']  = from_x, from_y
        links['to_x'], links['to_y'] = to_x, to_y

        data = links[['from_x','from_y','to_x','to_y']].to_dict(orient='list')
        return data

    def make_tollcircle_data(self):
        if 'sioux_faux' in self.scenario:
            x_lim = [-10776977, -10759011]
            y_lim = [5388501, 5406742]
        else:
            x_lim = [0, 0]
            y_lim = [0, 0]

        data = {}
        data['x_low'], data['x_high'] = x_lim
        data['y_low'], data['y_high'] = y_lim
        data['center_x'] = 0
        data['center_y'] = 0
        data['radius'] = 0
        data['text'] = ''

        if self.tollcircle_df is None or len(self.tollcircle_df) == 0:
            return pd.DataFrame(data, index=[0]).to_dict(orient='list')

        center_x, center_y = merc(self.tollcircle_df['center_lat'][0],
                                  self.tollcircle_df['center_lon'][0])
        border_x, border_y = merc(self.tollcircle_df['border_lat'][0],
                                  self.tollcircle_df['border_lon'][0])
        radius = np.linalg.norm([center_x-border_x, center_y-border_y])

        data['center_x'] = center_x
        data['center_y'] = center_y
        data['radius'] = radius
        toll = self.tollcircle_df['toll'][0]
        unit = '[$/mile]' if  self.tollcircle_df['type'][0] == 'permile' else '[$]'
        data['text'] = f"{toll:.2f} " + unit
        return pd.DataFrame(data, index=[0]).to_dict(orient='list')


    def make_modeinc_input_data(self, max_incentive=50, max_age=120,
            max_income=150000):

        incentives = self.incentives_df
        incentives.loc[:, "amount"] = incentives["amount"].astype(float)

        # Completing the dataframe with the missing subsidized modes (so that they appear in the plot)
        df = pd.DataFrame(
            ["", "(0:{})".format(max_age), "(0:{})".format(max_income), 0.00]).T
        df.columns = ["mode", "age", "income", "amount"]

        modes = ["ride_hail", "drive_transit", "walk_transit"]
        for mode in modes:
            df.loc[0, "mode"] = mode
            incentives = incentives.append(df, ignore_index=True, sort=False)
        incentives = incentives[incentives["mode"].isin(modes)].drop_duplicates()

        # Splitting age and income columns
        incentives = self.splitting_min_max(incentives, "age")
        incentives = self.splitting_min_max(incentives, "income")

        incentives = incentives.drop(labels=["age", "income"], axis=1)

        # Changing the type of the "mode" column to 'category' to reorder the modes
        incentives.loc[:, "mode"] = incentives["mode"].astype('category').cat.reorder_categories(modes)

        incentives = incentives.sort_values(by=["amount", "mode"])
        data = incentives.to_dict(orient='list')
        return data

    def make_mode_pie_chart_data(self, mode_choice):

        # Select columns w/ modes
        mode_choice = mode_choice.iloc[-1].drop('iterations').reset_index(name='value').rename(columns={'index': 'Mode'})
        
        mode_choice.loc[:, 'perc'] = mode_choice['value']/mode_choice['value'].sum() * 100.0
        mode_choice.loc[:, 'angle'] = mode_choice['value']/mode_choice['value'].sum() * 2*math.pi
        mode_choice = mode_choice.sort_values('angle', ascending=False)
        cumangle = 0.0
        scale = 3.0
        for i, row in mode_choice.iterrows():
            mode_choice.loc[i, 'start_angle'] = cumangle
            cumangle += row['angle'] / 2.0
            mode_choice.loc[i, 'x_loc'] = math.cos(cumangle) * 0.2
            mode_choice.loc[i, 'y_loc'] = 1 + (math.sin(cumangle) * 0.2 * scale)
            cumangle += row['angle'] / 2.0
            mode_choice.loc[i, 'end_angle'] = cumangle
            
        sorterIndex = dict(zip(self.modes + ['others'], range(len(self.modes + ['others']))))
        #mode_choice.loc[:, 'Mode'].replace(to_replace='ride_hail', value='ride_hail', inplace=True)
        mode_choice.loc[:, 'Mode_order'] = mode_choice['Mode'].map(sorterIndex)
        mode_choice = mode_choice.sort_values('Mode_order')

        mode_choice.loc[:, 'color'] = Dark2[len(mode_choice)]
            
        mode_choice.loc[:, "label"] = mode_choice.apply(lambda x: '{}%'.format(round(x['perc'], 1)) if x['perc']
             >= 2.0 else '', axis=1)
        mode_choice.loc[:, "label"] = mode_choice["label"].str.pad(30, side = "left")
        data = mode_choice.to_dict(orient='list')
        return data

    def make_mode_choice_by_time_data(self):
        
        mode_choice_by_hour = self.mode_choice_hourly_df.reset_index().dropna()
        
        mode_choice_by_hour.loc[:, "hours"] = mode_choice_by_hour["index"].apply(
            lambda x: x.split("_")[1])
        #mode_choice_by_hour.rename(columns={"ride_hail": "OnDemand_ride"}, inplace=True)
        mode_choice_by_hour = mode_choice_by_hour.drop(labels="index", axis=1)

        max_hour = max([int(h) for h in mode_choice_by_hour['hours']])
        if max_hour > 23:
            hours = [str(h) for h in range(max_hour + 1)]
        else:
            hours = HOURS
            max_hour = 23

        for mode in self.modes:
            if mode not in mode_choice_by_hour.columns:
                mode_choice_by_hour[mode] = 0

        # Completing the dataframe with the missing ridership bins (so that they appear in the plot)
        df = pd.DataFrame([0, 0.0, 0.0, 0.0, 0.0, 0.0]).T
        df.columns = ["hours"] + self.modes

        for hour in range(max_hour + 1):
            if str(hour) not in mode_choice_by_hour["hours"].values:
                df.loc[0, "hours"] = str(hour)
                mode_choice_by_hour = mode_choice_by_hour.append(
                    df, ignore_index=True, sort=False)

        mode_choice_by_hour = mode_choice_by_hour.set_index('hours')

        # max_choice = mode_choice_by_hour.sum(axis=1).max() * 1.1

        data = mode_choice_by_hour.reset_index().to_dict(orient='list')
        return data 

    def make_mode_choice_by_income_group_data(self):

        persons_cols = ['PID', 'income']
        trips_cols = ['PID', 'realizedTripMode']
        people_income_mode = self.persons_df[persons_cols].merge(
            self.trips_df[trips_cols], on=['PID'])
        edges = [0, 10000, 25000, 50000, 75000, 100000, float('inf')]
        bins = ['[$0, $10k)', '[$10k, $25k)', '[$25k, $50k)', '[$50k, $75k)',
                '[$75k, $100k)', '[$100k, inf)']
        people_income_mode.loc[:, 'income_group'] = pd.cut(
            people_income_mode['income'],
            bins=edges,
            labels=bins,
            right=False
        ).astype(str)
        grouped = people_income_mode.groupby(
            by=['realizedTripMode', 'income_group']).agg('count').reset_index()
        # ymax = grouped['PID'].max() * 1.1

        grouped.loc[:, 'PID'] = grouped['PID'] // self.simulation_count

        grouped = grouped.pivot(
            index='realizedTripMode', 
            columns='income_group', 
            values='PID'
        ).reset_index().rename(columns={'index':'realizedTripMode'})
        data = grouped.to_dict(orient='list')

        return data 

    def make_mode_choice_by_age_group_data(self):

        persons_cols = ['PID', 'Age']
        trips_cols = ['PID', 'realizedTripMode']
        people_age_mode = self.persons_df[persons_cols].merge(
            self.trips_df[trips_cols], on=['PID'])
        edges = [0, 18, 30, 40, 50, 60, float('inf')]
        bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]
        people_age_mode.loc[:, 'age_group'] = pd.cut(people_age_mode['Age'],
                                                     bins=edges,
                                                     labels=bins,
                                                     right=False).astype(str)
        grouped = people_age_mode.groupby(
            by=['realizedTripMode', 'age_group']).agg('count').reset_index()
        # ymax = grouped['PID'].max() * 1.1

        grouped.loc[:, 'PID'] = grouped['PID'] // self.simulation_count

        grouped = grouped.pivot(
            index='realizedTripMode', 
            columns='age_group', 
            values='PID'
        ).reset_index().rename(columns={'index':'realizedTripMode'})
        data = grouped.to_dict(orient='list')
        return data 

    def make_mode_choice_by_distance_data(self):
        
        mode_df = self.trips_df[['Trip_ID', 'Distance_m', 'realizedTripMode']].copy()
        mode_df.loc[:,'Distance_miles'] = mode_df['Distance_m'] * 0.000621371

        edges = [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7.5, 10, 40]
        bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]
        mode_df.loc[:,'Trip Distance (miles)'] = pd.cut(mode_df['Distance_miles'],
                                                        bins=edges,
                                                        labels=bins,
                                                        right=False).astype(str)

        mode_df_grouped = mode_df.groupby(
            by=['realizedTripMode', 'Trip Distance (miles)']
        ).agg('count').reset_index()

        # rename df column to num_people due to grouping
        mode_df_grouped = mode_df_grouped.rename(
            index=str, columns={'Trip_ID': 'num_trips'})

        mode_df_grouped.loc[:, 'num_trips'] = (
            mode_df_grouped['num_trips'] // self.simulation_count)

        for_plot = mode_df_grouped[['realizedTripMode',
                                    'Trip Distance (miles)',
                                    'num_trips']]
        # max_trips = for_plot.groupby('Trip Distance (miles)')['num_trips'].sum().max() * 1.1

        for_plot = for_plot.rename(columns={'realizedTripMode': 'Trip Mode'})
        for_plot = for_plot.pivot(
            index='Trip Distance (miles)', columns='Trip Mode',
            values='num_trips').fillna(0.0).reset_index()

        for mode in self.modes:
            if mode not in for_plot.columns:
                for_plot[mode] = 0.0
        # colors = Dark2[len(self.modes)]

        data = for_plot.to_dict(orient='list')
        return data 

    def make_congestion_travel_time_by_mode_data(self):

        travel_time = pd.DataFrame(
            self.travel_times_df.set_index("TravelTimeMode\Hour").mean(axis=1)
        ).T

        #travel_time.rename(columns={'ride_hail': 'OnDemand_ride'}, inplace=True)
        # del travel_time['others']

        # max_time = travel_time.max(axis=1)[0] * 1.1
        for mode in self.modes:
            if mode not in travel_time.columns:
                travel_time[mode] = 0

        modes = travel_time.columns.values.tolist()
        palette = Dark2[len(modes)]

        data=dict( 
            x=modes,
            y=[travel_time[mode] for mode in modes],
            color=palette,
        )
        return data

    def make_congestion_travel_time_per_passenger_trip_data(self):

        travel_time = self.travel_times_df.set_index(
            "TravelTimeMode\Hour").T.reset_index()

        for mode in self.modes:
            if mode not in travel_time.columns:
                travel_time[mode] = 0
        
        #travel_time.rename(columns={"ride_hail": "OnDemand_ride"}, inplace=True)
        # del travel_time['others']

        # max_hour = max([int(h) for h in travel_time['index']])
        # if max_hour > 23:
        #     hours = [str(h) for h in range(max_hour + 1)]
        # else:
        #     hours = HOURS
        #     max_hour = 23

        # max_time = travel_time.max().max() * 1.1 

        data = travel_time.to_dict(orient='list')
        return data

    def make_congestion_miles_traveled_per_mode_data(self):
        # get_vmt_dataframe:
        vmt_walk = round(
            self.paths_df[self.paths_df["mode"] == "walk"]["length"].apply(
                lambda x: x * 0.000621371).sum(), 0) / self.simulation_count
        vmt_bus = round(
            self.paths_df[self.paths_df["mode"] == "bus"]["length"].apply(
                lambda x: x * 0.000621371).sum(), 0) / self.simulation_count
        vmt_on_demand = round(
            self.paths_df[self.paths_df["vehicle"].str.contains("rideHailVehicle")]["length"].apply(lambda x: x * 0.000621371).sum(), 0) / self.simulation_count
        vmt_car = round(
            self.legs_df[self.legs_df["Mode"] == "car"]["Distance_m"].apply(
                lambda x: x * 0.000621371).sum(), 0) / self.simulation_count
        vmt = pd.DataFrame(
            {"bus": [vmt_bus], "car": [vmt_car], "ride_hail": [vmt_on_demand],
             "walk" : [vmt_walk]})

        modes = ['ride_hail', 'car', 'walk', 'bus']
        vmt = pd.melt(vmt, value_vars=modes)

        # max_vmt = vmt['value'].max() * 1.1

        palette = Dark2[5]
        data = dict(modes=modes, vmt=[vmt_on_demand, vmt_car, vmt_walk, vmt_bus], 
            color=[palette[0], palette[1], palette[3], palette[4]])
        return data

    def make_congestion_bus_vmt_by_ridership_data(self):
        columns = ["numPassengers", "vehicleType", "length",
                   "departureTime", "arrivalTime"]
        vmt_bus_ridership = self.paths_df[self.paths_df["mode"] == "bus"][columns]
        vmt_bus_ridership.loc[:, 'seatingCapacity'] = vmt_bus_ridership['vehicleType'].apply(
            lambda x: self.seating_capacities[x])
        vmt_bus_ridership.loc[:, 'standingRoomCapacity'] = vmt_bus_ridership['vehicleType'].apply(
            lambda x: self.standing_room_capacities[x])

        vmt_bus_ridership.loc[:, 'ridershipPerc'] = vmt_bus_ridership.apply(
            lambda x: calc_ridership_perc(x), axis=1)

        # Split the travels by hour of the day
        edges = range(0,25*3600,3600)
        vmt_bus_ridership.loc[:, "Hour"] = pd.cut(
            vmt_bus_ridership["departureTime"], 
            bins=edges,
            labels=HOURS,
            include_lowest=True)

        # Group by hours of the day and number of passengers in the bus
        vmt_bus_ridership = vmt_bus_ridership.groupby(
            by=["Hour", "ridershipPerc"])['length'].sum().reset_index()
        edges = [0, 0.01, 50, 100, 150.0, 200.0]
        bins = [
            'empty\n(0 passengers)', 
            'low ridership\n(< 50% seating capacity)', 
            'medium ridership\n(< seating capacity)', 
            'high ridership\n(< 50% standing capacity)',
            'crowded\n(<= standing capacity)'
        ]
        vmt_bus_ridership.loc[:, "ridership"] = pd.cut(
            vmt_bus_ridership["ridershipPerc"], 
            bins=edges,
            labels=bins,
            include_lowest=True)
        vmt_bus_ridership.replace(np.nan, 0, inplace=True)
        vmt_bus_ridership.loc[:, "Hour"] = vmt_bus_ridership["Hour"].astype("int")
        # del vmt_bus_ridership['numPassengers']
        # del vmt_bus_ridership['departureTime']
        # del vmt_bus_ridership['arrivalTime']
        # Completing the dataframe with the missing ridership bins (so that they appear in the plot)
        df = pd.DataFrame([0, 0.0, ""]).T
        df.columns = ["Hour", "length", "ridership"]

        for ridership in bins:
            for hour in range(24):
                if len(vmt_bus_ridership[(vmt_bus_ridership['Hour'] == hour) & (vmt_bus_ridership['ridership'] == ridership)].index) == 0:
                    df.loc[0, "ridership"] = ridership
                    df.loc[0, "Hour"] = hour
                    vmt_bus_ridership = vmt_bus_ridership.append(
                        df, ignore_index=True, sort=False)

        vmt_bus_ridership = vmt_bus_ridership.groupby(
            ['Hour', 'ridership'])['length'].sum().reset_index()

        # translate meters to miles
        vmt_bus_ridership.loc[:, 'length'] = round(
            vmt_bus_ridership['length'].apply(
                lambda x: x * 0.000621371), 0) / self.simulation_count

        vmt_bus_ridership = vmt_bus_ridership.pivot(
            index='Hour',
            columns='ridership', 
            values='length')
        # ymax = vmt_bus_ridership.sum(axis=1).max()*1.1

        # colors = Dark2[len(bins)]

        data = vmt_bus_ridership.reset_index().to_dict(orient='list')
        return data 

    def make_congestion_on_demand_vmt_by_phases_data(self):

        columns = ["numPassengers", "departureTime", "length"]
        vmt_on_demand = self.paths_df[self.paths_df["vehicle"].str.contains("rideHailVehicle")].copy()[columns]
        # Split the travels by hour of the day
        edges = range(0,25*3600,3600)
        vmt_on_demand.loc[:, "Hour"] = pd.cut(vmt_on_demand["departureTime"],
                                              bins=edges,
                                              labels=HOURS,
                                              right=False)
        driving_states = ["fetch", "fare"]
        vmt_on_demand.loc[:, "drivingState"] = pd.cut(
            vmt_on_demand["numPassengers"], bins=[0, 1, 2],
            labels=driving_states, right=False)

        vmt_on_demand = vmt_on_demand.groupby(
            by=["Hour", "drivingState"])['length'].sum().reset_index()
        vmt_on_demand.replace(np.nan, 0, inplace=True)
        vmt_on_demand.loc[:, "Hour"] = vmt_on_demand["Hour"].astype("int")

        # translate meters to miles
        vmt_on_demand.loc[:,'length'] = round(
            vmt_on_demand.loc[:,'length'].apply(
                lambda x: x * 0.000621371), 0) / self.simulation_count

        vmt_on_demand = vmt_on_demand.pivot(
            index='Hour', 
            columns='drivingState',
            values='length')
        vmt_on_demand = vmt_on_demand.reset_index()

        for h in HOURS:
            if int(h) not in vmt_on_demand.index:
                df = pd.DataFrame([int(h), 0.0, 0.0]).T
                df.columns = ['Hour','fare','fetch']
                vmt_on_demand = vmt_on_demand.append(
                    df, ignore_index=True, sort=False)

        # ymax = vmt_on_demand.sum(axis=1).max()*1.1

        # colors = Dark2[3][:len(driving_states)]

        data = vmt_on_demand.sort_values('Hour').to_dict(orient='list')
        return data 

    def make_congestion_travel_speed_data(self):

        trips = self.trips_df[self.trips_df['Duration_sec'] > 0].copy()
        
        trips.loc[:, 'average speed (meters/sec)'] = trips['Distance_m'] / trips['Duration_sec']
        trips.loc[:, 'Average Speed (miles/hour)'] = 2.23694 * trips['average speed (meters/sec)']
        trips.loc[:, 'Start_time_hour'] = trips['Start_time'] / 3600
        
        edges = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
        bins = ['[{}, {})'.format(edges[i], edges[i+1]) for i in range(len(edges)-1)]
        trips.loc[:, 'time_interval'] = pd.cut(
            trips['Start_time_hour'],
            bins=edges,
            labels=bins,
            right=False).astype(str)

        trips = trips.rename(
            index=str, columns={"time_interval": "Start time interval (hour)"})

        grouped = trips.groupby(
            by=['Start time interval (hour)', 'realizedTripMode']
        )['Average Speed (miles/hour)'].mean().reset_index()
        # max_speed = grouped['Average Speed (miles/hour)'].max() * 1.2

        grouped = grouped.pivot(
            index='Start time interval (hour)', 
            columns='realizedTripMode', 
            values='Average Speed (miles/hour)')

        for mode in self.modes:
            if mode not in grouped.columns:
                grouped[mode] = 0.0

        grouped = grouped.reset_index().rename(
            columns={'index':'Start time interval (hour)'})

        data = grouped.to_dict(orient='list')
        return data 

    def make_los_travel_expenditure_data(self):

        trips = self.trips_df.copy()
        trips.loc[:, 'trip_cost'] = np.zeros(trips.shape[0])

        trips.loc[trips['realizedTripMode'] == 'car', 'trip_cost'] = \
            trips[trips['realizedTripMode'] == 'car']['FuelCost'].values + \
            trips[trips['realizedTripMode'] == 'car']['Toll'].values

        fare_modes = ['walk_transit', 'drive_transit', 'ride_hail']
        trips.loc[trips['realizedTripMode'].isin(fare_modes), 'trip_cost'] = \
            trips[trips['realizedTripMode'].isin(fare_modes)]['Fare'].values - \
            trips[trips['realizedTripMode'].isin(fare_modes)]['Incentive'].values

        trips.loc[trips['realizedTripMode'] == 'drive_transit', 'trip_cost'] = \
            trips[trips['realizedTripMode'] == 'drive_transit']['trip_cost'].values + \
            trips[trips['realizedTripMode'] == 'drive_transit']['FuelCost'].values + \
            trips[trips['realizedTripMode'] == 'drive_transit']['Toll'].values

        trips.loc[trips['trip_cost'] < 0,:] = 0
        trips.loc[:, "hour_of_day"] = np.floor(trips.Start_time/3600)

        grouped = trips.groupby(
            by=["realizedTripMode", "hour_of_day"]
        )["trip_cost"].mean().reset_index()
        grouped = grouped[grouped['realizedTripMode'] != 0]
        # max_cost = grouped['trip_cost'].max() * 1.1

        grouped = grouped.pivot(
            index='hour_of_day', 
            columns='realizedTripMode', 
            values='trip_cost')

        for mode in self.modes:
            if mode not in grouped.columns:
                grouped[mode] = 0.0

        grouped = grouped.reset_index().rename(columns={'index':'hour_of_day'})

        data = grouped.to_dict(orient='list')
        return data 

    def make_los_crowding_data(self):

        columns = ["vehicle", "numPassengers", "departureTime", "arrivalTime",
                   "vehicleType"]
        bus_slice_df = self.paths_df[self.paths_df["mode"] == "bus"].copy()[columns]

        bus_slice_df.loc[:, "route_id"] = bus_slice_df['vehicle'].apply(
            lambda x: self.trip_to_route[x.split(":")[1].split('-')[0]])
        bus_slice_df.loc[:, "serviceTime"] = (
            bus_slice_df['arrivalTime'] - bus_slice_df['departureTime']) / 3600
        bus_slice_df.loc[:, "seatingCapacity"] = bus_slice_df['vehicleType'].apply(
            lambda x: TRANSIT_SCALE_FACTOR * self.seating_capacities[x])
        bus_slice_df.loc[:, "passengerOverflow"] = (
            bus_slice_df['numPassengers'] > bus_slice_df['seatingCapacity'])
        # AM peak = 7am-10am, PM Peak = 5pm-8pm, Early Morning, Midday, Late Evening = in between
        bins = [0, 25200, 36000, 61200, 72000, 86400]
        labels = ["Early Morning (12a-7a)", "AM Peak (7a-10a)",
                  "Midday (10a-5p)", "PM Peak (5p-8p)", "Late Evening (8p-12a)"]
        bus_slice_df.loc[:, "servicePeriod"] = pd.cut(
            bus_slice_df['departureTime'],
            bins=bins,
            labels=labels)
        grouped_data = bus_slice_df[bus_slice_df['passengerOverflow']].groupby(
            ["route_id", "servicePeriod"]
        )["serviceTime"].sum().fillna(0).reset_index()
        # max_crowding = grouped_data['serviceTime'].max() * 1.1

        if self.simulation_ids is not None:
            simulation_count = len(self.simulation_ids)
            grouped_data.loc[:, 'serviceTime'] = grouped_data['serviceTime'] // simulation_count

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

        for route_id in self.route_ids:
            if route_id not in set(grouped_data['route_id']):
                df.loc[0, "route_id"] = route_id
                grouped_data = grouped_data.append(
                    df, ignore_index=True, sort=False)

        grouped_data.loc[:, 'route_id'] = grouped_data.loc[:, 'route_id'].astype(str)
        data = grouped_data.to_dict(orient='list')
        return data 

    def make_transit_cb_data(self):

        columns = ["vehicle", "numPassengers", "departureTime", "arrivalTime",
                   "FuelCost", "vehicleType"]
        bus_slice_df = self.paths_df.loc[self.paths_df["mode"] == "bus"].copy()[columns]

        bus_slice_df.loc[:, "route_id"] = bus_slice_df['vehicle'].apply(
            lambda x: self.trip_to_route[x.split(":")[-1].split('-')[0]])
        bus_slice_df.loc[:, "operational_costs_per_bus"] = bus_slice_df['vehicleType'].apply(lambda x: self.operational_costs[x])
        bus_slice_df.loc[:, "serviceTime"] = (bus_slice_df['arrivalTime'] - bus_slice_df['departureTime']) / 3600
        bus_slice_df.loc[:, "OperationalCosts"] = bus_slice_df['operational_costs_per_bus'] * bus_slice_df['serviceTime']

        columns = ["Veh", "Fare"]
        bus_fare_df = self.legs_df[self.legs_df["Mode"] == "bus"].copy()[columns]

        bus_fare_df.loc[:, "route_id"] = bus_fare_df['Veh'].apply(
            lambda x: self.trip_to_route[x.split(":")[-1].split('-')[0].split('-')[0]])
        
        merged_df = pd.merge(bus_slice_df, bus_fare_df, on=["route_id"])

        labels = ["OperationalCosts", "FuelCost", "Fare"]
        costs_labels = labels[:2]
        benefits_labels = ["Fare"]

        grouped_data = merged_df.groupby(by="route_id")[labels].sum()

        # max_cost = grouped_data.sum(axis=1).max() * 1.1
        grouped_data.reset_index(inplace=True)

        # Completing the dataframe with the missing route_ids (so that they appear in the plot)
        df = pd.DataFrame(['', 0.0, 0.0, 0.0]).T
        df.columns = ["route_id"] + labels

        for route_id in self.route_ids:
            if int(route_id) not in grouped_data['route_id'].values:
                df.loc[0, "route_id"] = int(route_id)
                grouped_data = grouped_data.append(
                    df, ignore_index=True, sort=False)
        grouped_data.sort_values('route_id', inplace=True)

        grouped_data.loc[:, 'route_id'] = grouped_data.loc[:, 'route_id'].astype(str)
        grouped_data.loc[:, 'OperationalCosts'] *= -1
        grouped_data.loc[:, 'FuelCost'] *= -1

        # colors = Dark2[len(labels)]

        costs_data = grouped_data[['route_id'] + costs_labels].to_dict(orient='list')
        benefits_data = grouped_data[['route_id'] + benefits_labels].to_dict(orient='list')
        return costs_data, benefits_data

    def make_transit_inc_by_mode_data(self):
        
        columns = ['FuelCost', 'Fare', 'Start_time', 'realizedTripMode', 'Incentive', 'Toll']
        trips = self.trips_df.copy()[columns]

        trips.loc[:, 'trip_cost'] = np.zeros(trips.shape[0])
        trips.loc[:, 'ride_expenditure'] = trips['Fare'] - trips['Incentive']
        ride_modes = set(['walk_transit', 'drive_transit', 'ride_hail'])

        trips.loc[trips['realizedTripMode'] == 'car', 'trip_cost'] = \
            trips[trips['realizedTripMode'] == 'car']['FuelCost'].values + \
            trips[trips['realizedTripMode'] == 'car']['Toll'].values

        trips.loc[trips['realizedTripMode'].isin(ride_modes), 'trip_cost'] = \
            trips[trips['realizedTripMode'].isin(ride_modes)]['ride_expenditure'].values

        trips.loc[trips['realizedTripMode'] == 'drive_transit', 'trip_cost'] += \
            trips[trips['realizedTripMode'] == 'drive_transit']['FuelCost'].values + \
            trips[trips['realizedTripMode'] == 'drive_transit']['Toll'].values

        trips.loc[:, 'Incentives distributed'] = trips['Incentive'].values
        trips.loc[trips['trip_cost'] < 0, 'Incentives distributed'] -= trips[trips['trip_cost'] < 0]['trip_cost'].values

        trips.loc[:, "hour_of_day"] = np.floor(trips['Start_time'] / 3600).astype(int)
        grouped = trips.groupby(
            by=["realizedTripMode", "hour_of_day"]
        )["Incentives distributed"].sum().reset_index()

        # max_incentives = grouped['Incentives distributed'].max() * 1.1
        # if max_incentives == 0:
        #     max_incentives = 100

        grouped = grouped.pivot(
            index='hour_of_day', 
            columns='realizedTripMode', 
            values='Incentives distributed')

        for mode in self.modes:
            if mode not in grouped.columns:
                grouped[mode] = 0.0

        grouped = grouped.reset_index().rename(columns={'index':'hour_of_day'})

        data = grouped.to_dict(orient='list')
        return data 

    def make_toll_revenue_by_time_data(self):
        columns = ["Start_time", "Toll"]
        legs = self.legs_df.copy()[columns]

        hours = range(25)
        seconds = [hour*3600 for hour in hours]

        legs['Hour'] = pd.cut(
            legs['Start_time'],
            bins=seconds,
            labels=[str(h) for h in hours[:-1]]
        )

        legs = legs[['Toll','Hour']].groupby('Hour').sum()
        legs = legs.reset_index()

        return legs.to_dict(orient='list')

    def make_sustainability_25pm_per_mode_data(self):
        
        columns = ["vehicle", "mode", "length", "departureTime"]
        vmt = self.paths_df.copy()[columns]

        # emissions for each mode
        emissions_bus = round(
            vmt[vmt["mode"] == "bus"]["length"].apply(
                lambda x: x * 0.000621371 * 0.0025936648).sum(), 0) / self.simulation_count
        emissions_on_demand = round(
            vmt[vmt["vehicle"].str.contains("rideHailVehicle")]["length"].apply(
                lambda x: x * 0.000621371 * 0.001716086).sum(), 0) / self.simulation_count
        emissions_car = round(
            self.legs_df[self.legs_df["Mode"] == "car"]["Distance_m"].apply(
                lambda x: x * 0.000621371 * 0.001716086).sum(), 0) / self.simulation_count

        emissions = pd.DataFrame(
            {"bus": [emissions_bus], "car": [emissions_car],
             "ride_hail": [emissions_on_demand]})

        modes = ['ride_hail', 'car', 'bus']
        emissions = pd.melt(emissions, value_vars=modes)

        # max_emissions = emissions['value'].max() * 1.1
        
        palette = Dark2[len(modes)]
        data=dict(
            modes=modes,
            emissions=[emissions_on_demand, emissions_car, emissions_bus],
            color=palette)
        return data
