import sqlite3

def criar_tabelas():
    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    # Criação da tabela de jogos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid INTEGER UNIQUE NOT NULL,
            nome VARCHAR(255) NOT NULL,
            preco REAL,
            imagem_url TEXT,
            descricao TEXT,
            categorias TEXT
        );
    ''')

    # Criação da tabela de clientes
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

    # Criação da tabela de carrinho
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrinho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            jogo_id INTEGER,
            quantidade INTEGER DEFAULT 1,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (jogo_id) REFERENCES jogos(id) ON DELETE CASCADE
        );
    ''')

    # Criação da tabela de jogos_usuario (associando jogos aos clientes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos_usuario (
            cliente_id INTEGER,
            jogo_id INTEGER,
            data_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (cliente_id, jogo_id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (jogo_id) REFERENCES jogos(id)
        );
    ''')

    # Criando índices para melhorar a performance das consultas
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_cliente_email ON clientes(email);
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_jogo_nome ON jogos(nome);
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_carrinho_cliente_id ON carrinho(cliente_id);
    ''')

    conexao.commit()
    conexao.close()

if __name__ == '__main__':
    criar_tabelas()
    print("Tabelas criadas com sucesso!")
