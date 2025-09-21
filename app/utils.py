import pandas as pd
import numpy as np
from scipy.stats import linregress
import requests
import time
import aiohttp
import asyncio
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st

@st.cache_data
def analysis_city(df_city):
  city = df_city['city'].iloc[0]
  df = df_city.copy()
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  df = df.sort_values('timestamp').reset_index(drop=True)

  # 1.1 Скользящее среднее и std, поиск аномалий
  df['temp_smooth'] = df.groupby(['season'])['temperature'].transform(
    lambda x: x.rolling(window=30, center=True).mean()
  )

  smooth_season_profile = df.groupby(['season'])['temp_smooth'].agg(
    temp_mean_smooth = 'mean',
    temp_std_smooth = 'std'
  ).reset_index()

  df = df.merge(smooth_season_profile, on=['season'], how='left')
  df['temp_anomaly'] = np.abs(df['temperature'] - df['temp_mean_smooth']) > 2*df['temp_std_smooth']
  temp_anomaly = df[df['temp_anomaly']].copy()[['timestamp', 'temperature', 'temp_smooth', 'temp_std_smooth']]

  # 1.2 Сезонный профиль: mean, std по сезонам (без скользящего окна)
  season_profile = df.groupby(['season'])['temperature'].agg(
    temp_mean = 'mean',
    temp_std = 'std'
  ).reset_index()

  # 1.3 Тренд
  df['day_index'] = np.arange(len(df))
  slope, intercept, r_value, p_value, std_err = linregress(df['day_index'], df['temperature'])

  if abs(slope) < 1e-8 or p_value > 0.05:
    trend = 'neutral'
  elif slope > 0:
    trend = 'positive'
  else:
    trend = 'negative'

  # 1.4 Общая статистика
  avg_temp = df['temperature'].mean()
  min_temp = df['temperature'].min()
  max_temp = df['temperature'].max()

  return {
      'city': city,
      'avg_temp': avg_temp,
      'min_temp': min_temp,
      'max_temp': max_temp,
      'season_profile': season_profile,
      'trend': trend,
      'temp_anomaly': temp_anomaly
  }

@st.cache_data
def plot_season_profile(season_profile, city):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=season_profile['season'],
        y=season_profile['temp_mean'],
        error_y=dict(type='data', array=season_profile['temp_std']),
        mode='lines+markers',
        name='Seasonal Mean ± STD'
    ))
    fig.update_layout(title=f"Сезонный профиль города — {city}")
    return fig

@st.cache_data
def plot_time_series(city_df, temp_anomaly, city):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=city_df['timestamp'], y=city_df['temperature'],
        mode='lines', name='Temperature'
    ))
    if not temp_anomaly.empty:
        fig.add_trace(go.Scatter(
            x=temp_anomaly['timestamp'], y=temp_anomaly['temperature'],
            mode='markers', name='Anomalies', marker=dict(color='red', size=8)
        ))
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(rangeslider=dict(visible=True), type="date")
    )
    fig.update_layout(title=f"Временной ряд температуры города — {city}")
    return fig

async def get_temp_async(session, city, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    async with session.get(url) as response:
        data = await response.json()
        if response.status == 401:
            raise ValueError(data.get('message'))
        elif response.status != 200:
            raise ValueError(f"Ошибка API ({response.status}): {data.get('message', 'Неизвестная ошибка')}")
        return city, data['main']['temp']
    
async def fetch_temperature(city, api_key):
    async with aiohttp.ClientSession() as session:
        return await get_temp_async(session, city, api_key)

@st.cache_data
def get_temperature(city, api_key):
    try:
        return asyncio.run(fetch_temperature(city, api_key))
    except Exception as e:
        st.error(e)
        return city, None

@st.cache_data   
def get_currnet_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7,8]:
        return 'summer'
    else:
        return 'autumn'

@st.cache_data 
def check_temp_animaly(current_temp, season_profile, season):
    row = season_profile[season_profile['season'] == season]
    mean = row['temp_mean'].values[0]
    std = row['temp_std'].values[0]
    if abs(current_temp - mean) > 2*std:
        return 'Аномальная'
    else:
        return 'Нормальная'