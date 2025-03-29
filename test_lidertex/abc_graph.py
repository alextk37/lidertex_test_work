import pandas as pd
import plotly.graph_objects as go

def plot_abc_classic(df):
    """
    Строит интерактивный график для классического ABC‑анализа:
      1) Сортируем товары по убыванию продаж ('Продажи, кол-во').
      2) Считаем кумулятивную долю продаж.
      3) Классифицируем:
         - A: до 80% совокупных продаж
         - B: с 80% до 95%
         - C: свыше 95%
      4) Рисуем столбиковую диаграмму (продажи) + линию кумулятивной доли.
    """

    # Создаём копию DataFrame, чтобы не менять исходный
    df_abc = df.copy()
    
    # Сортируем по убыванию продаж
    df_abc.sort_values(by='Продажи, кол-во', ascending=False, inplace=True)
    
    # Считаем суммарные продажи
    total_sales = df_abc['Продажи, кол-во'].sum()
    
    # Вычисляем кумулятивную сумму и долю
    cumulative = 0
    cumulative_list = []
    share_list = []
    abc_groups = []
    
    for sales in df_abc['Продажи, кол-во']:
        cumulative += sales
        share = cumulative / total_sales  # доля от 0 до 1
        cumulative_list.append(cumulative)
        share_list.append(share)
    
    # Добавляем столбцы в DataFrame
    df_abc['CumulativeSales'] = cumulative_list
    df_abc['CumulativeShare'] = share_list
    
    # Классифицируем каждую строку
    # A – пока кумулятивная доля ≤ 0.80
    # B – от 0.80 до 0.95
    # C – всё что выше 0.95
    for share in df_abc['CumulativeShare']:
        if share <= 0.80:
            abc_groups.append('A')
        elif share <= 0.95:
            abc_groups.append('B')
        else:
            abc_groups.append('C')
    
    df_abc['ABC_Group'] = abc_groups
    
    # Подготовим данные для построения графика
    # x – это индекс (или порядковый номер товара)
    # y – это продажи
    x_values = list(range(len(df_abc)))  # порядковые номера товаров
    y_sales = df_abc['Продажи, кол-во']
    y_share = df_abc['CumulativeShare']
    
    # Создаём фигуру
    fig = go.Figure()
    
    # Столбики: продажи
    fig.add_trace(go.Bar(
        x=x_values,
        y=y_sales,
        name='Продажи',
        marker_color='rgba(100,150,255,0.8)'
    ))
    
    # Линия: кумулятивная доля (в процентах), на второй оси
    fig.add_trace(go.Scatter(
        x=x_values,
        y=[s * 100 for s in y_share],  # переводим долю в %
        name='Кумулятивная доля (%)',
        mode='lines+markers',
        line=dict(color='orange', width=2)
    ))
    
    # Настраиваем оси
    fig.update_layout(
        title="Классический ABC-анализ",
        xaxis=dict(title="Товары (отсортированы по убыванию продаж)"),
        yaxis=dict(title="Продажи (шт)", side='left'),
        yaxis2=dict(
            title="Кумулятивная доля, %",
            overlaying='y',
            side='right',
            range=[0, 110]  # запас сверху
        ),
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified'
    )
    
    # Привязываем вторую ось ко второму трейсу (линия кумулятивной доли)
    fig.data[1].yaxis = 'y2'
    
    # Добавим горизонтальные линии для 80% и 95%
    fig.add_shape(
        type='line', 
        xref='paper', x0=0, x1=1, 
        yref='y2', y0=80, y1=80,
        line=dict(color="red", width=1, dash="dash")
    )
    fig.add_shape(
        type='line', 
        xref='paper', x0=0, x1=1, 
        yref='y2', y0=95, y1=95,
        line=dict(color="red", width=1, dash="dash")
    )
    
    return fig