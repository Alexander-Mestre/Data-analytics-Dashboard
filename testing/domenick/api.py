from logging import exception
from re import split
from textwrap import indent
from altair import datasets
from altair.vegalite import data
from streamlit import cli as stcli
import altair as alt
import streamlit as st
import sys
import pandas as pd
import requests
import json
import datetime

# This application takes information from the Bureau of Labor Statistics
# and combines it with Streamlit to make beautiful visuals from the data.
#
# STREAMLIT: https://streamlit.io
# BUREAU OF LABOR STATISTICS: https://www.bls.gov
#
# Created by Domenick Casper and Alexandre Mestre

# Warning message to explain that the API call limit has reached
def get_warning():
    st.warning('Come Back Tomorrow, You have reached the maxiumum number of calls')
    st.stop()

# Opens the dataset.json file and gets a list of the datasets there
def get_data_set():
    with open('dataset.json') as json_file:
        json_obj = json.load(json_file)
        dataset = json_obj['dataset']
    
    return dataset

# Uses the json_file name to get the different drop downs that will be needed
def get_json_file(file):
    print(file)
    if (file):
        with open(file) as json_file:
            json_obj = json.load(json_file)
            codes = json_obj
    else:
        codes = {}
        st.empty()
        
    return codes

# Allows the user to select the dates they want displayed
def get_dates():

    years = [datetime.datetime.today().year - index for index in range(20)]
    years.reverse()

    SD = st.selectbox('Start Year', options=years)
    ED = ''
    if (SD):
        endYears = [year for year in years if year >= SD]
        ED = st.selectbox('End Year', options=endYears)

    return SD, ED

# Get the visual type depending on the users preferences
def get_visual():
    visualTypes = ['Bar', 'Line', 'Point', 'Circle', 'Area', 'Box Plot']
    visual = st.selectbox('Visual Type', options=visualTypes)
    actualVisual = ''

    if (visual == 'Bar'):
        actualVisual = 'mark_bar()'
    elif (visual == 'Line'):
        actualVisual = 'mark_line()'
    elif (visual == 'Point'):
        actualVisual = 'mark_point()'
    elif (visual == 'Circle'):
        actualVisual = 'mark_circle()'
    elif (visual == 'Area'):
        actualVisual = 'mark_area()'
    elif (visual == 'Box Plot'):
        actualVisual = 'mark_boxplot()'
    
    print(actualVisual)
    return actualVisual

def create_visual():
    st.header('Pick from these drop downs')
    string, startDate, endDate, dataType = create_data()
    # st.button('See Visual', on_click = get_visual())
    visual = get_visual()
    print(string)
    
    json_data = callApi(string, startDate, endDate)
    json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
    print(json_df)
    #json_df['monthYear'] = json_df['periodName'] + ' ' + json_df['year']
    # # #json_df['yearTotals'] = (json_df['value'])
    # # st.write(json_df)
    emp_dist = pd.DataFrame(json_df, columns=['value', 'year'])
    print(emp_dist)

    # This creates the visuals!
    if (visual == 'mark_point()'):
        c = alt.Chart(emp_dist).mark_point().encode(
        x=alt.X('year:T', axis=alt.Axis(title='Start Year to End Year')),
        y=alt.Y('value:Q', axis=alt.Axis(title=dataType))
        ).interactive()
    elif (visual == 'mark_bar()'):
        c = alt.Chart(emp_dist).mark_bar().encode(
        x=alt.X('year:T', axis=alt.Axis(title='Start Year to End Year')),
        y=alt.Y('value:Q', axis=alt.Axis(title=dataType))
        ).interactive()
    elif (visual == 'mark_line()'):
        c = alt.Chart(emp_dist).mark_line().encode(
        x=alt.X('year:T', axis=alt.Axis(title='Start Year to End Year')),
        y=alt.Y('value:Q', axis=alt.Axis(title=dataType))
        ).interactive()
    elif (visual == 'mark_circle()'):
        c = alt.Chart(emp_dist).mark_circle().encode(
        x=alt.X('year:T', axis=alt.Axis(title='Start Year to End Year')),
        y=alt.Y('value:Q', axis=alt.Axis(title=dataType))
        ).interactive()
    elif (visual == 'mark_area()'):
        c = alt.Chart(emp_dist).mark_area().encode(
        x=alt.X('year:T', axis=alt.Axis(title='Start Year to End Year')),
        y=alt.Y('value:Q', axis=alt.Axis(title=dataType))
        ).interactive()
    elif (visual == 'mark_boxplot()'):
        c = alt.Chart(emp_dist).mark_boxplot().encode(
        x=alt.X('year:T', axis=alt.Axis(title='Start Year to End Year')),
        y=alt.Y('value:Q', axis=alt.Axis(title=dataType))
        ).interactive()

    theVisual = st.altair_chart(c)          # The completed Graph

    return theVisual

# Creating the string that will be passed to the API
def create_data(): 
    # THE USER SELECTED DATASET
    selection = st.selectbox('Which DataSet would you like information for?', options=list(get_data_set().keys()))
    #print("SELECTION " + selection + " \n")
    # THE FILE NAME OF THE DATA SET
    files = get_data_set()
    #print("FILES " + str(files)  + "\n")
    # THE JSON FILE THE USER WANTED TO SEE DATA 
    dataset = get_json_file(files[selection])
    #print("DATASET " + str(dataset)  + "\n")
    #print(dataset)

    string = ''             # Initializing String

    # NEED TO CLEAN THIS UP TO MAKE IT BETTER & EASIER TO READ
    if (selection == 'Pick Dataset'):
        st.stop()
    else:
        if (selection == 'National Employment, Hours, and Earnings'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Seasonally Adjusted or Not?', options=list(dataset['seasonal'].keys()), key='1')
            sac = dataset['seasonal'][sacSelect]

            industrySelect = st.selectbox('Which Industry?', options=list(dataset['industry'].keys()), key='2')
            industry = dataset['industry'][industrySelect]

            dataTypeSelect = st.selectbox('Which Data Type?', options=list(dataset['data'].keys()), key='3')
            dataType = dataset['data'][dataTypeSelect]

            string = str(prefix) + str(sac) + str(industry) + str(dataType)
            print(string + "\n")      
        elif (selection == 'Occupational Employment and Wage Stats'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Seasonally Adjusted or Not?', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            areaTypeSelect = st.selectbox('Which type of Area?', options=list(dataset['area_type'].keys()))
            area_type = dataset['area_type'][areaTypeSelect]

            areaSelect = st.selectbox('Which Area?', options=list(dataset['area'].keys()))
            area = dataset['area'][areaSelect]

            industrySelect = st.selectbox('Which Industry?', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]

            occupationSelect = st.selectbox('Which Occupation?', options=list(dataset['occupation'].keys()))
            occupation = dataset['occupation'][occupationSelect]

            dataTypeSelect = st.selectbox('Which Data Type?', options=list(dataset['data'].keys()))
            dataType = dataset['data'][dataTypeSelect]

            string = str(prefix) + str(sac) + str(area_type) + str(area) + str(industry) + str(occupation) + str(dataType)
            print(string + "\n")
        elif (selection == 'State/County Employment from Census'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Seasonally Adjusted or Not?', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            areaSelect = st.selectbox('Which Area?', options=list(dataset['area'].keys()))
            area = dataset['area'][areaSelect]

            dataTypeSelect = st.selectbox('Which Data Type?', options=list(dataset['data_type'].keys()))
            dataType = dataset['data_type'][dataTypeSelect]

            sizeSelect = st.selectbox('Which Size?', options=list(dataset['size'].keys()))
            size = dataset['size'][sizeSelect]

            ownerSelect = st.selectbox('Which Owner?', options=list(dataset['ownership'].keys()))
            ownership = dataset['ownership'][ownerSelect]

            industrySelect = st.selectbox('Which Industry?', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]


            string = str(prefix) + str(sac) + str(area) + str(dataType) + str(size) + str(ownership) + str(industry)
            print(string + "\n")
        elif (selection == 'State/Area Employment, Hours, and Earnings'):
            prefix = dataset['prefix'][selection]

            sacSelect = st.selectbox('Seasonally Adjusted or Not?', options=list(dataset['seasonal'].keys()))
            sac = dataset['seasonal'][sacSelect]

            stateSelect = st.selectbox('Which State?', options=list(dataset['state'].keys()))
            state = dataset['state'][stateSelect]

            areaSelect = st.selectbox('Which Area?', options=list(dataset['area'].keys()))
            area = dataset['area'][areaSelect]

            industrySelect = st.selectbox('Which Industry?', options=list(dataset['industry'].keys()))
            industry = dataset['industry'][industrySelect]

            dataTypeSelect = st.selectbox('Which Data Type?', options=list(dataset['data'].keys()))
            dataType = dataset['data'][dataTypeSelect]

            string = str(prefix) + str(sac) + str(state) + str(area) + str(industry) + str(dataType)
            print(string + "\n")
        
        st.info('Years can only have a 20 year difference at most')
        startDate, endDate = get_dates()
        st.subheader('Now Select the Visual you would like to see: ')
    
    return string, startDate, endDate, dataTypeSelect         # the string, start and end date

# Based on the bls.gov api found here: https://www.bls.gov/developers/api_python.htm
@st.cache(suppress_st_warning=True)
def callApi(string, startDate, endDate):
    json_data = ''

    # Get's the data needed
    def get_data():
        # Getting the dates for the user to choose
        # GET YOUR OWN KEY!
        key = '5590bbd31ba54c5e902eefa0b1e8a23b'        # PUT YOUR API KEY HERE, REGISTER HERE: https://data.bls.gov/registrationEngine/
        headers = {'Content-type': 'application/json'}  # CHECK YOUR EMAIL, CONFIRM THE KEY, AND YOU SHOULD BE ABLE TO USE THE CODE GIVEN
        data = json.dumps({"seriesid": [string], "startyear":startDate,"endyear":endDate, "registrationkey":key})
        p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
        json_data = json.loads(p.text)
        return json_data

    pressed = st.button('Request Data', key='dataReturn')

    if (pressed):
        json_data = get_data() 
        json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
        st.write(json_df)
        st.write('Hello Friend!')
        print('SUCKERS'+ str(json_data))
        if(json_data['status'] == 'REQUEST_NOT_PROCESSED'):
            get_warning()           # GET THAT WARNING
    else:
        st.stop()

    st.subheader('Here is the data that is being used to create the chart!')
    
    print('JSON DATA:' + str(json_data))

    return json_data

# Main does all the neat stuff, calling functions, creating some of the streamlit application
def main():
    st.title('ECIPDA Dashboard')
    #create_data()
    
    create_visual()
    


# Allows you to run the application once, and never have to worry about re-running to test code
if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    