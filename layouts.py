import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
import datetime as dt
import settings as st
from dotenv import load_dotenv
import os 

#df = pd.read_csv('Clear_dash_new.csv')

# Загрузка переменных из .env файла
load_dotenv()

# Получение путей из переменных окружения
excel_file_path = os.getenv('EXCEL_FILE_PATH')
sheet_name = os.getenv('SHEET_NAME')  # значение по умолчанию

try:
    df = pd.read_excel(
        excel_file_path,
        skiprows=1,
        sheet_name=sheet_name,
        engine='openpyxl'  # для .xlsx файлов
    )
    
    print("Данные успешно загружены")
    
    
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")



df = df.rename(columns={'Дата счёта':'Acc_date', '№ дог':'Contr_num', 
                        'Заказчик':'Customer', 'Подразделение': 'Department',
                        'Наименование работ': 'Job_desc', 'Сумма': 'Sum',
                        'Дата оплаты': 'Payment_date', 'Дата акта': 'Exec_date',
                        'Ответственный':'Responsible', 'Срок платежа':'Payment_time',
                        'Cрок выполнения':'Exec_time'})

df.drop(['Contr_num', 'Job_desc'], axis=1, inplace=True)
df = df.dropna(subset=['Acc_date'])

# df['month'] = df['Acc_date'].dt.to_period('M')

# Вместо Period используем строки везде
df['month'] = df['Acc_date'].dt.strftime('%Y-%m')  # Формат "2024-01"



def get_layouts():
    # Русские названия месяцев для селектора
    month_names = {
        '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
        '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
        '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
    }
    
    # Формируем варианты для селектора месяцев
    month_options = [
        {'label': f"{month_names[mon[5:7]]} {mon[:4]}", 'value': mon} 
        for mon in sorted(df['month'].unique())
    ]
    
    
    
    # Получаем уникальные значения для фильтров
    months = sorted(df['month'].unique())
    departments = sorted(df['Department'].unique())
    customers = sorted(df['Customer'].unique())
    responsibles = sorted(df['Responsible'].unique())

    return dbc.Container(
        [
            # 1. Заголовок
            html.H1("Анализ дополнительных работ отдела эксплуатации", className='header-title'), 
                   #className="mt-4 mb-4 text-center", 
                   #style={"fontWeight": "bold"}),

            # 2. Блок селекторов
            dbc.Card([
                dbc.CardHeader("Фильтры", className='filter-label'), #className="font-weight-bold bg-light"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id="month-selector",
                                options=[{'label': m, 'value': m} for m in months],
                                value=months[-1:],  # Последний 1 месяц по умолчанию
                                multi=True,
                                placeholder="Месяц...",
                                className='filter-dropdown',
                                style=st.DROPDOWN_STYLE,
                            ), width=3, xs=12, md=3
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="dept-selector",
                                options=[{'label': dep, 'value': dep} for dep in departments],
                                multi=True,
                                placeholder="Отдел...",
                                className='filter-dropdown',
                                style=st.DROPDOWN_STYLE,
                            ), width=3, xs=12, md=3
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="customer-selector",
                                options=[{'label': ctm, 'value': ctm} for ctm in customers],
                                multi=True,
                                placeholder="Заказчик...",
                                className='filter-dropdown',
                                style=st.DROPDOWN_STYLE,
                            ), width=3, xs=12, md=3
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="responsible-selector",
                                options=[{'label': resp, 'value': resp} for resp in responsibles],
                                multi=True,
                                placeholder="Ответственный...",
                                className='filter-dropdown',
                                style=st.DROPDOWN_STYLE,
                            ), width=3, xs=12, md=3
                        ),
                    ])
                ])
            ], className='filters-row'), #, className="mb-4 shadow-sm"),

            # 3. Графики
            dbc.Row([
                # Линейный график (отделы)
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Суммы по отделам"), #className="font-weight-bold bg-light"),
                        dbc.CardBody(dcc.Graph(id="dept-line-chart")),
            ]), #className="h-100 shadow-sm"),
                    width=6, xs=12, md=6, className="mb-4"
                ),
                
                # Столбчатая диаграмма (заказчики)
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Суммы по заказчикам"), #className="font-weight-bold bg-light"),
                        dbc.CardBody(dcc.Graph(id="customer-bar-chart"))
                    ]), #className="h-100 shadow-sm"),
                    width=6, xs=12, md=6, className="mb-4"
                ),
            ]),

            dbc.Row([
                # Круговая диаграмма (ответственные)
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Распределение по ответственным"), #className="font-weight-bold bg-light"),
                        dbc.CardBody(dcc.Graph(id="responsible-pie-chart"))
                    ]), #className="h-100 shadow-sm"),
                    width=6, xs=12, md=6, className="dash_graph" #"mb-4"
                ),
                
                # Статистика
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Статистика"), #className="font-weight-bold bg-light"),
                        dbc.CardBody(html.Div(id="stats-container"))
                    ]), #, className="h-100 shadow-sm"),
                    width=6, xs=12, md=6, className="mb-4" #"stats-panel" 
                    #"mb-4"
                ),
            ])
        ],
        fluid=True,
        #style={"maxWidth": "1400px"}
    )
