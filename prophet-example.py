# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13i2Czd8pJ-vEXapk8QzRTSTQnQ8AMWeg
"""

#以下のブログを参考にしました
#https://facebook.github.io/prophet/docs/quick_start.html
#http://data.gunosy.io/entry/change-point-detection-prophet

!pip install pandas_datareader

import numpy as np
import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import timeit

print(timeit.timeit('"-".join(str(n) for n in range(100))', number=10000))

start = datetime.datetime(2012, 1, 1)
end = datetime.datetime(2018, 5, 31)

brand_list = ['NVDA', 'AMD', 'GOOGL', 'SNE', 'AAPL']

f = web.DataReader(brand_list, 'morningstar', start, end)

print(f.head())

f_u = f.unstack(0)

f_u['Close'].head()

train_begin = '2017-07-01'
train_begin = pd.to_datetime(train_begin) #str to datetime
train_timedelta = 60 #days

train_end = train_begin +datetime.timedelta(days=train_timedelta+1)

print(train_begin, train_end)

df = f_u['Close']

f_u['Close'].plot(grid=True)
plt.axvline(x=train_begin, lw=1, color='black') 
plt.axvline(x=train_end, lw=1, color='black') 

plt.show()

!pip install fbprophet

from fbprophet import Prophet

temp = df.loc[:, 'GOOGL'].rename('y')
temp = pd.DataFrame(temp)
temp['ds'] = temp.index

model = Prophet()
model.fit(temp)

future = model.make_future_dataframe(periods=365)
future.tail()

forecast = model.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

#forecast = model.predict(future)
model.plot(forecast);

model.plot_components(forecast);

model.params['delta']

import seaborn as sns

#変化点情報のデータフレーム, dateを抽出
def getDateCp(temp, model):
    df_changepoints = temp.iloc[model.changepoints.index]
    df_changepoints['delta'] = model.params['delta'].ravel()

    #変化点の取得
    df_changepoints['ds'] = df_changepoints['ds'].astype(str) 
    df_changepoints['delta'] = df_changepoints['delta'].round(2)
    df_selection = df_changepoints[df_changepoints['delta'] != 0] 
    date_changepoints = df_selection['ds'].astype('datetime64[ns]').reset_index(drop=True)
    return df_changepoints, date_changepoints

df_changepoints, date_changepoints = getDateCp(temp, model)

#変化度をplot
sns.set(style='whitegrid')
ax = sns.factorplot(x='ds', y='delta', data=df_changepoints, kind='bar', color='royalblue', size=4, aspect=2)
ax.set_xticklabels(rotation=90)

figure = model.plot(forecast)
for dt in date_changepoints:
    plt.axvline(dt,ls='--', lw=1)
plt.show()

#ケース2
#特定期間だけ抜き出す

#パラメータ
train_begin = '2012-05-01'
train_timedelta = 120 #days

#ウィンドウ幅
train_begin = pd.to_datetime(train_begin) #str to datetime
train_end = train_begin +datetime.timedelta(days=train_timedelta+1) #timedelta幅でとる

#モデル作成
model2 = Prophet()
model2.fit(temp.loc[train_begin:train_end])

#5日後まで予測
future2 = model2.make_future_dataframe(periods=30)
forecast2 = model2.predict(future2)

df_changepoints2, date_changepoints2 = getDateCp(temp.loc[train_begin:train_end], model2)

#変化度をplot
sns.set(style='whitegrid')
ax = sns.factorplot(x='ds', y='delta', data=df_changepoints2, kind='bar', color='royalblue', size=4, aspect=2)
ax.set_xticklabels(rotation=90)

model2.plot(forecast2)
for dt in date_changepoints2[date_changepoints2 <= train_end]:
  plt.axvline(dt, ls='--', lw=1)

import math

#異常度の閾値 
alpha_threshold = 0.15

#モデルplot
model2.plot(forecast2)

#おそい
#for idx, val in enumerate(df_changepoints2['delta']):
#    if abs(val) > abs(alpha_threshold) :
#      print("異常疑惑発見: ", df_changepoints2.index[idx],  "異常度の閾値", val)
#      dt = df_changepoints2.index[idx]
#      plt.axvline(dt, ls='--', lw=1, c='red') 

#はやい
for val in df_changepoints2['delta'][abs(df_changepoints2['delta']) > abs(alpha_threshold)]:
      print("異常疑惑発見2: ", df_changepoints2.index[df_changepoints2['delta']==val],  "異常度の閾値", val)
      dt = df_changepoints2.index[df_changepoints2['delta']==val]
      plt.axvline(dt, ls='--', lw=1, c='red')