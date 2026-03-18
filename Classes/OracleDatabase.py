import os
import oracledb as odb
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import time

load_dotenv()

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class OracleDatabase:
    def __init__(self):
        self.user = os.environ["USER_DB"]
        self.password = os.environ["PASSWORD_DB"]
        self.host = os.environ["HOST_DB"]
        self.port = os.environ["PORT_DB"]
        self.service_name = os.environ["SERVICE_NAME_DB"]
        self.connection = None

    def connect(self):
        try:
            self.connection = odb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                service_name=self.service_name,
            )
            logger.info("Conexão estabelecida com sucesso")
        except odb.Error as e:
            logger.error(f"Erro ao conectar: {e}")
            raise

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Conexão fechada")

    @contextmanager
    def get_cursor(self):
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def fetch_dataframe(self, sql: str, **params) -> pd.DataFrame:
        """Executa uma query e retorna um DataFrame."""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)

    def fetch_batches(self, sql: str, chunk_size: int):
        """Gerador que yields batches Arrow a partir de uma query."""
        if not self.connection:
            self.connect()
        for batch in self.connection.fetch_df_batches(statement=sql, size=chunk_size):
            yield pa.Table.from_arrays(
                arrays=batch.column_arrays(),
                names=batch.column_names(),
            )


    def save_to_parquet(self, sql, chunk_size, file_name: str) -> str:
        """Recebe um gerador de batches Arrow e salva como Parquet na pasta Output."""
        batches = self.fetch_batches(sql, chunk_size)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # sobe para a raiz
        output_dir = os.path.join(base_dir, "Output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{file_name}.parquet")

        start = time.perf_counter()
        writer = None
        total_rows = 0
        batch_count = 0

        try:
            for table in batches:
                if writer is None:
                    writer = pq.ParquetWriter(output_path, table.schema)
                writer.write_table(table)
                total_rows += table.num_rows
                batch_count += 1
        finally:
            if writer:
                writer.close()

        elapsed = time.perf_counter() - start
        logger.info(f"Batches: {batch_count} | Linhas: {total_rows} | Tempo: {elapsed:.2f}s | Tabela: {file_name}")
        return output_path


# --- Uso ---
ORACLE_DB = OracleDatabase()