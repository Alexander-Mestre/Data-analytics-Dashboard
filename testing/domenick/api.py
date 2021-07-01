from re import split
from textwrap import indent
from streamlit import cli as stcli
import altair as alt
import streamlit as st
import sys
import pandas as pd
import requests
import json
import prettytable


def callApi():

    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['CEU4142343001'], "startyear":"2010","endyear":"2020"})
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

def create_data():
    
    return 0

def main():
    json_data = callApi()
    st.title('ECIPDA Dashboard')
    json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
    st.write(json_df)
    emp_dist = pd.DataFrame(json_df, columns=['value','year','periodName'])
    print(emp_dist)

    c = alt.Chart(emp_dist).mark_line().encode(
        x= 'periodName',y='value'
    )
    st.altair_chart(c)
    #st.write(json.dumps(json_data), indent = 4)
    
    

if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    