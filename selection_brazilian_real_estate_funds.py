#Import libraries
import requests
import pandas as pd
import numpy as np

"""Colecting data from https://www.fundsexplorer.com.br/ranking"""

def coletar_FI():
    #Busca no site a tabela de FIs
    url = 'https://www.fundsexplorer.com.br/ranking'
    response = requests.get(url)
    if response.status_code == 200:
        data = pd.read_html(response.content, encoding='utf-8')[0]

    #Ordena de acordo com o código do Fundo A-Z
    data.sort_values('Códigodo fundo', inplace=True)

    # limpeza e formatação de dados
    #print(data.isna().sum())  # Conta qtd de vazios "nan"
    categorical_columns = ['Códigodo fundo', 'Setor']
    for head in categorical_columns:
        index = data[data[head].isna()].index  # acha index que o "head" é "nan"
        data.drop(index, inplace=True)  # deleta dado

    # transformar em categorico
    data[categorical_columns] = data[categorical_columns].astype('category')
    #print(data.info())

    # Colunas float
    col_float = data.iloc[:, 2:-1].columns
    data[col_float] = data[col_float].fillna(value=0)  # subistitui os valores "nan" por 0

    # Subistituindo valores em todo o data frame
    data[col_float] = data[col_float].applymap(lambda x: str(x).replace('R$', '').replace('.0', '').replace('.', '').replace('%', '').replace(',','.'))
    data[col_float] = data[col_float].astype('float')

    index = data[np.isinf(data[col_float]).any(1)].index  # index dos dados que estão marcados como infinito
    data.drop(index, inplace=True)

    # Corrigindo P/VPA
    data['P/VPA'] = data['P/VPA'] / 100

    #Define indicadores
    indicadores = ['Códigodo fundo', 'Setor', 'Liquidez Diária', 'DividendYield','DY (12M)Acumulado', 'DY (12M)Média', 'P/VPA','QuantidadeAtivos']
    data_frame_indicadores = data[indicadores]

    return data_frame_indicadores

def opportunity_FI(data, sector='All'):
    if sector == 'All':
        media = data.agg(['mean', 'std'])
        mediana = data.agg(['median', 'std'])
        data_agrupada = data   

        filter_ = (data_agrupada['Liquidez Diária'] > media['Liquidez Diária'][0]) & \
                  (data_agrupada['DividendYield'] > mediana['DividendYield'][0]) & \
                  (data_agrupada['P/VPA'] < 1) & \
                  (data_agrupada['DY (12M)Média'] > mediana['DY (12M)Média'][0])

    else:
        media = data.groupby('Setor').agg(['mean','std'])
        mediana = data.groupby('Setor').agg(['median', 'std'])
        data_agrupada = data[data['Setor'].isin([sector])]

        filter_ = (data_agrupada['Liquidez Diária'] > media.loc[sector, ('Liquidez Diária', 'mean')]) & \
                  (data_agrupada['DividendYield'] > mediana.loc[sector, ('DividendYield', 'median')]) & \
                  (data_agrupada['P/VPA'] < 1) & \
                  (data_agrupada['QuantidadeAtivos'] >= int(media.loc[sector, ('QuantidadeAtivos', 'mean')])) & \
                  (data_agrupada['DY (12M)Média'] > mediana.loc[sector, ('DY (12M)Média', 'median')])


    return [data_agrupada[filter_], media, mediana]

Setores = ['Shoppings', 'Títulos e Val. Mob.', 'Lajes Corporativas', 'Logística', 'Híbrido', 'Outros','Hospital', 'Residencial', 'Hotel']

df = pd.DataFrame()
tabela_FI = coletar_FI()

for setor in Setores:
    FI, media, mediana = opportunity_FI(tabela_FI, setor)
    if FI.empty:
        pass
    else:
        df = pd.concat([df,FI])

print(df)

df
