import pandas as pd
import plotly.express as px
import re

# --- НАСТРОЙКИ ---
INPUT_FILE = 'Africa_china.xlsx'
OUTPUT_IMAGE = "china_top10_sectors_final_rus_4k.png"

# Словарь стран
COUNTRY_MAP = {
    "Angola": "Ангола", "Ethiopia": "Эфиопия", "Kenya": "Кения",
    "Nigeria": "Нигерия", "Egypt": "Египет", "Sudan": "Судан",
    "Zambia": "Замбия", "Cameroon": "Камерун", "Ghana": "Гана",
    "Cote d'Ivoire": "Кот-д'Ивуар", "Côte d’Ivoire": "Кот-д'Ивуар"
}

# Словарь отраслей (включая новые)
SECTOR_MAP = {
    "Energy": "Энергетика", "Transport": "Транспорт", "Transportation": "Транспорт",
    "Mining": "Горнодобыча", "Non-energy Mining": "Горнодобыча (неэнергет.)",
    "ICT": "ИКТ и связь", "Information and Communication Technology": "ИКТ и связь",
    "Government": "Госуправление", "Public Administration": "Госуправление",
    "Financial Sector": "Финансовый сектор", "Defense and Military": "Оборона и безопасность",
    "Defense": "Оборона и безопасность", "Social Protection": "Социальная защита",
    "Other Social": "Соц. инфраструктура", "Industry": "Промышленность",
    "Agriculture": "Сельское хозяйство", "Water": "Водоснабжение",
    "Health": "Здравоохранение", "Education": "Образование",
    "Action Relating to Debt": "Операции с долгом", "Other": "Прочее"
}


def clean_amount(val):
    if pd.isna(val) or not isinstance(val, str): return 0
    match = re.search(r'\$(\d+\.?\d*)([MB])', val)
    if match:
        num = float(match.group(1))
        return num if match.group(2) == 'B' else num / 1000.0
    return 0


def create_top10_sector_v5():
    try:
        print("Запуск универсального парсинга...")
        df = pd.read_excel(INPUT_FILE)

        current_sector = "Прочее"
        current_country = None
        data_rows = []

        for i, row in df.iterrows():
            # Превращаем все ячейки строки в список строк для удобного поиска
            vals = [str(v).strip() for v in row.values]

            # 1. Пропускаем технический мусор
            if any("collapse" in v.lower() for v in vals): continue

            # 2. Ищем СЕКТОР (обычно первая ячейка не пустая, а в 4-й есть 'loans')
            # Или ячейка содержит название сектора из нашего словаря
            col0 = vals[0]
            if pd.notna(row.iloc[0]) and 'loan' in str(row.iloc[3]).lower():
                current_sector = col0.split(',')[0].strip()
                continue

            # 3. Ищем СТРАНУ
            # Логика: если ячейка совпадает с ключом в COUNTRY_MAP
            for v in vals[:2]:  # Проверяем первые две колонки
                if v in COUNTRY_MAP:
                    current_country = v
                    break

            # 4. Сбор данных проекта
            # Если в 3-й колонке (индекс 2) стоит число — это Год
            year_val = str(row.iloc[2])
            if year_val.isdigit() and current_country in COUNTRY_MAP:
                amount_str = str(row.iloc[4])
                data_rows.append({
                    'Country': current_country,
                    'Sector': current_sector,
                    'Amount_Billion': clean_amount(amount_str)
                })

        if not data_rows:
            print("Ошибка: Данные все еще не найдены. Попробуем вывести структуру первой строки с данными:")
            print(df.head(5))
            return

        full_df = pd.DataFrame(data_rows)
        full_df['Страна'] = full_df['Country'].map(COUNTRY_MAP)
        full_df['Отрасль'] = full_df['Sector'].map(SECTOR_MAP).fillna(full_df['Sector'])

        final_df = full_df.groupby(['Страна', 'Отрасль'])['Amount_Billion'].sum().reset_index()

        # Сортировка для визуализации
        sort_order = final_df.groupby('Страна')['Amount_Billion'].sum().sort_values(ascending=True).index
        final_df['Страна'] = pd.Categorical(final_df['Страна'], categories=sort_order, ordered=True)

        print(f"Найдено стран: {final_df['Страна'].nunique()}. Создание графика...")
        fig = px.bar(
            final_df, x='Amount_Billion', y='Страна', color='Отрасль',
            title="Секторальная структура кредитов КНР в Африке (2000–2024)",
            labels={'Amount_Billion': 'Объем кредитов (млрд USD)', 'Страна': ''},
            orientation='h', template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Prism,
            width=3840, height=2160
        )

        fig.update_layout(
            title_font=dict(size=85, family="Arial Black"),
            legend=dict(font_size=35, title_font_size=40, x=1.02, y=0.5),
            xaxis=dict(tickfont_size=35, title_font_size=40),
            yaxis=dict(tickfont_size=40),
            margin=dict(l=250, r=950, t=250, b=250),
            annotations=[dict(
                x=1, y=-0.08, xref='paper', yref='paper',
                text='Источник: Boston University Global Development Policy Center (2024)',
                showarrow=False, font=dict(size=30, color="grey")
            )]
        )

        fig.write_image(OUTPUT_IMAGE, engine="kaleido")
        print(f"Успех! Файл: {OUTPUT_IMAGE}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    create_top10_sector_v5()