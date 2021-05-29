# Как подготовить файлы
1. Прогоняем все csv файлы через скрипт [convert_csv.py](convert_csv.py)
2. Запускаем [preprocess_atmos.py](preprocess_atmos.py) для обработки `atmos.pickle`
3. Запускаем [preprocess_meteo.py](preprocess_meteo.py) для обработки `meteo.pickle`
4. Привязываем данные о метеостанциях с помощью [merge_weather_test.py](merge_weather_test.py),
[merge_weather_traffic.py](merge_weather_traffic.py) и [merge_weather_train.py](merge_weather_test.py)
5. Используем [prepare_train.py](prepare_train.py) для получения смёрженного `train-merged.pickle` и тестирования нескольких моделей
6. Используем [prepare_test.py](prepare_test.py) для получения смёрженного `test-merged.pickle` над которым можно делать предсказания
7. Обучаем модели с помощью скрипта [prepare_models.py](prepare_models.py)
8. Скармливаем полученным моделям файл `test-merged.pickle`
9. PROFIT
