import boto3
import os
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()

AWS_KEY = os.getenv("AWS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

class Sender:
    def __init__(self, bucket_name, bucket_folder):
        self.bucket_name = bucket_name
        self.bucket_folder = bucket_folder

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name="us-east-1"
        )

    def process_file(self, filename):
        file = os.path.basename(filename)
        bucket_path = f"{self.bucket_folder}/{file}"
        try:
            self.s3_client.upload_file(
                filename,
                self.bucket_name,
                bucket_path
            )
        except Exception as err:
            print(str(err))
            return False
        
        os.remove(filename)
        return True
    
    def process_folder(self, folder, filename):
        files = [i for i in os.listdir(folder) if i == f"{filename}.parquet"]

        for f in tqdm(files):
            self.process_file(os.path.join(folder,f))
