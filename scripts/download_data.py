"""Скачивание датасета Online Retail II с Kaggle.

Датасет: mashlyn/online-retail-ii-uci, лицензия CC0 1.0 (public domain).
Источник: https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci
Файл: online_retail_II.csv, 1 067 371 строка, декабрь 2009 — декабрь 2011.

Скрипт не требует авторизации: Kaggle отдаёт публичные датасеты по прямой ссылке.
Если ссылка перестанет работать, скачайте архив вручную и положите рядом.
"""

import hashlib
import os
import urllib.request
import zipfile

URL = 'https://www.kaggle.com/api/v1/datasets/download/mashlyn/online-retail-ii-uci'
ZIP_SHA256 = 'e2a0ebc53c3b0b577ff2f3dc4eb64032a38e38f6d7a47f73e511cdcd6d5b7dbd'
CSV_NAME = 'online_retail_II.csv'

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    os.makedirs(DATA, exist_ok=True)
    zip_path = os.path.join(DATA, 'online-retail-ii.zip')
    csv_path = os.path.join(DATA, CSV_NAME)

    if os.path.exists(csv_path):
        print(f'{csv_path} уже есть')
        return

    if not os.path.exists(zip_path):
        print(f'скачиваю {URL}')
        urllib.request.urlretrieve(URL, zip_path)

    actual = sha256(zip_path)
    if actual != ZIP_SHA256:
        raise SystemExit(f'контрольная сумма не совпала: {actual}')

    with zipfile.ZipFile(zip_path) as archive:
        archive.extract(CSV_NAME, DATA)
    print(f'{csv_path}: {os.path.getsize(csv_path) / 1024 / 1024:.0f} МБ')


if __name__ == '__main__':
    main()
