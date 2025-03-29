import streamlit as st
import pandas as pd
from parser import Parser
import io

from graphs import (plot_total_daily_sales, 
                    plot_price_vs_sales, 
                    plot_price_segments,
                    plot_reviews_segments,
                    plot_ratings_distribution,
                    plot_action_distribution,
                    plot_sales_action_heatmap,
                    plot_photos_distribution,
                    plot_marketplace_days_distribution)
from abc_graph import plot_abc_classic

# Запуск приложения в режиме Wide mode с темным оформлением
st.set_page_config(layout="wide", page_title="Данные о продавце Лидер Дом")

# Инъекция CSS для темного режима
st.markdown(
    """
    <style>
    body {
        background-color: #2e2e2e;
        color: #f0f0f0;
    }
    .reportview-container .main .block-container {
        background-color: #2e2e2e;
        color: #f0f0f0;
    }
    .sidebar .sidebar-content {
        background-color: #1c1c1c;
        color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def load_data():
    parser = Parser()
    return parser.get_combined_data()

# Функция для получения информации о компании
def get_company_info():
    parser = Parser()
    legal_info = parser.get_legal_info()
    seller_info = parser.get_seller_info()
    votes = parser.get_votes()
    return legal_info, seller_info, votes

# Определяем текущую страницу; по умолчанию – информационная ("info")
if 'page' not in st.session_state:
    st.session_state.page = 'info'

# Загружаем данные при первом запуске (для таблицы)
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    st.success("Данные получены")

# Верхняя навигация (добавляем четвёртую колонку для кнопки "Обновить данные")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Информация"):
        st.session_state.page = 'info'
with col2:
    if st.button("Сводная таблица"):
        st.session_state.page = 'table'
with col3:
    if st.button("Графики"):
        st.session_state.page = 'graphs'
with col4:
    if st.button("Обновить данные"):
        st.session_state.data = load_data()
        st.success("Данные обновлены")

# Страница "Информация" (главная)
if st.session_state.page == 'info':
    st.title("Информация о компании :office:")
    
    legal_info, seller_info, votes = get_company_info()
    st.markdown(f"**Краткое название:** {legal_info.get('Краткое название', '')}")
    st.markdown(f"**Полное название:** {legal_info.get('Полное название', '')}")
    st.markdown(f"**ИНН:** {legal_info.get('ИНН', '')}")
    st.markdown(f"**ОГРН:** {legal_info.get('ОГРН', '')}")
    st.markdown(f"**Юридический адрес:** {legal_info.get('Юридический адрес', '')}")
    st.markdown(f"**Торговая марка:** {legal_info.get('Торговая марка', '')}")
    
    st.markdown("### Информация о продавце 🕵️")
    st.markdown(f"🖥️ **Ссылка на магазин:** [Перейти]({seller_info.get('Ссылка на магазин', '')})")
    st.markdown(f":star: **Средняя оценка:** {seller_info.get('Средняя оценка', '')}")
    st.markdown(f"👍 **Общее количество отзывов:** {seller_info.get('Количество отзывов', '')}")
    st.markdown(f"🗓️ **Дата регистрации:** {seller_info.get('Дата регистрации', '')}")
    st.markdown(f"🤑 **Общее количество продаж:** {seller_info.get('Общее количество продаж', '')}")
    st.markdown(f"😄 **Процент выкупа:** {seller_info.get('Процент выкупа', '')}%")
    st.markdown(f"📜 **Джем:** {seller_info.get('Джем', '')}")
    
    st.markdown("### Избранное :heart:")
    st.markdown(f"💟 **Количество добавлений магазина в избранное:** {votes}")

# Страница "Сводная таблица" с фильтрами и таблицей
elif st.session_state.page == 'table':
    st.title("Сводная таблица")
    
    # Преобразуем данные в DataFrame
    df = pd.DataFrame(st.session_state.data)
    
    st.sidebar.subheader("Фильтры")
    
    # Фильтр по названию
    name_filter = st.sidebar.text_input("Поиск:")
    
    # Фильтр по рейтингу
    min_rating = float(df['Рейтинг'].min())
    max_rating = float(df['Рейтинг'].max())
    rating_filter = st.sidebar.slider("Рейтинг", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))
    
    # Фильтр по цене
    min_price = float(df['Цена (руб)'].min())
    max_price = float(df['Цена (руб)'].max())
    price_filter = st.sidebar.slider("Цена (руб)", min_value=min_price, max_value=max_price, value=(min_price, max_price))
    
    # Фильтр по количеству дней на маркетплейсе
    min_days = int(df['Дней на маркетплейсе'].min())
    max_days = int(df['Дней на маркетплейсе'].max())
    days_filter = st.sidebar.slider("Дней на маркетплейсе", min_value=min_days, max_value=max_days, value=(min_days, max_days))
    
    # Фильтр по акции
    action_options = df['Акция'].unique().tolist()
    action_filter = st.sidebar.multiselect("Акция", options=action_options, default=action_options)
    
    # Фильтр по количеству продаж
    min_sales = int(df['Продажи, кол-во'].min())
    max_sales = int(df['Продажи, кол-во'].max())
    sales_filter = st.sidebar.slider("Количество продаж", min_value=min_sales, max_value=max_sales, value=(min_sales, max_sales))
    
    # Фильтр по остаткам
    min_stock = int(df['Общий остаток'].min())
    max_stock = int(df['Общий остаток'].max())
    stock_filter = st.sidebar.slider("Общий остаток", min_value=min_stock, max_value=max_stock, value=(min_stock, max_stock))
    
    # Фильтр по количеству отзывов
    min_reviews = int(df['Количество отзывов'].min())
    max_reviews = int(df['Количество отзывов'].max())
    reviews_filter = st.sidebar.slider("Количество отзывов", min_value=min_reviews, max_value=max_reviews, value=(min_reviews, max_reviews))
    
    # Фильтр по участию в рекламной кампании
    ad_options = ["Все", "Участвует", "Не участвует"]
    ad_filter = st.sidebar.radio("Участие в рекламной кампании", options=ad_options, index=0)
    
    # Применяем фильтры к DataFrame
    filtered_df = df[
        (df['Рейтинг'] >= rating_filter[0]) & (df['Рейтинг'] <= rating_filter[1]) &
        (df['Цена (руб)'] >= price_filter[0]) & (df['Цена (руб)'] <= price_filter[1]) &
        (df['Дней на маркетплейсе'] >= days_filter[0]) & (df['Дней на маркетплейсе'] <= days_filter[1]) &
        (df['Акция'].isin(action_filter)) &
        (df['Продажи, кол-во'] >= sales_filter[0]) & (df['Продажи, кол-во'] <= sales_filter[1]) &
        (df['Общий остаток'] >= stock_filter[0]) & (df['Общий остаток'] <= stock_filter[1]) &
        (df['Количество отзывов'] >= reviews_filter[0]) & (df['Количество отзывов'] <= reviews_filter[1])
    ]
    
    # Фильтр по участию в рекламной кампании
    if ad_filter == "Участвует":
        filtered_df = filtered_df[filtered_df['Средняя рекламная ставка, ₽'] > 0]
    elif ad_filter == "Не участвует":
        filtered_df = filtered_df[filtered_df['Средняя рекламная ставка, ₽'] == 0]
    
    # Определяем столбцы для отображения: убираем столбец оборачиваемости, добавляем SKU
    display_columns = [
        'Название', 'Рейтинг', 'Количество отзывов', 'Акция', 'Цена (руб)',
        'Общий остаток', 'SKU', 'Продажи, кол-во', 'Дней на маркетплейсе', 'Средняя рекламная ставка, ₽'
    ]
    filtered_df = filtered_df[display_columns]
    filtered_df = filtered_df.rename(columns={'Средняя рекламная ставка, ₽': 'Средняя рекламная ставка'})
    
    # Функция для изменения цвета текста в ячейке "Общий остаток":
    def highlight_stock(row):
        try:
            stock = float(row["Общий остаток"])
        except:
            stock = None
        style = ""
        if stock is not None:
            if stock < 30:
                style = 'color: red'
            elif stock < 100:
                style = 'color: yellow'
            else:
                style = 'color: lightgreen'
        return ['' if col != "Общий остаток" else style for col in row.index]
    
    styled_df = filtered_df.style.apply(highlight_stock, axis=1)
    
    # Форматирование числовых столбцов
    styled_df = styled_df.format({
        'Рейтинг': '{:.1f}',
        'Цена (руб)': '{:.2f}',
        'Общий остаток': '{:.0f}',
        'Продажи, кол-во': '{:.0f}',
        'Дней на маркетплейсе': '{:.0f}',
        'Средняя рекламная ставка': '{:.2f}'
    })
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Генерация Excel-файла из отфильтрованного DataFrame
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')
    excel_data = output.getvalue()

    st.download_button(
        label="Скачать Excel",
        data=excel_data,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Страница "Графики"
elif st.session_state.page == 'graphs':
    st.title("Графики")
    df = pd.DataFrame(st.session_state.data)
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Динамика суммарных продаж за 30 дней")
        fig_sales = plot_total_daily_sales(df)
        st.plotly_chart(fig_sales, use_container_width=True)
        message_sales = """Всплеск продаж в начале месяца может быть напрямую связан с подготовкой 8 марта. 
                            Обычно наблюдается повышенный спрос на подарки и сопутствующие товары. 
                            После, как правило, наблюдается спад продаж, из снижения спроса
                            и покупательской способности, что и отражается в падении графика продаж к середине и концу месяца.
                        """
        st.write(message_sales)

        st.subheader("Анализ корреляции между ценой и продажами")
        fig_price = plot_price_vs_sales(df)
        st.plotly_chart(fig_price, use_container_width=True)
        message_correlation = """
            Нет ярко выраженной линейной корреляции. Точки распределены достаточно хаотично,
            хотя и прослеживается тенденция, что самые большие объёмы продаж в среднем ценовом диапазоне. 
                """
        st.write(message_correlation)

        st.subheader("Кластеризация товаров по количеству отзывов")
        fig_reviews = plot_reviews_segments(df, low_threshold=100)  # можно изменить порог, если нужно
        st.plotly_chart(fig_reviews, use_container_width=True)

        message_reviews = """ Значительная часть ассортимента уже успела набрать существенное количество отзывов,
          что повышает доверие покупателей и облегчает принятие решения о покупке. Тем не менее, почти половина товаров
            (около 44%) имеет ограниченное количество отзывов, и им может потребоваться дополнительная реклама или стимулирование 
            оставления отзывов.
            """
        st.write(message_reviews)

        st.subheader("Акции & Продажи")
        fig_sales_action = plot_sales_action_heatmap(df)
        st.plotly_chart(fig_sales_action, use_container_width=True)

        st.subheader("Количество фото в карточке товара")
        fig_photos = plot_photos_distribution(df, nbins=20)  # можно настроить число интервалов
        st.plotly_chart(fig_photos, use_container_width=True)

    with colB:
        st.subheader("ABC анализ")
        fig = plot_abc_classic(df)
        st.plotly_chart(fig, use_container_width=True)
        message_abc = """График подтверждает «правило Парето» (20% товаров приносят 80% продаж) 
                    или близкий к нему принцип. Чем круче поднимается оранжевая кривая кумулятивной 
                    доли в начале и чем длиннее «хвост» справа, тем сильнее выражена концентрация 
                    продаж в ограниченном наборе позиций.
                 """
        st.write(message_abc)

        st.subheader("Ценовая сегментация")
        fig_segments = plot_price_segments(df)
        st.plotly_chart(fig_segments, use_container_width=True)
        message_segments = """
             Ассортимент смещён в сторону среднего и высокого ценовых диапазонов. 
             Это может говорить о том, что компания делает ставку на более дорогие 
             товары либо ориентируется на аудиторию, готовую тратить больше.
        """
        st.write(message_segments)

        st.subheader("Кластеризация товаров по рейтингу")
        fig_ratings = plot_ratings_distribution(df)
        st.plotly_chart(fig_ratings, use_container_width=True)
        message_reviews_rating = """
        Основная масса товаров сосредоточена в диапазоне 4–5 звёзд. 
        Это говорит о том, что большая часть ассортимента получает высокие оценки покупателей, 
        что в целом свидетельствует о хорошем качестве товаров или удовлетворённости клиентов.
            """
        st.write(message_reviews_rating)

        st.subheader("Участие в акции")
        fig_action = plot_action_distribution(df)
        st.plotly_chart(fig_action, use_container_width=True)

        st.subheader("Дней на маркетплейсе")
        fig_colors = plot_marketplace_days_distribution(df, nbins=50)
        st.plotly_chart(fig_colors, use_container_width=True)
