import requests
import csv


def get_forecast(headers, lat_lon, limit):
    """
    Запрос данных по API Яндекс Погоды
    :param headers: Ключ для доступа к API
    :param lat_lon: координаты
    :param limit: количество дней
    :return: ответ API
    """
    params = {
        'limit': limit,
        'lat': lat_lon[0],
        'lon': lat_lon[1]
    }
    return requests.get(url='https://api.weather.yandex.ru/v2/forecast', headers=headers, params=params)


def get_city(fc) -> str:
    """
    Получение названия города из JSON
    :param fc: json с прогнозными данными
    :return: Название города
    """
    return fc.json()["geo_object"]["locality"]["name"]


def get_attrs(fc, rain_cond):
    """
    Получение атрибутов из JSON
    :param fc: json с Прогнозными данными
    :param rain_cond: Погодные статусы осадков
    :return: Словарь с атрибутоми прогноза
    """
    days = fc.json()["forecasts"]
    attrs = []
    for date in range(len(days)):
        for hour in days[date]["hours"]:
            attrs.append([days[date]["date"],
                          hour["hour"],
                          hour["temp"],
                          hour["pressure_mm"],
                          hour["condition"] in rain_cond])
    return attrs


def recreate_file(fieldnames):
    """
    Очистка файла и запись заголовков
    :param fieldnames: Наименования столбцов
    :return: None
    """
    with open('weather.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def write_file(fieldnames, city_name, dates):
    """
    Запись в файл по городам
    :param fieldnames: Наименования столбцов
    :param city_name: Наименование города
    :param dates: атрибуты прогноза
    :return: Nome
    """
    with open('weather.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for day in dates:
            writer.writerow({'city': city_name,
                             'date': day[0],
                             'hour': day[1],
                             'temperature_c': day[2],
                             'pressure_mm': day[3],
                             'is_rain': 1 if day[4] is True else 0
                             })


if __name__ == '__main__':
    # Но так-же ключ можно положить в toml, yaml или любой другой удобный формат для конфигов
    access_key = 'bbc120d2-daac-4089-80f5-e77bce57ea07'
    key = {
        'X-Yandex-Weather-Key': access_key
    }

    # Координаты городов: https://time-in.ru/coordinates/russia
    cities = {
        'Москва':          ['55.7522', '37.6156'],
        'Казань':          ['55.7887', '49.1221'],
        'Санкт-Петербург': ['59.9386', '30.3141'],
        'Тула':            ['54.1961', '37.6182'],
        'Новосибирск':     ['55.0415', '82.9346']
    }

    # список погодных условий, подразумевающих дождь: https://yandex.ru/dev/weather/doc/ru/concepts/forecast-test#fact
    rain_conditions = ['light-rain',
                       'rain',
                       'heavy-rain',
                       'showers',
                       'wet-snow',
                       'thunderstorm',
                       'thunderstorm-with-rain',
                       'thunderstorm-with-hail']

    # Количество дней
    days = '7'

    # Перечень полей в CSV файле
    fieldnames = ['city', 'date', 'hour', 'temperature_c', 'pressure_mm', 'is_rain']

    recreate_file(fieldnames)
    # Запросы по API
    for city, coord in cities.items():
        forecast = get_forecast(headers=key, lat_lon=coord, limit=days)
        city_name = get_city(forecast)
        dates = get_attrs(forecast, rain_conditions)
        print(city_name)
        print(dates[0])
        write_file(fieldnames, city_name, dates)
