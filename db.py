# db.py
import sqlite3

def conectar_banco():
    return sqlite3.connect('database.db')

def validar_usuario(email, senha):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM clientes WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    
    if usuario and usuario[3] == senha:
        conexao.close()
        return usuario
    else:
        conexao.close()
        return None
