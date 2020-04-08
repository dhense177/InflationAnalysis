import pandas as pd
import numpy as np
import pickle, os, csv, requests, zipfile, io, re
from bs4 import BeautifulSoup



def load_zip(f, path):
    '''
        Load zip file and extract elements
    '''
    r = requests.get(f)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    z.extractall(path=path)


def get_table(url_path):
    '''
        Locate table of big mac data and parse it for relevant figures
        Return: Columns and associated data
    '''
    r = requests.get(url_path, auth=('user', 'pass'))
    soup = BeautifulSoup(r.content, 'html.parser')

    table_headers = soup.find('table').find('thead')
    cols = table_headers.find_all('th')

    data = soup.find('table').find('tbody')
    data = data.find_all('td',class_=None)
    return cols, data


def create_df(cols,data):
    '''
        Create DataFrame and set columns to data from scraped table
        Return: Newly-created DataFrame
    '''
    df = pd.DataFrame()
    for x in range(0,len(cols)):
        df[cols[x].text] = [data[i].text for i in range(x,len(data),len(cols))]

    #Year column instead of date
    df['year'] = pd.DatetimeIndex(df.date).year.values
    df.drop('date', axis=1, inplace=True)
    return df


def clean_and_filter(df,yr1,yr2):
    '''
        Filter for mid-year American prices between provided years
        Return: Annual Bic Mac prices in America for years between those provided 
    '''
    #Get just America
    df = df[df.name=='United States'].reset_index()
    #Remove duplicates
    no_dupe = df[df.year.isin(df.year.value_counts()[df.year.value_counts()==1].index)]
    #Get second value from all duplicates (middle of year value)
    dupe = df[df.year.isin(df.year.value_counts()[df.year.value_counts()>1].index)][1::2]

    df = pd.concat([no_dupe,dupe]).sort_values(by='year')
    bmi_vals = df[(df.year<yr2)&(df.year>yr1)]['local_price'].values.astype(float)

    return bmi_vals

if __name__=='__main__':
    filepath = '/home/dhense/PublicData/Economic_analysis/'
    bigmac_pickle = 'bigmac.pickle'

    if not os.path.isfile(filepath+bigmac_pickle):
        url_path = 'https://github.com/TheEconomist/big-mac-data/blob/master/source-data/big-mac-historical-source-data.csv'
        cols, data = get_table(url_path)
        df1 = create_df(cols, data)

        url_path2 = 'https://github.com/TheEconomist/big-mac-data/blob/master/source-data/big-mac-source-data.csv'
        cols2, data2 = get_table(url_path2)
        df2 = create_df(cols2, data2)

        df2.drop('GDP_dollar',axis=1, inplace=True)

        df = pd.concat([df1,df2])

        print("...saving pickle")
        tmp = open(filepath+bigmac_pickle,'wb')
        pickle.dump(df,tmp)
        tmp.close()
    else:
        print("...loading pickle")
        tmp = open(filepath+bigmac_pickle,'rb')
        df = pickle.load(tmp)
        tmp.close()
