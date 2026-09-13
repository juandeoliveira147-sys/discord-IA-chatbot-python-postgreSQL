import psycopg2 as pg
from psycopg2 import Error
from dotenv import load_dotenv
import os

load_dotenv()
"""
caso alguém queira usar futuramente sem estar na nuvem!

senha = os.getenv("SENHA_BANCO_DE_DADOS")
user_BD = os.getenv("userBD")
hostBD = os.getenv("hostBD")
databaseBD = os.getenv("databaseBD")
"""

def conectar():
    try:
        DATABASE_URL = os.getenv("databasesupabase")
        conect = pg.connect(
            DATABASE_URL

        )
        return conect
    except Error as e:
        print(f"Ocorreu um erro ao se conectar ao banco de dados: {e}")
        raise e

def encerrar_conexao(conect):
    if conect:
        conect.close()
