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

def get_prefix():
    prefix = ['Select Option','State Employment','County Employment']

    choice = st.selectbox('Choose Type:', options=prefix, index=0)

    return choice

def get_sac_code():
    choice = ''
    return choice

def get_type():
    choice =''
    return choice

def create_data():      #Need to get prefix, sac code, and type as a drop down
    option = get_prefix()
         #Figure out how to get the correct JSON info
    if 'Select Option' in option:
        prefix = ''
    elif 'State Employment' in option:    # If user selects State Employment
        prefix = 'CE'
    elif 'County Employment' in option:   # If user selects County Employment
        prefix = 'OE'

    sacCode = '41423430'
    type ='01'
    
    string = prefix + 'U' + sacCode + type
    
    print(string)
    return string

def callApi(string):
    # string = create_data()
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": [string], "startyear":"2010","endyear":"2020"})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/?registrationkey=5590bbd31ba54c5e902eefa0b1e8a23b', data=data, headers=headers)
    json_data = json.loads(p.text)

    print(json_data)

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

def main():
    string = create_data()
    #print(string)
    
    """
    json_data = callApi(string)
    st.title('ECIPDA Dashboard')
    json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
    json_df['monthYear'] = json_df['periodName'] + ' ' + json_df['year']
    st.write(json_df)
    emp_dist = pd.DataFrame(json_df, columns=['value','monthYear'])
    print(emp_dist)

    st.selectbox('Select', ['emp_dist'])

    c = alt.Chart(emp_dist).mark_line().encode(
        x=alt.X('monthYear', axis=alt.Axis(title='Month of Each Year')),
        y='value:Q'
    )
    st.altair_chart(c)
    #st.write(json.dumps(json_data), indent = 4)
    
    """

if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    