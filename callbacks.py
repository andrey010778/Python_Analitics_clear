from dash import Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import settings as st
import plotly.io as pio

# Установка кастомной паллетки цветов для всех графиков plotly
pio.templates['custom'] = pio.templates['plotly'].update(
    layout=dict(colorway=st.MY_PALETTE)
)

pio.templates.default='custom'


#df = pd.read_csv('Clear_dash_new.csv')



def format_days(days):
    #Функция для правильного склонения слова 'день'
        
    days = round(days)
    if days % 10 == 1 and days % 100 != 11:
        return f"{days} день"
    elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
        return f"{days} дня"
    else:
        return f"{days} дней"


def register_callbacks(app):
    @app.callback(
        Output('dept-line-chart', 'figure'),
        Output('customer-bar-chart', 'figure'),
        Output('responsible-pie-chart', 'figure'),
        Output('stats-container', 'children'),
        Input('month-selector', 'value'),
        Input('dept-selector', 'value'),
        Input('customer-selector', 'value'),
        Input('responsible-selector', 'value')
    )
    def update_graphs(selected_months, selected_depts, selected_customers, selected_responsibles):
        # Фильтрация данных
        filtered_df = df.copy()

        month_names = {
            '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
            '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
            '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}
        
        if selected_months:
            filtered_df = filtered_df[filtered_df['month'].isin(selected_months)]
        if selected_depts:
            filtered_df = filtered_df[filtered_df['Department'].isin(selected_depts)]
        if selected_customers:
            filtered_df = filtered_df[filtered_df['Customer'].isin(selected_customers)]
        if selected_responsibles:
            filtered_df = filtered_df[filtered_df['Responsible'].isin(selected_responsibles)]

        dept_data = filtered_df.groupby(['month', 'Department'])['Sum'].sum().reset_index()
        dept_data['month_name'] = dept_data['month'].str[5:7].map(month_names) + ' ' + dept_data['month'].str[:4]

        customer_data = filtered_df.groupby('Customer')['Sum'].sum().reset_index()
        customer_data = customer_data.sort_values('Sum', ascending=False)


        # 1. Линейный график по отделам
        line_fig = px.line(
            data_frame=dept_data,
            x='month_name',
            y='Sum',
            color='Department',
            labels={
                    'amount': 'Сумма (руб)',
                    'month_name': 'Месяц',
                    'Department': 'Отделы'
                },
            markers=True
            #title='Динамика по отделам'
        )

        
        line_fig.add_trace(
            go.Scatter(
            x=dept_data['month_name'],
            y=dept_data.groupby('month_name')['Sum'].transform('mean'),  # Среднее значение
            name='Линия тренда',
            mode='lines+markers',
            line=dict(color='green', width=3, dash='dash'),
            )
        )       
        line_fig.update_layout(
            #legend_title_text='Отделы',
            xaxis_title='Месяцы',
            yaxis_title='Сумма, руб.',
            xaxis={'tickangle': 45},
            font=dict(family='Inter, sans-serif'),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            #plot_bgcolor=st.PLOT_BACKGROUND - нет области рисования у pie
            paper_bgcolor=st.PAPER_BACKGROUND
        )
        # 2. Столбчатая диаграмма по заказчикам
        bar_fig = px.bar(
            data_frame=customer_data,            
            x='Customer',
            y='Sum',
            labels={
                    'Sum': 'Сумма (руб)',
                    'Customer': 'Заказчик'
                },
            #title='Суммы по заказчикам'
        )

        bar_fig.update_layout(
            legend_title_text='Заказчики',
            xaxis_title='Заказчики',
            yaxis_title='Сумма, руб.',
            xaxis={'tickangle': 45},
            font=dict(family='Inter, sans-serif'),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            #plot_bgcolor=st.PLOT_BACKGROUND - нет области рисования у pie
            paper_bgcolor=st.PAPER_BACKGROUND
        )

        # 3. Круговая диаграмма по ответственным
        pie_fig = px.pie(
            filtered_df.groupby('Responsible')['Sum'].sum().reset_index(),
            names='Responsible',
            values='Sum',
            #title='Распределение по ответственным, %'
        )

        pie_fig.update_layout(
            legend_title_text='Ответственные',
            #title='Распределение по ответственным',
            #title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            #title_x=st.GRAPH_TITLE_ALIGN,
            #title_font_weight=st.GRAPH_TITLE_WEIGHT,
            font=dict(family='Inter, sans-serif'),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            #plot_bgcolor=st.PLOT_BACKGROUND - нет области рисования у pie
            paper_bgcolor=st.PAPER_BACKGROUND
        )

        # 4. Статистика
        stats = dbc.ListGroup([
            dbc.ListGroupItem(f'Количество счетов: {len(filtered_df)}'),
            dbc.ListGroupItem(f'Общая сумма: {filtered_df['Sum'].sum():,.0f} ₽'),
            dbc.ListGroupItem(f'Медианное значение по сумме счёта: {filtered_df['Sum'].median():,.0f} ₽'),
            dbc.ListGroupItem(f'Среднее значение по сумме счёта: {filtered_df['Sum'].mean():,.0f} ₽'),
            dbc.ListGroupItem(f'Среднее значение по выполнению: {format_days(filtered_df['Exec_time'].mean())}'),
            dbc.ListGroupItem(f'Среднее время оплаты: {format_days(filtered_df['Payment_time'].mean())}'),
        ]) 

        return line_fig, bar_fig, pie_fig, stats


