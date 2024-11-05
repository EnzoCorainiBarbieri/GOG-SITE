import sqlite3

def criar_tabelas():
    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid INTEGER UNIQUE NOT NULL,
            nome VARCHAR(255) NOT NULL,
            preco VARCHAR(50),
            imagem_url TEXT,
            descricao TEXT,
            categorias TEXT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            endereco TEXT,
            telefone VARCHAR(15)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrinho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            jogo_id INTEGER,
            quantidade INTEGER DEFAULT 1,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (jogo_id) REFERENCES jogos(id)
        );
    ''')

    conexao.commit()
    conexao.close()

if __name__ == '__main__':
    criar_tabelas()
    print("Tabelas criadas com sucesso!")
