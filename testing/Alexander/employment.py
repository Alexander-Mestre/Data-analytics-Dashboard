import requests
import json
import prettytable
import streamlit as st
import pandas as pd

headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": ['CEU4142343001'],"startyear":"2019", "endyear":"2021"})
p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/?registrationkey=1590d05ee887498794d547fc750badd6', data=data, headers=headers)
json_data = json.loads(p.text)
print(json_data)
st.write(json_data)

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

st.write(year)
st.write(period)
st.write(value)

json_df = pd.DataFrame(json_data['Results']['series'][0]['data'])
print(type(json_df))
st.write(json_df)


#data = json.load(open(p.text))

#df = pd.DataFrame(data["result"])

#employment_data = pd.read_json(json_data)
# print("/n")
#print(employment_data)