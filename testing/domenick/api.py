from re import split
from streamlit import cli as stcli
import streamlit as st
import sys
import pandas as pd
import requests
import json
import prettytable


def callApi():

    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['ENU1606510010']})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/?registrationkey=5590bbd31ba54c5e902eefa0b1e8a23b', data=data, headers=headers)
    json_data = json.loads(p.text)

    #print(json_data)

    # df = pd.DataFrame(json_data)
    # print(df)

    # headers = {'Content-type': 'application/json'}
    # data = json.dumps({"seriesid": ['CUUR0000SA0','SUUR0000SA0'],"startyear":"2011", "endyear":"2014"})
    # p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/?registrationkey=5590bbd31ba54c5e902eefa0b1e8a23b', data=data, headers=headers)
        # json_data = json.loads(p.text)
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

# def createStreamlit(json_data):
#     st.write(json_data)

def main():
    json_data = callApi()
    st.title('ECIPDA Dashboard')
    #st.help(json_data)
    st.write(json_data['seriesID'])
    

if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    