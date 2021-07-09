from logging import exception
from os import wait
from re import split
from textwrap import indent
from tokenize import Ignore
from altair.vegalite import data
from matplotlib.pyplot import pause
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
import pickle as pk

# This application takes information from the Bureau of Labor Statistics
# and combines it with Streamlit to make beautiful visuals from the data.
#
# STREAMLIT: https://streamlit.io
# BUREAU OF LABOR STATISTICS: https://www.bls.gov
#
# Created by Domenick Casper and Alexandre Mestre

# Opens the dataset.json file and gets a list of the datasets there
def get_data_set():

    with open('dataset.json') as json_file:
        json_obj = json.load(json_file)
        dataset = json_obj['dataset']
    
    return dataset

# Uses the json_file name to get the different drop downs that will be needed
def get_json_file(file):
    print(file)
    #st.write('Select a Data Set')
    if (file):
        with open(file) as json_file:
            json_obj = json.load(json_file)
            codes = json_obj
    else:
        codes = {}
        st.empty()
        
    return codes

def get_dates():
    years = [2000, 2001, 2002, 2003, 2004, 2005,
     2006, 2007, 2008, 2009, 2010, 2011, 2012,
      2013, 2014, 2015, 2016, 2017, 2018, 2019, 
      2020, 2021]


    SD = st.selectbox('Start Year', options=years)

    endYears = [year for year in years if year >= SD]
    #print(endYears)
    if (SD):
        ED = st.selectbox('End Year', options=endYears)
    
    

    return SD, ED

def get_visual():
    visualTypes = ['Bar', 'Line', 'Point']
    visual = st.selectbox('Visual Type', options=visualTypes)
    actualVisual = ''

    if (visual == 'Bar'):
        actualVisual = 'mark_bar()'
    elif (visual == 'Line'):
        actualVisual = 'mark_line()'
    elif (visual == 'Point'):
        actualVisual == 'mark_point()'

    return actualVisual

# Creating the string that will be passed to the API
def create_data(): 
    # THE USER SELECTED DATASET
    selection = st.selectbox('Datasets', options=list(get_data_set().keys()))
    print("SELECTION " + selection + " \n")
    # THE FILE NAME OF THE DATA SET
    files = get_data_set()
    print("FILES " + str(files)  + "\n")
    # THE JSON FILE THE USER WANTED TO SEE DATA 
    dataset = get_json_file(files[selection])
    print("DATASET " + str(dataset)  + "\n")
    #print(dataset)

    string = ''             # Initializing String

    if (selection == 'Pick Dataset'):
        st.stop()
    else:
        if (selection == 'National Employment, Hours, and Earnings'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Select', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            industrySelect = st.selectbox('Select', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]

            dataTypeSelect = st.selectbox('Select', options=list(dataset['data'].keys()))
            dataType = dataset['data'][dataTypeSelect]

            string = str(prefix) + str(sac) + str(industry) + str(dataType)
            print(string + "\n")
        
        elif (selection == 'Occupational Employment and Wage Stats'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Select', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            areaTypeSelect = st.selectbox('Select', options=list(dataset['area_type'].keys()))
            area_type = dataset['area_type'][areaTypeSelect]

            areaSelect = st.selectbox('Select', options=list(dataset['area'].keys()))
            area = dataset['area_type'][areaSelect]

            industrySelect = st.selectbox('Select', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]

            occupationSelect = st.selectbox('Select', options=list(dataset['occupation'].keys()))
            occupation = dataset['occupation'][occupationSelect]

            dataTypeSelect = st.selectbox('Select', options=list(dataset['data'].keys()))
            dataType = dataset['data'][dataTypeSelect]

            string = str(prefix) + str(sac) + str(area_type) + str(area) + str(industry) + str(occupation) + str(dataType)
            print(string + "\n")

        elif (selection == 'State/County Employment from Census'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Select', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            areaSelect = st.selectbox('Select', options=list(dataset['area'].keys()))
            area = dataset['area'][areaSelect]

            dataTypeSelect = st.selectbox('Select', options=list(dataset['data_type'].keys()))
            dataType = dataset['data_type'][dataTypeSelect]

            sizeSelect = st.selectbox('Select', options=list(dataset['size'].keys()))
            size = dataset['size'][sizeSelect]

            ownerSelect = st.selectbox('Select', options=list(dataset['ownership'].keys()))
            ownership = dataset['ownership'][ownerSelect]

            industrySelect = st.selectbox('Select', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]


            string = str(prefix) + str(sac) + str(area) + str(dataType) + str(size) + str(ownership) + str(industry)
            print(string + "\n")

        elif (selection == 'State/Area Employment, Hours, and Earnings'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Select', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            stateSelect = st.selectbox('Select', options=list(dataset['state'].keys()))
            state = dataset['state'][stateSelect]

            areaSelect = st.selectbox('Select', options=list(dataset['area'].keys()))
            area = dataset['area'][areaSelect]

            industrySelect = st.selectbox('Select', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]

            dataTypeSelect = st.selectbox('Select', options=list(dataset['data'].keys()))
            dataType = dataset['data'][dataTypeSelect]

            string = str(prefix) + str(sac) + str(state) + str(area) + str(industry) + str(dataType)
            print(string + "\n")

    return string          # The Finished String!

# Based on the bls.gov api found here: https://www.bls.gov/developers/api_python.htm
def callApi(string):
    startDate, endDate = get_dates()                # Getting the dates for the user to choose
    key = '5590bbd31ba54c5e902eefa0b1e8a23b'        # PUT YOUR API KEY HERE, REGISTER HERE: https://data.bls.gov/registrationEngine/
    headers = {'Content-type': 'application/json'}  # CHECK YOUR EMAIL, CONFIRM THE KEY, AND YOU SHOULD BE ABLE TO USE THE CODE GIVEN
    data = json.dumps({"seriesid": [string], "startyear":startDate,"endyear":endDate})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/?registrationkey=' + key, data=data, headers=headers)
    json_data = json.loads(p.text)

    print('JSON DATA:' + str(json_data))


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
    visual = get_visual()
    #print(string)
    
    #st.button('Create Visual',)

    # json_data = callApi(string)
    # st.title('ECIPDA Dashboard')
    # json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
    # print(json_df)
    # json_df['monthYear'] = json_df['periodName'] + ' ' + json_df['year']
    # st.write(json_df)
    # emp_dist = pd.DataFrame(json_df, columns=['value','monthYear', 'year'])
    # print(emp_dist)



    # c = alt.Chart(emp_dist).mark_line().encode(
    #     x=alt.X('year:T', axis=alt.Axis(title='Month of Each Year')),
    #     y='value:Q'
    # )
    # print(type(c))
    # st.altair_chart(c)
    # st.write(json.dumps(json_data), indent = 4)
    


# Allows you to run the application once, and never have to worry about re-running to test code
if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    