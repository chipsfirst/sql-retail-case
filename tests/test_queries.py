import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
QUERIES = sorted((ROOT / 'sql' / 'queries').glob('*.sql'))

pytestmark = pytest.mark.skipif(
    not os.environ.get('PGHOST'),
    reason='нужен PostgreSQL: задайте PGHOST, PGDATABASE и доступ',
)


@pytest.fixture(scope='module')
def cursor():
    psycopg2 = pytest.importorskip('psycopg2')

    conn = psycopg2.connect()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute((ROOT / 'sql' / 'schema.sql').read_text(encoding='utf-8'))
    for table in ('customers', 'products', 'orders', 'order_items'):
        with open(ROOT / 'tests' / 'fixtures' / f'{table}.csv', encoding='utf-8') as handle:
            cur.copy_expert(f'COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)', handle)
    yield cur
    cur.close()
    conn.close()


def test_view_has_paid_orders(cursor):
    cursor.execute('SELECT COUNT(*) FROM v_paid_order_totals')
    assert cursor.fetchone()[0] == 3


@pytest.mark.parametrize('path', QUERIES, ids=[p.name for p in QUERIES])
def test_query_runs_and_returns_rows(cursor, path):
    cursor.execute(path.read_text(encoding='utf-8'))
    rows = cursor.fetchall()
    assert cursor.description is not None
    assert rows, f'{path.name} вернул пустой результат'
