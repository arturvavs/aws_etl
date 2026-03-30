# %%
from Classes.OracleDatabase import ORACLE_DB
from Classes.Sender import Sender
from Queries.Queries import *
from datetime import date, datetime, timedelta, time
from dotenv import load_dotenv
import os
import argparse
load_dotenv()

def load_sql(file_name: str) -> str:
    path = os.path.join("Queries", file_name)

    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def extract_data(sql, chunk_size, filename, bucket_name, bucket_folder, folder):
    today = date.today()
    string=f"{today.day}_{today.month:02}_{today.year}"
    filename = f"{filename}_{string}"
    sender = Sender(bucket_name, bucket_folder)
    try:
        ORACLE_DB.save_to_parquet(sql, chunk_size, filename)
        sender.process_folder(folder, filename)

    except Exception as err:
        print(err)
    
    finally:
        ORACLE_DB.disconnect()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql_file", type=str)
    parser.add_argument("--filename", type=str)
    parser.add_argument("--chunk_size", type=int, default=10000)
    parser.add_argument("--bucket_name", type=str, default= 'datalake-raw-arturvavs')
    parser.add_argument("--bucket_folder", type=str, default= 'supply/raw/movimento_estoque/2026')
    parser.add_argument("--folder", type=str, default='Output/')

    args = parser.parse_args()


    sql = load_sql(args.sql_file)
    extract_data(sql, args.chunk_size, args.filename, args.bucket_name, args.bucket_folder, args.folder)