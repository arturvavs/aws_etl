# %%
from Classes.OracleDatabase import ORACLE_DB, save_to_parquet
from Queries.Queries import MOVIMENTO_ESTOQUE, MOVIMENTO_ESTOQUE_DAILY
from datetime import date, datetime, timedelta, time



def extract_data():
    today = date.today()
    yesterday = today - timedelta(days=1)
    string=f"{yesterday.day}_{yesterday.month:02}_{yesterday.year}"
    try:
        batches = ORACLE_DB.fetch_batches(sql=MOVIMENTO_ESTOQUE_DAILY, chunk_size=10000)
        save_to_parquet(batches, f'MOVIMENTO_ESTOQUE_DAILY_{string}')
    except Exception as err:
        print(str(err))
    finally:
        ORACLE_DB.disconnect()
# %%
extract_data()