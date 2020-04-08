import pandas as pd
import numpy as np
import pickle, os


def filter_ce(df_ce):
    df_ce = df_ce[df_ce['QINTRVYR']==2018]
    df_ce = df_ce[df_ce['TOTEXPPQ']>0]
    df_ce = df_ce[df_ce['HEALTHPQ']>=0]
    df_ce = df_ce[df_ce['FOODPQ']>=0]
    df_ce = df_ce[df_ce['HOUSPQ']>=0]
    df_ce = df_ce[df_ce['TRANSPQ']>=0]
    return df_ce


def rename_cols_rows(df_ce):
    df_ce_cats = df_ce[['HOUSPQ','FOODPQ','TRANSPQ','HEALTHPQ']].stack().reset_index().rename(columns={'level_1':'Category',0:'Values'})[['Category','Values']]

    df_ce_cats['Category'] = df_ce_cats['Category'].replace({'HOUSPQ':'HOUSING','FOODPQ':'FOOD','TRANSPQ':'TRANSPORTATION','HEALTHPQ':'HEALTHCARE'})

    return df_ce_cats


def percent_costs(df_ce):
    df_perc = df_ce
    df_perc = df_perc[df_perc['HEALTHPQ']>0]
    df_perc = df_perc[df_perc['FOODPQ']>0]
    df_perc = df_perc[df_perc['HOUSPQ']>0]
    df_perc = df_perc[df_perc['TRANSPQ']>0]

    df_perc['Housing'] = df_perc['HOUSPQ']/df_perc['TOTEXPPQ']
    df_perc['Food'] = df_perc['FOODPQ']/df_perc['TOTEXPPQ']
    df_perc['Healthcare'] = df_perc['HEALTHPQ']/df_perc['TOTEXPPQ']
    df_perc['Transportation'] = df_perc['TRANSPQ']/df_perc['TOTEXPPQ']

    df_ce_perc = df_perc[['Housing','Food','Transportation','Healthcare']].stack().reset_index().rename(columns={'level_1':'Category',0:'Values'})[['Category','Values']]

    return df_ce_perc











if __name__=='__main__':
    #Import detailed consumer expenditure interview survey data
    df_ce1 = pd.read_csv('/home/dhense/PublicData/ce_survey/interviews/2018/intrvw18/fmli181x.csv')
    df_ce2 = pd.read_csv('/home/dhense/PublicData/ce_survey/interviews/2018/intrvw18/fmli182.csv')
    df_ce3 = pd.read_csv('/home/dhense/PublicData/ce_survey/interviews/2018/intrvw18/fmli183.csv')
    df_ce4 = pd.read_csv('/home/dhense/PublicData/ce_survey/interviews/2018/intrvw18/fmli184.csv')
    df_ce5 = pd.read_csv('/home/dhense/PublicData/ce_survey/interviews/2018/intrvw18/fmli191.csv')

    df = pd.concat([df_ce1,df_ce2,df_ce3,df_ce4,df_ce5])

    df_ce = filter_ce(df)
    df_ce_cats = rename_cols_rows(df_ce)
    df_ce_perc = percent_costs(df_ce)
