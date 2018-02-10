# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:08:29 2018

@author: Siyan
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
plt.style.use('fivethirtyeight')








def FilePrepare(file_list, col_list):
# transfer file to csv format, based on <col_list>
# file_list: list of string, col_list: string
    
    for file in file_list:
        print('Loading: {}...'.format(file))
        df= pd.read_excel(file+'.xlsx')

        # sort columns by name
        df = df[col_list].sort_index(axis=1)
        print('Transfer to .csv file...\n')
        df.to_csv(file+ '.csv', index=False)
    print ('Done!')






def LoadData(filename, chunksize=100000, index= None):
# load csv to df, set smaller chunksize for small RAM
# filename: string; index: string
    
    temp=[]
    chunk_load=pd.read_csv('Data/'+filename,
                           chunksize=chunksize,
                           engine ='c') # c engine is faster
    # filter data, drop empty columns, set date as index
    print('Loading: {}...'.format(filename))
    for chunk in chunk_load:
            temp.append(chunk)
    print('Done!\n')

    df = pd.concat(temp, ignore_index= True)
    if index!= None:
        df.set_index(index, drop=True, inplace=True) # set CASE_NUMBER as index
    return df




 
def MatchCount (data, target_list, remove_punct= True):
# search name return its frequency in pd series
# input: data (pd series), target_list (string or list of string)
# set <remove_punct> = False for exact match        
    data= data.value_counts()
    if type(target_list)== type('string'): target_list= [target_list]
    index= data.index.values
    return_series= [] # append pd series together 
         
    if remove_punct== True:
        # remove all special characters, punctuation and spaces
        index_remove_punct= []
        for i in index:
            index_remove_punct.append( ''.join(_ for _ in i if _.isalnum()))
            
        for target in target_list:            
            match_list= [] # append names that match specified target
            target= ''.join(_ for _ in target if _.isalnum()).upper()  
            for i, j in enumerate(index_remove_punct): 
                if re.search(target, j): # match value in <index_remove_punct>
                    match_list.append(index[i]) # return value in <index>
            return_series.append(data.loc[match_list])             
    else:     
        for target in target_list:            
            match_list= [] # append names that match specified target 
            target= target.upper()
            for j in index: 
                if re.search(target, j): 
                    match_list.append(j) 
            return_series.append(data.loc[match_list])      
            
    l= len(return_series)
    if l==1:  
        print('1 pandas.Series is returned')
        return return_series[0]  
    else: 
        print('A list of pandas.Series ({} items) is returned'.format(l))
        return return_series
         



#%% process data

# columns included
col_list= ['CASE_NUMBER', 'CASE_STATUS', 'CASE_SUBMITTED', 'DECISION_DATE',
          'SOC_NAME', 'JOB_TITLE', 'EMPLOYER_NAME',
          'FULL_TIME_POSITION','PREVAILING_WAGE',
          'WORKSITE_CITY', 'WORKSITE_STATE']

# file name without .xlsx
file_list= ['H-1B_Disclosure_Data_FY15_Q4',
            'H-1B_Disclosure_Data_FY16',
            'H-1B_Disclosure_Data_FY17']

#FilePrepare(file_list, col_list) # takes couple mins



# load df
df15= LoadData(file_list[0]+ '.csv')
df16= LoadData(file_list[1]+ '.csv')
df17= LoadData(file_list[2]+ '.csv')
df_all= pd.concat([df15, df16, df17], ignore_index= True)




# drop all (76) abnormal/duplicate CASE_NUMBER
df_all= df_all.drop_duplicates(subset=['CASE_NUMBER', 'CASE_STATUS'], keep= False)
df_all.to_csv('H-1B_Disclosure_Data_FY15to17.csv', index=False)

df_ctf= df_all[df_all['CASE_STATUS'].isin(['CERTIFIED', 'Certified-Withdrawn'])]

match= MatchCount(df_ctf['EMPLOYER_NAME'], 'A&Z Pharmaceutical ')
print(match.head())
print(df_all[df_all['EMPLOYER_NAME'].isin( match.index)].head(10))



#%% Plot graph



# plot top 25 visa sponsors
plt.figure(figsize=(8,12))
top_values= df_ctf['EMPLOYER_NAME'].value_counts()[:25].reset_index()
sns.barplot(x= 'EMPLOYER_NAME', y= 'index', data= top_values, palette= 'Blues_d' )
plt.title('Top 25 H-1B Visa Sponsors (2015-2017)')
plt.xlabel('Number of Certified')
plt.ylabel('')
plt.show()
print(top_values)


# plot top 25 JOB_TITLE
plt.figure(figsize=(8,12))
top_values= df_ctf['JOB_TITLE'].value_counts()[:25].reset_index()
sns.barplot(x= 'JOB_TITLE', y= 'index', data= top_values, palette= 'Blues_d' )
plt.title('Top 25 Job Titles (2015-2017)')
plt.xlabel('Number of Certified')
plt.ylabel('')
plt.show()
print(top_values)


# plot top 10 WORKSITE_STATE
plt.figure(figsize=(8,12))
top_values= df_ctf['WORKSITE_STATE'].value_counts()[:10].reset_index()
sns.barplot(x= 'WORKSITE_STATE', y= 'index', data= top_values, palette= 'Blues_d' )
plt.title('Top 10 Working States (2015-2017)')
plt.xlabel('Number of Certified')
plt.ylabel('')
plt.show()
print(top_values)



#%% check duplicate CASE_NUMBER


#case_number= df_ctf.CASE_NUMBER.value_counts()
#dup_case= case_number[case_number>1]
#print ('There are {} duplicate CASE_NUMBER\n'.format(dup_case.sum()))
#
#
#print(df_ctf.head())
#print(df_ctf.info())
#print(df_ctf.shape)



