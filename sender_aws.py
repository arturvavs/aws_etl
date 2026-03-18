# %%
from Classes.Sender import Sender
from dotenv import load_dotenv
import os
load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")

def sender_files():
    try:
        sender = Sender(bucket_name=BUCKET_NAME, bucket_folder='supply/stock_mov')
        sender.process_folder('Output/')
    except Exception as err:
        print(str(err))

# %%
sender_files()