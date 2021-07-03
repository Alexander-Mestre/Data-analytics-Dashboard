from re import split
from textwrap import indent
from numpy.core.fromnumeric import sort
from streamlit import cli as stcli
import altair as alt
import streamlit as st
import sys
import pandas as pd
import requests
import json
import prettytable
import csv

# This application takes information from the Bureau of Labor Statistics
# and combines it with Streamlit to make beautiful visuals from the data.
#
# STREAMLIT: https://streamlit.io
# BUREAU OF LABOR STATISTICS: https://www.bls.gov
#
# Created by Domenick Casper and Alexandre Mestre


# A list of all the diffrent Data Sets that the user can choose from.
# Select Option is there for the create_data() function.
def get_prefix():
    prefix = ['Select Option','National Employment, Hours, and Earnings',
        'State and Area Employment, Hours, and Earnings',
        'Occupational Employment and Wage Statistics',
        'Local Area Unemployment Statistics',
        'Mass Layoff Statistics', 'Job Openings and Labor Turnover Survey' ]

    choice = st.selectbox('Choose Type:', options=prefix, index=0)
    return choice

# A list of Whether it's seasonal or not
def get_seasonal():
    seasonal = ['Select Option','Non-Seasonal', 'Seasonal']

    choice = st.selectbox('Seasonal Adjustments:', options=seasonal, index=0)
    return choice

# Will open a csv file where all the different codes are stored to read from
#
# DO WE WANT JSON?
def get_sac_code():
    with open('sac_code.csv', newline='') as csvfile:       #Reading all the Codes from a CSV File?
        choice = csv.reader(csvfile, delimeter=' ')
    return choice

# 
def get_type():
    choice =''
    return choice

# Creating the string that will be passed to the API
def create_data():                                  
    options = get_prefix()                           # Get the Prefix
    seasons = get_seasonal()                         # Get whether it's seasonally ajusted or not
    codes = get_sac_code()                           # Get the SAC Codes that are used in the bls.gov api
    types = get_type()                               
         
    # https://www.bls.gov/help/hlpforma.htm
    if 'Select Option' in options:
        prefix = ''
    elif 'National Employment, Hours, and Earnings' in options:    # If user selects State Employment
        prefix = 'CE'
    elif 'State and Area Employment, Hours, and Earnings' in options:   # If user selects County Employment
        prefix = 'SM'
    elif 'Occupational Employment and Wage Statistics' in options:
        prefix = 'OE'
    elif 'Local Area Unemployment Statistics' in options:
        prefix = 'LA'
    elif 'Mass Layoff Statistics' in options:
        prefix = 'ML'
    elif 'Job Openings and Labor Turnover Survey' in options:
        prefix = 'JT'

    # https://download.bls.gov/pub/time.series/ce/ce.seasonal
    if 'Select Option' in seasons:
        season = ''
    elif 'Non-Seasonal' in seasons:
        season = 'U'
    elif 'Seasonal' in seasons:
        season = 'S'

    # SUPERSECTOR: https://download.bls.gov/pub/time.series/ce/ce.supersector
    # INDUSTRY: https://download.bls.gov/pub/time.series/ce/ce.industry
    if 'Computer and Software' in codes:
        code = '41423430'

    # https://download.bls.gov/pub/time.series/ce/ce.datatype
    if 'All Employees' in types:
        type = '01'

    # sacCode = '41423430'
    # type ='01'
    
    string = prefix + season + code + type
    
    #print(string)
    return string           # The Finished String!

# Based on the bls.gov api found here: https://www.bls.gov/developers/api_python.htm
def callApi(string):
    # string = create_data()
    key = '5590bbd31ba54c5e902eefa0b1e8a23b'        # PUT YOUR API KEY HERE, REGISTER HERE: https://data.bls.gov/registrationEngine/
    headers = {'Content-type': 'application/json'}  # CHECK YOUR EMAIL, CONFIRM THE KEY, AND YOU SHOULD BE ABLE TO USE THE CODE GIVEN
    data = json.dumps({"seriesid": [string], "startyear":"2010","endyear":"2020"})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/?registrationkey=' + key, data=data, headers=headers)
    json_data = json.loads(p.text)

    print(json_data)

    # Iterate through the json_data and create a table in a txt document
    for series in json_data['Results']['series']:
        x=prettytable.PrettyTable(["series id","year","period","value","footnotes"])
        seriesId = series['seriesID']
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes=""
            for footnote in item['footnotes']:
                if footnote:
                    footnotes = footnotes + footnote['text'] + ','
            if 'M01' <= period <= 'M12':
                x.add_row([seriesId,year,period,value,footnotes[0:-1]])
    output = open('text/' + seriesId + '.txt','w')
    output.write (x.get_string())
    output.close()
    
    return json_data

# Main does all the neat stuff, calling functions, creating some of the streamlit application
def main():
    string = create_data()
    #print(string)
    
    # 
    # json_data = callApi(string)
    # st.title('ECIPDA Dashboard')
    # json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
    # json_df['monthYear'] = json_df['periodName'] + ' ' + json_df['year']
    # st.write(json_df)
    # emp_dist = pd.DataFrame(json_df, columns=['value','monthYear'])
    # print(emp_dist)

    # st.selectbox('Select', ['emp_dist'])

    # c = alt.Chart(emp_dist).mark_line().encode(
    #     x=alt.X('monthYear', axis=alt.Axis(title='Month of Each Year')),
    #     y='value:Q'
    # )
    # st.altair_chart(c)
    # #st.write(json.dumps(json_data), indent = 4)
    
    # 

# Allows you to run the application once, and never have to worry about re-running to test code
if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    