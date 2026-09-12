import psycopg2 as pg
from psycopg2 import Error
from dotenv import load_dotenv
import os

load_dotenv()
senha = os.getenv("SENHA_BANCO_DE_DADOS")

def conectar():
    try:
        conect = pg.connect(
            user = "postgres",
            password = senha,
            host = "127.0.0.1",
            port = "5432",
            database = "memoriaAI"

        )
        return conect
    except Error as e:
        print(f"Ocorreu um erro ao se conectar ao banco de dados: {e}")

def encerrar_conexao(conect):
    if conect:
        conect.close()
