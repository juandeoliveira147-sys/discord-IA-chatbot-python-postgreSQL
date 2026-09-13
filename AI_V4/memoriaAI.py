import psycopg2 as pg
from psycopg2 import Error
from dotenv import load_dotenv
import os

load_dotenv()
senha = os.getenv("SENHA_BANCO_DE_DADOS")
user_BD = os.getenv("userBD")
hostBD = os.getenv("hostBD")
databaseBD = os.getenv("databaseBD")

def conectar():
    try:
        conect = pg.connect(
            user = user_BD,
            password = senha,
            host = hostBD,
            port = "5432",
            database = databaseBD

        )
        return conect
    except Error as e:
        print(f"Ocorreu um erro ao se conectar ao banco de dados: {e}")
        raise e

def encerrar_conexao(conect):
    if conect:
        conect.close()
