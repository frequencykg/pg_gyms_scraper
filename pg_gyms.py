"""Scrap the pg website for number of climbers in the gym using beautiful soup"""

from bs4 import BeautifulSoup
import urllib.request
import codecs
import re
import json
import pandas as pd
import click
import time
import threading
import datetime


EARTHTREKS_GOLDEN = "GOL"
EARTHTREKS_TIMONIUM = "TIM"
EARTHTREKS_ROCKVILLE = "ROC"
EARTHTREKS_CRYSTAL_CITY = "CRY"
EARTHTREKS_COLUMBIA = "COL"
MOVEMENT_BAKER = "DEN"
MOVEMENT_BOULDER = "BDR"
PG_BELMONT = "BEL"
PG_PORTLAND = "PDX"
PG_SUNNYVALE = "SUN"
EARTHTREKS_HAMPDEN = "HMD"
MOVEMENT_RINO = "RNO"
EARTHTREKS_ENGLEWOOD = "ENG"
PG_FOUNTAIN_VALLEY = "FTV"
PG_SANTA_CLARA = "SCA"


def pg_current_capacity(location=None):
    """Gets the current capacity of one of the El Cap family gyms"""
    page = urllib.request.urlopen("https://portal.rockgympro.com/portal/public/dd60512aa081d8b38fff4ddbbd364a54/occupancy?&iframeid=occupancyCounter&fId=1515")

    bay_area_reservations = page.read()

    pg_html = BeautifulSoup(bay_area_reservations, "html.parser")

    data_regex = re.compile("var data = ({[\\s\\S]*?});")
    data_regex_result = data_regex.search(str(pg_html.body.script))

    pg_counter_data_raw = data_regex_result.group(1).replace("'", "\"")
    last_comma_index = pg_counter_data_raw.rindex(",")
    if last_comma_index > 0:
        pg_counter_data_raw = pg_counter_data_raw[:last_comma_index] + pg_counter_data_raw[last_comma_index+1:]

    pg_counter_data = json.loads(pg_counter_data_raw)
    if location:
        return pg_counter_data[location]
    else:
        return pg_counter_data


# print(pg_current_capacity(location=PG_BELMONT))

#TODO: remove the column sublabel from the df and csv file

def record_data_to_log(location, file_name):
    #get data from pg by using pg_current_capacity()
    new_line = pg_current_capacity(location)
    #create new dataframe using pd from this result
    dataframe_to_add_to = pd.DataFrame(new_line, index=[new_line["lastUpdate"]])
    #append to csv using .to_csv
    dataframe_to_add_to.to_csv(file_name, mode="a", header=False)

# while True:
#     record_data_to_log(PG_BELMONT, "pg_belmont_data.csv")

#CLI definitions (command line interface)
@click.command()
@click.option(
    "--start",
    prompt="enter start date and time",
    type=click.DateTime(),
    help="The date and time that this program starts running."
)
@click.option(
    "--end",
    prompt="enter end date and time",
    type=click.DateTime(),
    help="The date and time that this program stops running."
)
@click.option(
    "--interval_min",
    default=15.0,
    help="interval_min specifies the time between each capacity check."
)
@click.option(
    "--output_filename",
    default="pg_belmont_data.csv",
    help="The CSV file to write to."
)
@click.option(
    "--location",
    default=PG_BELMONT,
    help="Gym location ID string."
)
def pg_data_logger_command(start, end, interval_min, output_filename, location):
    current = datetime.datetime.now()
    countdown = start - current
    print('Starting data logger in '+str(countdown.total_seconds())+' seconds ('+str(start)+' to '+str(end)+') every '+str(interval_min)+' minutes...')
    logger_loop = threading.Timer(countdown.total_seconds(), pg_data_logger_loop, [interval_min, end, output_filename, location])
    logger_loop.start()

def pg_data_logger_loop(interval_min, end, output_filename, location):
    if datetime.datetime.now() + datetime.timedelta(minutes=interval_min) < end:
        print("Recording new data!!! " + str(datetime.datetime.now()))
        record_data_to_log(location, output_filename)
        next_run = threading.Timer(interval_min*60, pg_data_logger_loop, [interval_min, end, output_filename, location])
        next_run.start()
    else:
        print("Done recording data!")

if __name__ == "__main__":
    pg_data_logger_command()