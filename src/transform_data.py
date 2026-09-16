import pandas as pd
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'
columns_names_to_drop = ['weather', 'weather_icon', 'sys.type']
columns_name = {
        'base' : 'base',
        'visibility' : 'visibility',
        'dt': 'datetime',
        'timezone': 'timezone',
        'id': 'city_id',
        'name': 'city_name',
        'cod': 'code',
        'coord.lon': 'longitude',
        'coord.lat': 'latitude',
        'main.temp': 'temperature',
        'main.feels_like': 'feels_like',
        'main.temp_min': 'temp_min',
        'main.temp_max': 'temp_max',
        'main.pressure': 'pressure',
        'main.humidity': 'humidity',
        'main.sea_level': 'sea_level',
        'main.grnd_level': 'ground_level',
        'wind.speed': 'wind_speed',
        'wind.deg': 'wind_degree',
        'wind.gust': 'wind_gust',
        'rain.1h': 'rain_1h',
        'clouds.all': 'clouds_all',
        'sys.type': 'sys_type',
        'sys.id': 'sys_id',
        'sys.country': 'country',
        'sys.sunrise': 'sunrise',
        'sys.sunset': 'sunset'
    }
columns_to_normalize_datetime = ['datetime', 'sunrise', 'sunset']

# Criação de funções para transformar os dados extraídos da API (json) em um DataFrame do Pandas
def create_dataframe(path_name:str) -> pd.DataFrame:
    path = path_name

    if not path.exists():
        logging.error(f'Arquivo não encontrado: {path}')
    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logging.info(f'Dataframe criado com sucesso com {len(df)} linhas e {len(df.columns)} colunas.')
    return df
# Normatização das colunas do DataFrame
def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))
    df_weather = df_weather.rename(columns={
            'id': 'weather_id',
            'main': 'weather_main',
            'description': 'weather_description',
            'icon': 'weather_icon'
    })

    df = pd.concat([df, df_weather], axis=1)
    logging.info(f'Coluna Weather normalizada com sucesso. Novo dataframe com {len(df)} linhas e {len(df.columns)} colunas.')
    return df

# Remoção de colunas desnecessárias do DataFrame
def drop_columns(df: pd.DataFrame, columns_name: list[str]) -> pd.DataFrame:
    logging.info(f'Removendo colunas: {columns_name}')
    df = df.drop(columns=columns_name)
    logging.info(f'Colunas removidas com sucesso. Colunas restantes: ({len(df.columns)})')
    return df

#função para renomear as colunas do DataFrame
def rename_columns(df: pd.DataFrame, columns_name: dict[str, str]) -> pd.DataFrame:
    logging.info(f'Renomeando {len(columns_name)} colunas do DataFrame.')
    df = df.rename(columns=columns_name)
    logging.info('colunas renomeadas com sucesso.')
    return df

def normalize_datetime_columns(df: pd.DataFrame, columns_name: list[str]) -> pd.DataFrame:

    logging.info(f'Normalizando {len(columns_name)} colunas de data e hora do DataFrame.')
    for name in columns_name:
        df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')
    logging.info('Colunas de data e hora normalizadas com sucesso.')
    return df

def data_transformation():
    print('Iniciando transformação dos dados...')
    df = create_dataframe(path_name)
    df = normalize_weather_columns(df)
    df = drop_columns(df, columns_names_to_drop)
    df = rename_columns(df, columns_name)
    df = normalize_datetime_columns(df, columns_to_normalize_datetime)
    logging.info(f'Transformação dos dados concluida com sucesso. Dataframe final com {len(df)} linhas e {len(df.columns)} colunas.')
    return df