import streamlit as st
import pandas as pd
from utils import analysis_city, plot_season_profile, plot_time_series, get_temperature, get_currnet_season, check_temp_animaly

if 'city_stats' not in st.session_state:
    st.session_state.city_stats = None
if 'city' not in st.session_state:
    st.session_state.city = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False


st.title('Анализ погоды')

st.markdown('##### Загрузите файл с данными')

data = st.file_uploader('', type='csv')
st.session_state.api_key = st.text_input('Введить ключ API от OpenWeatherMap', value=st.session_state.api_key, type='password')

if data is not None:
    df = pd.read_csv(data)

    # Блок 1: данные
    show_data = st.toggle('Показать исходные данные', value=True)
    if show_data:
        st.write(df)

    # Блок 2: выбор города
    prev_city = st.session_state.city
    cities = df['city'].unique()
    st.session_state.city = st.selectbox(
        'Выберите город для анализа',
        df['city'].unique(),
        index=0 if st.session_state.city is None else list(df['city'].unique()).index(st.session_state.city)
    )

    if prev_city != st.session_state.city:
        st.session_state.analyzed = False
        st.session_state.city_stats = None
        
    # Блок 3: анализ
    st.markdown(f"##### Анализ погоды города: {st.session_state.city}")
    start_compute = st.button('Выполнить анализ')
    df_city = df[df['city']==st.session_state.city].copy()

    if start_compute:
        st.session_state.city_stats = analysis_city(df_city)
        st.session_state.analyzed = True
        
    if st.session_state.analyzed and st.session_state.city_stats:    
        st.markdown(f"""Климатические показатели города — {st.session_state.city}:\n
* Средняя температура — **{st.session_state.city_stats['avg_temp']:.1f}°C**\n
* Минимальная температура — **{st.session_state.city_stats['min_temp']:.1f}°C**\n
* Максимальная температура — **{st.session_state.city_stats['max_temp']:.1f}°C**\n
* Общий температурный тренд — **{st.session_state.city_stats['trend']}**
        """)
        fig_season_profile = plot_season_profile(st.session_state.city_stats['season_profile'], st.session_state.city)
        st.plotly_chart(fig_season_profile)

        fig_time_series = plot_time_series(df_city, st.session_state.city_stats['temp_anomaly'], st.session_state.city)
        st.plotly_chart(fig_time_series)
        

        # Блок 4: текущая температура через API
        if st.session_state.api_key:
            try:
                city_name, current_temp = get_temperature(st.session_state.city, st.session_state.api_key)
                if current_temp is not None:
                    season = get_currnet_season()
                    season_profile = st.session_state.city_stats['season_profile']
                    status = check_temp_animaly(current_temp, season_profile, season)
                    st.metric(f"Текущая температура в {city_name}", f"{current_temp:.1f}°C ({status})")
            except Exception as e:
                st.error(e)
        else:
            st.markdown('##### Чтобы получить данные о текущей температуре, введите API-ключ')

else:
    st.markdown('##### Чтобы продолжить анализ необходимо загрузить файл с данными')


