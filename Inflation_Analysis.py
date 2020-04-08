import os, pickle
import pandas as pd
import numpy as np


def create_df(df,df_series):
    '''
        Format dataframe columns, merge together
    '''
    dfs = [df,df_series]
    for d in dfs:
        d.columns = d.columns.map(str.strip)
        for col in d.columns:
            d[col] = d[col].astype(str).str.strip()


    df = pd.merge(df, df_series,how='left',on='series_id')
    df = df[['series_id','series_title','year','period','value','category_code', 'subcategory_code', 'item_code', 'demographics_code','characteristics_code']]

    df['value'] = df['value'].astype(float)
    df['year'] = df.year.astype(int)

    return df


def find(key, dictionary):
    '''
        Recursively looks for dictionary key, returns associated value
    '''
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result

def mask(df,yr,exp):
    '''
        Returns median value for given expense category and year
    '''
    if {'item_code'}.issubset(df.columns):
        return df[(df.year==yr)&(df['item_code']==exp)]['value'].values[0]
    else:
        return np.median(df[df.year==yr][exp])

def calc_inc_rates(totals, years, total_inc):
    '''
        Calculates annual income growth rates for each year
        Returns income figures and growth rates
    '''
    inc_list = []
    inc_rates = []
    for yr in years:
        inc_total = mask(totals,yr,total_inc)
        inc_min1_total = mask(totals,yr-1,total_inc)
        inc_rates.append(inc_total/inc_min1_total)
        inc_list.append(inc_total)
    return inc_rates, inc_list

def calc_cost_rates(totals, years, exp_vars, total_exp):
    '''
        Calculates annual costs and growth rates for each category of cost items

        Calculaltes annual total costs and total cost growth rates by weighting each cost category by it's proportion of the total cost among all categories used

        Returns annual growth rates and cost figures
    '''
    rate_list=[]
    cost_list = []
    year_dict = {}
    for yr in years:
        vars_dict = {}

        yr_total = mask(totals,yr,total_exp)
        yr_min1_total = mask(totals,yr-1,total_exp)

        year_cost = 0
        for exp in exp_vars:
            rate_dict = {}

            yr_val = mask(totals,yr,exp)
            yr_min1_val = mask(totals,yr-1,exp)
            year_cost += yr_val

            rate = yr_val/yr_min1_val
            weight = (yr_val+yr_min1_val)/(yr_total+yr_min1_total)

            rate_dict['Rate'] = rate
            rate_dict['Weight'] = weight

            vars_dict[exp] = rate_dict

        cost_list.append(year_cost)
        total_weights = sum([x for x in find('Weight',vars_dict)])
        rate_sum = 0
        for i in exp_vars:
            rate_sum += (vars_dict[i]['Weight']/total_weights)*vars_dict[i]['Rate']
        rate_list.append(rate_sum)

        year_dict[yr] = vars_dict

    return rate_list, cost_list, year_dict

def median_mean(df,yrs):
    '''
        Calculate difference between median and mean to make sure mean of 40th-60th
        percentiles is a good proxy for median
    '''
    diff_list = []
    for yr in yrs:
        diff_list.append(np.mean(df[df.year==yr]['HINCP'])-np.median(df[df.year==yr]['HINCP']))
    return diff_list

def gini(array):
    '''
        Calculate the Gini coefficient of a numpy array.
        based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
        from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    '''

    array = array.flatten() #all values are treated equally, arrays must be 1d
    if np.amin(array) < 0:
        array -= np.amin(array) #values cannot be negative
    array += 0.0000001 #values cannot be 0
    array = np.sort(array) #values must be sorted
    index = np.arange(1,array.shape[0]+1) #index per array element
    n = array.shape[0]#number of array elements
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))) #Gini coefficient


def cpi_calc(df_cpi,yr1,yr2):
    '''
        Calculate inflation relative to yr2 (latest year), annual inflation from CPI figures
        Return: dictionary with relative (to latest year) inflation rates, annual inflation rates
    '''
    inflation_dict= {}
    inflation_list = []
    for yr in range(yr1,yr2+1):
        cpi = df_cpi[df_cpi.YEAR==yr]['AVG']
        cpi2 = df_cpi[df_cpi.YEAR==yr2]['AVG']
        cpi_min1 = df_cpi[df_cpi.YEAR==yr-1]['AVG']
        inflation = float(cpi2)/float(cpi)
        inflation_dict[yr]=inflation
        inflation_list.append(float(cpi)/float(cpi_min1))

    return inflation_dict, inflation_list

if __name__=='__main__':
    filepath = '/home/dhense/PublicData/ZNAHealth/'
    url_path = 'https://download.bls.gov/pub/time.series/cx/'

    cx_pickle = 'cx.pickle'
    if not os.path.isfile(filepath+'intermediate_files/'+cx_pickle):
        df_series = pd.read_csv(url_path+'cx.series',sep='\t')
        df = pd.read_csv(url_path+'cx.data.1.AllData',sep='\t')

        df = create_df(df,df_series)

        print("...saving pickle")
        tmp = open(filepath+'intermediate_files/'+cx_pickle,'wb')
        pickle.dump(df,tmp)
        tmp.close()
    else:
        print("...loading pickle")
        tmp = open(filepath+'intermediate_files/'+cx_pickle,'rb')
        df = pickle.load(tmp)
        tmp.close()
