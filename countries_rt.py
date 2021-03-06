from google.cloud import bigquery
import pandas as pd
import math
import pprint
import csv
pp = pprint.PrettyPrinter(indent = 4)

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from henry_covid19 import common
from henry_covid19.states_data import us_states_list as states_list

def get_country_data(test = False):
    sql  = """
    select country, date, cases, deaths
from covid19.world
order by date
    """
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    final = []
    for i in result:
        final.append([i.get('date'), i.get('country'), i.get('cases'), 
            i.get('deaths')])
    return final


def rates(df,  min_value, window = 3):
    countries = sorted(set(df['country'].tolist()))
    l = []
    for i in countries:
        increase_deaths = common.get_rate_increase(
               df = df[(df['country']==i) & (df['deaths'] > min_value)],
                key = 'deaths', window =window)
        increase_cases = common.get_rate_increase(
               df = df[(df['country']==i) & (df['cases'] > min_value)],
                 key = 'cases', window =window)
        if len(increase_deaths) == 0 or len(increase_deaths) == 1 or math.isnan(increase_deaths[-1]):
            last_value_deaths = None
            double_r_deaths = None
        else:
            last_value_deaths = round(increase_deaths[-1],2)
            double_r_deaths  = common.get_double_rate(last_value_deaths)
        if len(increase_cases) == 0 or len(increase_cases) == 1 or math.isnan(increase_cases[-1]):
            last_value_cases = None
            double_r_cases = None
        else:
            last_value_cases= round(increase_cases[-1],2)
            double_r_cases  = common.get_double_rate(last_value_cases)
        l.append([i, last_value_deaths, double_r_deaths,
            last_value_cases, double_r_cases])
    l.insert(0, ['country', 'deaths_rate', 'deaths_double', 'cases_rate', 'cases_double'])
    with open('html_temp/country_rates.csv', 'w') as write_obj:
        writer = csv.writer(write_obj)
        writer.writerows(l)

def all_countries(df, key, min_value, window = 3, 
        plot_height = 300, plot_width = 300):
    countries = sorted(set(df['country'].tolist()))
    p_list = []
    for i in countries:
        increase = common.get_rate_increase(
               df = df[(df['country']==i) & (df[key] > min_value)],
                key = key, window =window)
        if len(increase) == 0 or len(increase) == 1 or math.isnan(increase[-1]):
            continue
        min_val = increase[-1]
        if min_val < 1:
            n = common.get_days_less_than_0(increase)
            msg = 'under 1 for {n} days'.format(n = n)
        else:
            double_rate = common.get_double_rate(min_val)
            msg = 'doubles every {b} days'.format(b = round(double_rate))
        p = figure( plot_height = plot_height, plot_width = plot_width, 
                title = '{country}: {msg}'.format(
                    country = i, 
                    msg = msg
                    )
                )
        p.line(x = range(len(increase)), y = increase )
        p.line(x = range(len(increase)), y = [1 for x in increase], 
           line_dash = 'dashed', color = 'black')
        p_list.append(p)
    grid = gridplot(p_list, ncols = 4)
    return grid

def main(window = 3):
    df_countries = common.make_dataframe(get_country_data(test = False), country = True)
    rates(df_countries,  min_value = 0, window = window)
    grid = all_countries(df = df_countries, key = 'deaths', min_value = 0, 
            window = window)
    grid2 = all_countries(df = df_countries, key = 'cases', min_value = 0, 
            window = window)
    show(grid2)
    return
    script, div = components(grid)
    script2, div2 = components(grid2)
    with open('html_temp/states_deaths_rt.js', 'w') as write_obj:
        write_obj.write(script)
    with open('html_temp/states_deaths_rt.div', 'w') as write_obj:
        write_obj.write(div)
    with open('html_temp/states_cases_rt.js', 'w') as write_obj:
        write_obj.write(script2)
    with open('html_temp/states_cases_rt.div', 'w') as write_obj:
        write_obj.write(div2)

if __name__ == '__main__':
    main()
