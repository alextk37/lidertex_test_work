import plotly.express as px
import pandas as pd
import numpy as np

def plot_total_daily_sales(df):
    """
    Построение интерактивного графика суммарных продаж за 30 дней.
    
    Ожидается, что в DataFrame имеется столбец "График продаж",
    содержащий строку с 30 числами (продажи по дням месяца), разделёнными запятыми.
    Функция суммирует продажи по каждому дню для всех товаров и строит интерактивный график.
    """
    total_sales = [0] * 30
    for sales_str in df['График продаж']:
        try:
            sales_list = [float(x.strip()) for x in sales_str.split(',')]
        except Exception:
            continue
        if len(sales_list) != 30:
            continue
        for i, sale in enumerate(sales_list):
            total_sales[i] += sale

    days = list(range(1, 31))
    data = pd.DataFrame({'День': days, 'Общие продажи': total_sales})
    
    fig = px.line(
        data,
        x='День',
        y='Общие продажи',
        markers=True,
        title='Суммарные продажи за 30 дней'
    )
    fig.update_layout(
        xaxis_title="День месяца",
        yaxis_title="Общее количество продаж"
    )
    return fig

def plot_abc_pie_chart(df):
    """
    Функция разбивает товары по продажам на три группы ABC:
      - Группа A: продажи > 66-й процентиль,
      - Группа B: продажи между 33-м и 66-м процентилем,
      - Группа C: продажи < 33-го процентиля.
    Затем функция строит интерактивную круговую диаграмму с количеством товаров в каждой группе.
    """
    # Вычисляем процентильные пороги для продаж
    q33 = df['Продажи, кол-во'].quantile(0.33)
    q66 = df['Продажи, кол-во'].quantile(0.66)
    
    # Функция для назначения группы по продажам
    def assign_group(sales):
        if sales > q66:
            return 'A'
        elif sales >= q33:
            return 'B'
        else:
            return 'C'
    
    # Применяем функцию к столбцу продаж и получаем группу для каждого товара
    df = df.copy()  # чтобы не изменять исходный DataFrame
    df['ABC_Group'] = df['Продажи, кол-во'].apply(assign_group)
    
    # Подсчитываем количество товаров в каждой группе
    group_counts = df['ABC_Group'].value_counts().reset_index()
    group_counts.columns = ['Группа', 'Количество товаров']
    
    # Строим интерактивный пирог
    fig = px.pie(
        group_counts,
        values='Количество товаров',
        names='Группа',
        title='ABC классификация товаров по продажам',
        color='Группа',
        color_discrete_map={'A': 'green', 'B': 'yellow', 'C': 'red'}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_price_vs_sales(df):
    """
    Строит интерактивный scatter plot для анализа корреляции между ценой и продажами.
    
    Параметры:
      df (DataFrame): Данные, содержащие столбцы "Цена (руб)" и "Продажи, кол-во".
                      Для удобства при наведении также можно включить столбец "Название".
    
    Возвращает:
      fig (Plotly Figure): Интерактивный график корреляции.
    """
    # Строим интерактивный scatter plot с использованием темного шаблона
    fig = px.scatter(
        df,
        x="Цена (руб)",
        y="Продажи, кол-во",
        title='Корреляция "Цена vs Продажи"',
        labels={"Цена (руб)": "Цена (руб)", "Продажи, кол-во": "Продажи, кол-во"},
        hover_data=["Название"]  # отображение названия товара при наведении
    )
    fig.update_layout(template="plotly_dark")
    return fig

def plot_price_segments(df):
    """
    Разбивает товары на три ценовых сегмента (нижний, средний, высокий)
    и строит круговую диаграмму с количеством товаров в каждом сегменте.

    Предполагается, что в DataFrame есть столбец 'Цена (руб)'.
    Вы можете при необходимости изменить границы сегментов.
    """

    # Определим границы сегментов (пример: <500, 500–1500, >1500)
    def get_price_segment(price):
        if price < 500:
            return "Нижний"
        elif price <= 1500:
            return "Средний"
        else:
            return "Высокий"

    # Создадим копию, чтобы не менять исходный DataFrame
    df_copy = df.copy()
    df_copy["Ценовой сегмент"] = df_copy["Цена (руб)"].apply(get_price_segment)

    # Считаем, сколько товаров в каждом сегменте
    segment_counts = df_copy["Ценовой сегмент"].value_counts().reset_index()
    segment_counts.columns = ["Ценовой сегмент", "Количество товаров"]

    # Строим интерактивный пирог
    fig = px.pie(
        segment_counts,
        values="Количество товаров",
        names="Ценовой сегмент",
        title="Распределение товаров по ценовым сегментам"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_reviews_segments(df, low_threshold=20):
    """
    Разбивает товары на три группы по количеству отзывов:
      - "Нет отзывов" если количество отзывов равно 0,
      - "Мало отзывов" если количество отзывов от 1 до low_threshold,
      - "Много отзывов" если количество отзывов больше low_threshold.
      
    Затем строит интерактивную круговую диаграмму с количеством товаров в каждой группе.
    
    Параметры:
      df (DataFrame): Исходный DataFrame с данными, содержащий столбец "Количество отзывов".
      low_threshold (int): Порог для определения "мало отзывов". По умолчанию 20.
    
    Возвращает:
      fig (Plotly Figure): Интерактивный график-пирог.
    """
    # Функция для назначения категории отзывов
    def assign_reviews_category(num_reviews):
        if num_reviews == 0:
            return "Нет отзывов"
        elif num_reviews <= low_threshold:
            return "Мало отзывов (< 100)"
        else:
            return "Много отзывов(> 100)"
    
    # Создаем копию DataFrame, чтобы не изменять исходный
    df_copy = df.copy()
    df_copy["Отзывы_категория"] = df_copy["Количество отзывов"].apply(assign_reviews_category)
    
    # Подсчитываем количество товаров в каждой категории
    counts = df_copy["Отзывы_категория"].value_counts().reset_index()
    counts.columns = ["Отзывы", "Количество товаров"]
    
    # Строим интерактивный пирог
    fig = px.pie(
        counts,
        values="Количество товаров",
        names="Отзывы",
        title="Распределение товаров по количеству отзывов",
        color="Отзывы",
        color_discrete_map={
            "Нет отзывов": "gray",
            "Мало отзывов": "yellow",
            "Много отзывов": "green"
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_ratings_distribution(df):
    """
    Строит интерактивную гистограмму распределения товаров по рейтингу.

    Параметры:
      df (DataFrame): Исходный DataFrame, содержащий столбец "Рейтинг".
      
    Возвращает:
      fig (Plotly Figure): Интерактивный график распределения рейтингов.
    """
    # Строим гистограмму; можно задать количество корзин (nbins) для более детального анализа
    fig = px.histogram(
        df, 
        x="Рейтинг", 
        nbins=20,  
        title="Распределение товаров по рейтингу",
        labels={"Рейтинг": "Рейтинг товара", "count": "Количество товаров"},
        template="plotly_dark"
    )
    fig.update_layout(bargap=0.2)
    return fig

def plot_action_distribution(df):
    """
    Строит круговую диаграмму, показывающую, у скольких товаров есть акция и у скольких нет.
    
    Ожидается, что в DataFrame есть столбец 'Акция'.
    """
    # Создадим копию, чтобы не изменять исходный DataFrame
    df_copy = df.copy()
    
    # Функция для определения, участвует товар в акции или нет
    def is_on_action(action_value):
        # Считаем, что если в поле 'Акция' не пустая строка и не "Нет" (с любым регистром),
        # то товар участвует в акции.
        if not isinstance(action_value, str):
            return "Без акции"
        # Убираем лишние пробелы и приводим к нижнему регистру
        val = action_value.strip().lower()
        if val and val != "нет акции":
            return "С акцией"
        else:
            return "Без акции"
    
    df_copy["action_label"] = df_copy["Акция"].apply(is_on_action)
    
    # Подсчитываем количество товаров в каждой группе
    action_counts = df_copy["action_label"].value_counts().reset_index()
    action_counts.columns = ["Акция", "Количество товаров"]
    
    # Строим интерактивную круговую диаграмму
    fig = px.pie(
        action_counts,
        values="Количество товаров",
        names="Акция",
        title="Распределение товаров по участию в акции",
        color="Акция",
        color_discrete_map={
            "С акцией": "green",
            "Без акции": "red"
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_sales_action_heatmap(df, bin_size=50):
    """
    Строит тепловую карту, показывающую распределение товаров по количеству продаж 
    в зависимости от участия в акции.
    
    Параметры:
      df (DataFrame): Исходный DataFrame, содержащий столбцы "Продажи, кол-во" и "Акция".
      bin_size (int): Размер интервала для группировки продаж (по умолчанию 50).
      
    Возвращает:
      fig (Plotly Figure): Интерактивная тепловая карта.
    """
    # Функция для определения, участвует ли товар в акции
    def is_on_action(action_value):
        if not isinstance(action_value, str):
            return "Без акции"
        val = action_value.strip().lower()
        if val and val != "нет акции":
            return "С акцией"
        else:
            return "Без акции"
    
    df = df.copy()
    # Добавляем метку по акции, если её ещё нет
    if "action_label" not in df.columns:
        df["action_label"] = df["Акция"].apply(is_on_action)
    
    # Определяем диапазон продаж
    min_sales = df["Продажи, кол-во"].min()
    max_sales = df["Продажи, кол-во"].max()
    # Создаем интервалы (бины)
    bins = np.arange(0, max_sales + bin_size, bin_size)
    labels = [f"{int(b)}-{int(b+bin_size-1)}" for b in bins[:-1]]
    
    # Добавляем столбец с интервалами продаж
    df["sales_bin"] = pd.cut(df["Продажи, кол-во"], bins=bins, labels=labels, right=False)
    
    # Строим сводную таблицу: строки – наличие акции, столбцы – бин продаж, значения – количество товаров
    pivot = df.pivot_table(index="action_label", columns="sales_bin", 
                           values="Название", aggfunc="count", fill_value=0)
    
    # Строим интерактивную тепловую карту
    fig = px.imshow(pivot,
                    labels=dict(x="Диапазон продаж", y="Участие в акции", color="Количество товаров"),
                    x=pivot.columns,
                    y=pivot.index,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="Viridis",
                    title="Тепловая карта распределения товаров по продажам и участию в акции")
    
    return fig

def plot_photos_distribution(df, nbins=10):
    """
    Строит интерактивную гистограмму распределения товаров по количеству фотографий в карточке.
    
    Параметры:
      df (DataFrame): Исходный DataFrame, содержащий столбец "Количество фото".
      nbins (int): Количество интервалов (bins) для гистограммы (по умолчанию 10).
    
    Возвращает:
      fig (Plotly Figure): Интерактивный график распределения.
    """
    fig = px.histogram(
        df,
        x="Количество фото",
        nbins=nbins,
        title="Распределение товаров по количеству фотографий",
        labels={"Количество фото": "Количество фотографий", "count": "Количество товаров"},
        template="plotly_dark"
    )
    fig.update_layout(bargap=0.2)
    return fig

def plot_marketplace_days_distribution(df, nbins=10):
    """
    Строит интерактивную гистограмму распределения товаров по количеству дней на маркетплейсе.
    
    Параметры:
      df (DataFrame): Исходный DataFrame, содержащий столбец "Дней на маркетплейсе".
      nbins (int): Количество интервалов (bins) для гистограммы (по умолчанию 10).
      
    Возвращает:
      fig (Plotly Figure): Интерактивный график распределения дней на маркетплейсе.
    """
    fig = px.histogram(
        df,
        x="Дней на маркетплейсе",
        nbins=nbins,
        title="Распределение товаров по количеству дней на маркетплейсе",
        labels={"Дней на маркетплейсе": "Дней на маркетплейсе", "count": "Количество товаров"},
        template="plotly_dark"
    )
    fig.update_layout(bargap=0.2)
    return fig