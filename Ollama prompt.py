import pandas as pd
import json
import time
from google import genai
from google.genai import types

# Настройки API из вашего примера
client = genai.Client(
    api_key='sk-kz6d2839Bt_GF0uW19Mhfg',
    http_options=types.HttpOptions(base_url='https://api.artemox.com')
)
MODEL_NAME = 'gemini-1.5-flash'

# Настройки файлов и параметров
INPUT_FILE = 'Эволюция образа России в англоязычном кино (2).xlsx'  # Имя вашего исходного файла
OUTPUT_FILE = 'movies_output.xlsx'  # Имя файла для сохранения результатов
BATCH_SIZE = 3
SAVE_INTERVAL = 6


def process_movies():
    print(f"Загрузка файла {INPUT_FILE}...")
    # Читаем Excel файл
    df = pd.read_excel(INPUT_FILE)

    # Создаем новую колонку "Комментарии", если её еще нет
    if 'Комментарии' not in df.columns:
        df['Комментарии'] = ""

    # Убедимся, что колонки для оценок существуют и имеют тип string
    for col in ['Описание контекста', 'Оценка контекста (персонаж)', 'Оценка контекста (Россия)']:
        if col not in df.columns:
            df[col] = ""

    # Переменная для отслеживания количества обработанных фильмов
    processed_count = 0
    total_movies = len(df)

    print(f"Всего фильмов для обработки: {total_movies}")

    # Проходим по датафрейму батчами по 3 фильма
    for i in range(0, total_movies, BATCH_SIZE):
        batch = df.iloc[i:i + BATCH_SIZE]

        # Подготавливаем список фильмов для промпта
        movies_to_process = batch[['Название фильма', 'Год']].to_dict('records')

        # Системный промпт, объясняющий модель её задачу
        prompt = f"""
        Ты кинокритик и аналитик. Проанализируй следующие {len(movies_to_process)} фильма(ов).
        В каждом из этих фильмов фигурирует Россия, русские персонажи или упоминается СССР. 
        Твоя задача — оценить в каком контексте они использовались.

        Важные правила:
        1. "Оценка контекста (персонаж)" — это образ персонажей из России. Может быть "Положительно", "Нейтрально" или "Отрицательно".
        2. "Оценка контекста (Россия)" — это образ России/СССР в целом (как фон, бэкграунд, государство). Может быть "Положительно", "Нейтрально" или "Отрицательно".
        3. "Описание контекста" — подробно опиши, ПОЧЕМУ персонаж и страна отражены именно так. (Например, персонаж может быть положительным героем, но сама Россия упоминаться в отрицательном ключе как угроза).
        4. "Комментарии" — любые дополнительные интересные детали об образах или стереотипах в этом фильме.

        Список фильмов для анализа:
        {json.dumps(movies_to_process, ensure_ascii=False)}

        Верни ТОЛЬКО валидный JSON-массив, где каждый элемент — объект со следующими ключами:
        "Название фильма", "Год", "Описание контекста", "Оценка контекста (персонаж)", "Оценка контекста (Россия)", "Комментарии".
        """

        print(f"\nОтправка фильмов {i + 1}-{min(i + BATCH_SIZE, total_movies)} в Gemini...")

        try:
            # Отправляем запрос. Заставляем модель вернуть JSON с помощью конфигурации
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4  # Чуть снижаем температуру для большей фактологической точности
                )
            )

            # Парсим полученный JSON
            result_data = json.loads(response.text)

            # Записываем результаты обратно в датафрейм
            for item in result_data:
                # Находим строку по названию и году
                idx_mask = (df['Название фильма'] == item.get('Название фильма')) & (df['Год'] == item.get('Год'))
                if idx_mask.any():
                    idx = df[idx_mask].index[0]

                    df.at[idx, 'Описание контекста'] = item.get('Описание контекста', '')
                    df.at[idx, 'Оценка контекста (персонаж)'] = item.get('Оценка контекста (персонаж)', '')
                    df.at[idx, 'Оценка контекста (Россия)'] = item.get('Оценка контекста (Россия)', '')
                    df.at[idx, 'Комментарии'] = item.get('Комментарии', '')

            processed_count += len(batch)
            print(f"Успешно обработано: {processed_count} из {total_movies}.")

            # Автосохранение каждые 6 фильмов
            # Так как батч = 3, сохранение будет срабатывать на 6, 12, 18 и т.д.
            if processed_count % SAVE_INTERVAL == 0:
                try:
                    df.to_excel(OUTPUT_FILE, index=False)
                    print(f"💾 Автосохранение: Прогресс ({processed_count} фильмов) сохранен в {OUTPUT_FILE}")
                except PermissionError:
                    print(f"⚠️ Ошибка сохранения! Пожалуйста, закройте файл {OUTPUT_FILE}, если он открыт в Excel.")

        except json.JSONDecodeError:
            print("❌ Ошибка: Gemini вернул невалидный JSON. Пропуск батча.")
            print("Ответ модели:", response.text)
        except Exception as e:
            print(f"❌ Произошла ошибка при обращении к API: {e}")

        # Небольшая пауза между запросами, чтобы не спамить API
        time.sleep(2)

    # Финальное сохранение после обработки всех фильмов
    try:
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\n✅ Обработка полностью завершена! Итоговый файл сохранен как {OUTPUT_FILE}")
    except PermissionError:
        print(f"⚠️ Ошибка финального сохранения! Закройте файл {OUTPUT_FILE} и пересохраните данные.")


if __name__ == "__main__":
    process_movies()