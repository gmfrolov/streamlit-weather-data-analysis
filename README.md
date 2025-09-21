# Streamlit Weather Data Analysis

Учебный проект по применению фреймворка Streamlit для анализа данных на тему «Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API».

Запустить приложение можно через Streamlit Cloud по ссылке [клик](https://app-weather-data-analysis-bq9ho2tydfwgxbw8ho5nj8.streamlit.app/)

## Установка и запуск локально

```bash
git clone git@github.com:gmfrolov/streamlit-weather-data-analysis.git
cd streamlit-weather-data-analysis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Описание проекта

Приложение позволяет:

- Загружать исторические данные о температуре (CSV)
- Рассчитывать статистику по каждому городу: среднее, минимальное, максимальное, тренд
- Строить интерактивные графики Plotly: сезонный профиль, временной ряд с аномалиями
- Проверять текущую температуру через OpenWeatherMap API и сравнивать с историческим профилем

## Требования
- Python 3.12.3
- Установленные зависимости из `requirements.txt`

## Настройка API

Для проверки текущей температуры нужен API-ключ OpenWeatherMap:

1. Зарегистрироваться на OpenWeatherMap (API Key должен активироваться в течение 2-3 часов)
2. Ввести ключ в соответствующее поле в приложении

## Особенности

- Используется кэширование и сессия Streamlit для корректной работы интерфейса
- Обработка ошибок API-ключа
- Возможность выбора города и отображения только нужных графиков