from flask import Flask, jsonify, request, render_template
import requests
import logging


app = Flask(__name__)
my_api_key = 'JGRYVTRcJQdExPXd1N7cIOZglCVT0kVz'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

'''Наверху делаем необходимая подготовка для дальнейшего выполнения проекта'''

''''Задача №1'''
def get_location_key_by_latlon(api_key, latlon):
    '''После того, как ознакомились с документацией к API, реализуем фукнцию получения параметра
     "location key", используя широту и долготу'''
    url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={api_key}&q={latlon}&language=en-us'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['Key']  # Возвращаем ключ местоположения
    else:
        raise Exception(f"Произошла ошибка {response.text} при выполнении запроса")

# Проверим, что код действительно работает для города Нью-Йорка:
# print(get_location_key(my_api_key, '40.7143', '-74.006'))


def get_weather_by_latlon(lat, lon, api_key):
    '''Получаем ключевые параметры прогноза погоды используя lat и lon (только для задания №1)'''
    query_param = f"{lat},{lon}"
    location_key = get_location_key_by_latlon(my_api_key, query_param)
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {"apikey": api_key, "details": "true", "metric": "true"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        forecast = data.get("DailyForecasts", [])[0]

        weather_data = {
            "Температура": forecast["Temperature"]["Maximum"][
                "Value"
            ],
            "Влажность": forecast.get("RealFeelTemperature", {})
            .get("Maximum", {})
            .get("Value", "N/A"),
            "Скорость ветра": forecast["Day"]["Wind"]["Speed"]["Value"],
            "Вероятность дождя": forecast["Day"][
                "PrecipitationProbability"
            ],
        }

        return weather_data
    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"Ошибка HTTP при запросе погоды для locationKey {location_key}: {http_err}"
        )
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(
            f"Ошибка при соединении для запроса погоды для locationKey {location_key}: {conn_err}"
        )
    except requests.exceptions.Timeout as timeout_err:
        logger.error(
            f"Тайм-аут при запросе погоды для locationKey {location_key}: {timeout_err}"
        )
    except requests.exceptions.RequestException as req_err:
        logger.error(
            f"Произошла ошибка при запросе погоды для locationKey {location_key}: {req_err}"
        )
    return None


'''Проверка работы функцию'''
# print(get_weather_by_latlon('51.83', '107.61', 'kWCEDJG2KHGWkW5jrlhR2aSQtEAoe3Ta'))


'''Остальной проект'''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_location_key_by_city(city, API_KEY=my_api_key):
    #Получает уникальный ключ локации  по названию города.
    params = {"apikey": API_KEY, "q": city}
    try:
        response = requests.get("http://dataservice.accuweather.com/locations/v1/cities/search", params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0].get("Key")
        else:
            return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"HTTP error occurred при запросе locationKey для города {city}: {http_err}"
        )
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(
            f"Ошибка соединения при запросе locationKey для города {city}: {conn_err}"
        )
    except requests.exceptions.Timeout as timeout_err:
        logger.error(
            f"Тайм-аут при запросе locationKey для города {city}: {timeout_err}"
        )
    except requests.exceptions.RequestException as req_err:
        logger.error(
            f"Произошла ошибка при запросе locationKey для города {city}: {req_err}"
        )
    return None


def check_bad_weather(temperature, wind_speed, rain_probability):
    '''Моя субъективная оценка плохих погодных условий'''
    if temperature < -15 or temperature > 35:
        return "Плохие погодные условия"
    if wind_speed > 50:
        return "Плохие погодные условия"
    if rain_probability > 60:
        return "Плохие погодные условия"

    return "Хорошие погодные условия"



def get_weather(location_key, API_KEY=my_api_key):
    #Получает прогноз погоды по locationKey.
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {"apikey": API_KEY, "details": "true", "metric": "true"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        forecast = data.get("DailyForecasts", [])[0]

        weather_data = {
            "temperature": forecast["Temperature"]["Maximum"][
                "Value"
            ],  # Температура в Цельсиях
            "humidity": forecast["Day"]["RelativeHumidity"]["Average"],
            "wind_speed": forecast["Day"]["Wind"]["Speed"]["Value"],  # Скорость ветра
            "rain_probability": forecast["Day"][
                "RainProbability"
            ],  # Вероятность дождя
        }
        # Оценка погодных условий
        weather_condition = check_bad_weather(
            weather_data["temperature"],
            weather_data["wind_speed"],
            weather_data["rain_probability"],
        )
        weather_data["weather_condition"] = weather_condition

        return weather_data
    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"HTTP error occurred при запросе погоды для locationKey {location_key}: {http_err}"
        )
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(
            f"Ошибка соединения при запросе погоды для locationKey {location_key}: {conn_err}"
        )
    except requests.exceptions.Timeout as timeout_err:
        logger.error(
            f"Тайм-аут при запросе погоды для locationKey {location_key}: {timeout_err}"
        )
    except requests.exceptions.RequestException as req_err:
        logger.error(
            f"Произошла ошибка при запросе погоды для locationKey {location_key}: {req_err}"
        )
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    #Главная страница приложения
    weather = None
    if request.method == "POST":
        start_city = request.form.get("start_city")
        end_city = request.form.get("end_city")

        if start_city and end_city:
            try:
                # Получение locationKey для начальной и конечной точек
                start_location_key = get_location_key_by_city(start_city)
                end_location_key = get_location_key_by_city(end_city)

                if not start_location_key and not end_location_key:
                    weather = {
                        "error": "Оба города не найдены. Проверьте правильность введённых названий."
                    }
                elif not start_location_key:
                    weather = {
                        "error": f'Начальная точка "{start_city}" не найдена. Проверьте правильность названия.'
                    }
                elif not end_location_key:
                    weather = {
                        "error": f'Конечная точка "{end_city}" не найдена. Проверьте правильность названия.'
                    }
                else:
                    # Получение прогноза погоды для начальной и конечной точек
                    start_weather = get_weather(start_location_key)
                    end_weather = get_weather(end_location_key)

                    if start_weather and end_weather:
                        # Оценка погодных условий для обеих точек
                        weather = {
                            "start_temperature": start_weather["temperature"],
                            "start_humidity": start_weather["humidity"],
                            "start_wind_speed": start_weather["wind_speed"],
                            "start_rain_probability": start_weather["rain_probability"],
                            "start_weather_condition": start_weather["weather_condition"],

                            "end_temperature": end_weather["temperature"],
                            "end_humidity": end_weather["humidity"],
                            "end_wind_speed": end_weather["wind_speed"],
                            "end_rain_probability": end_weather["rain_probability"],
                            "end_weather_condition": end_weather["weather_condition"],
                        }
                    else:
                        weather = {
                            "error": "Не удалось получить данные о погоде для одного из городов."
                        }

            except Exception as e:
                logger.error(f"Ошибка при обработке запроса: {e}")
                weather = {
                    "error": "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."
                }
    return render_template("index.html", weather=weather)



if __name__ == "__main__":
    app.run(debug=True)
