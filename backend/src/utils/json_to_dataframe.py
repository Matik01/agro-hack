import pandas as pd
import json
import numpy as np


def json_to_dataframe(data: json) -> pd.DataFrame:
    records = []

    for op in data['операции']:
        department = op.get('отделение')
        is_multi = isinstance(department, list)

        if not is_multi:
            record = {
                'дата': op.get('дата'),
                'операция': op.get('операция'),
                'отделение': department,
                'подразделение': op.get('подразделение'),
                'растительная_культура': op.get('растительная_культура'),
                'площадь_за_день': op.get('площадь', {}).get('за_день'),
                'площадь_с_начала': op.get('площадь', {}).get('c_начала_операции'),
                'площадь_по_ПУ_за_день': op.get('площадь_по_ПУ', {}).get('за_день') if op.get(
                    'площадь_по_ПУ') else np.nan,
                'площадь_по_ПУ_с_начала': op.get('площадь_по_ПУ', {}).get('c_начала_операции') if op.get(
                    'площадь_по_ПУ') else np.nan,
                'вал_за_день': op.get('вал', {}).get('за_день') if op.get('вал') else np.nan,
                'вал_с_начала': op.get('вал', {}).get('с_начала') if op.get('вал') else np.nan
            }
            records.append(record)
        else:
            for i in range(len(department)):
                record = {
                    'дата': op.get('дата'),
                    'операция': op.get('операция'),
                    'отделение': department[i],
                    'подразделение': op.get('подразделение'),
                    'растительная_культура': op.get('растительная_культура'),
                    'площадь_за_день': op.get('площадь', {}).get('за_день', [np.nan] * len(department))[i],
                    'площадь_с_начала': op.get('площадь', {}).get('c_начала_операции', [np.nan] * len(department))[i],
                    'площадь_по_ПУ_за_день': op.get('площадь_по_ПУ', {}).get('за_день') if op.get(
                        'площадь_по_ПУ') else np.nan,
                    'площадь_по_ПУ_с_начала': op.get('площадь_по_ПУ', {}).get('c_начала_операции') if op.get(
                        'площадь_по_ПУ') else np.nan,
                    'вал_за_день': op.get('вал', {}).get('за_день') if op.get('вал') else np.nan,
                    'вал_с_начала': op.get('вал', {}).get('с_начала') if op.get('вал') else np.nan
                }
                records.append(record)

    return pd.DataFrame(records)
