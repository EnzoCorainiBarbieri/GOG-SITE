from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

cache = {}
appids = [
    # Lista dos appids fornecida
]

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS jogos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appid INTEGER UNIQUE NOT NULL,
        nome VARCHAR(255) NOT NULL,
        preco DECIMAL(5,2),
        imagem_url TEXT,
        descricao TEXT,
        categorias TEXT
    );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        endereco TEXT,
        telefone VARCHAR(15)
    );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS carrinho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        jogo_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(jogo_id) REFERENCES jogos(id)
    );''')

    conn.commit()
    conn.close()

def salvar_jogo_no_bd(jogo):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT OR IGNORE INTO jogos (appid, nome, preco, imagem_url, descricao, categorias)
                      VALUES (?, ?, ?, ?, ?, ?)''', (
        jogo['appid'],
        jogo['name'],
        jogo['price'],
        jogo['image'],
        jogo['description'],
        ', '.join(jogo['categories'])
    ))

    conn.commit()
    conn.close()

def get_steam_game_data(appid):
    if appid in cache:
        return cache[appid]

    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data[str(appid)]['success']:
            game_data = data[str(appid)]['data']
            game_info = {
                'name': game_data['name'],
                'price': game_data['price_overview']['final_formatted'] if 'price_overview' in game_data else 'Gratuito',
                'image': game_data['header_image'],
                'description': game_data['short_description'],
                'categories': [cat['description'] for cat in game_data.get('categories', [])],
                'appid': appid
            }
            cache[appid] = game_info
            salvar_jogo_no_bd(game_info)
            return game_info
    return None

def populate_games():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jogos")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        for appid in appids:
            get_steam_game_data(appid)

@app.route('/', methods=['GET', 'POST'])
def home():
    populate_games()
    search_query = request.args.get('search_query', '').lower()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if search_query:
        cursor.execute('SELECT * FROM jogos WHERE LOWER(nome) LIKE ?', (f'%{search_query}%',))
    else:
        cursor.execute('SELECT * FROM jogos')

    jogos = cursor.fetchall()
    conn.close()

    return render_template('index.html', jogos=jogos)

def validar_usuario(email, senha):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    conn.close()

    if usuario and check_password_hash(usuario[3], senha):  # usuario[3] é a senha armazenada
        return usuario
    else:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        # Validar o usuário
        usuario = validar_usuario(email, senha)

        if usuario:
            # Armazenar os dados do usuário na sessão
            session['user_id'] = usuario[0]  # id do usuário
            session['user_name'] = usuario[1]  # nome do usuário
            session['user_email'] = usuario[2]  # email do usuário
            return redirect('/usuario')  # Redireciona para a página de perfil do usuário
        else:
            return 'Usuário ou senha inválidos'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Limpar a sessão
    return redirect('/login')  # Redirecionar para a página de login

@app.route('/usuario')
def usuario():
    if 'user_id' not in session:
        return redirect('/login')  # Se não estiver logado, redireciona para o login

    user_id = session['user_id']

    # Consultar as informações do cliente
    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, email FROM clientes WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()  # Obtém nome e email do usuário

    # Consultar os jogos que o cliente tem no carrinho
    cursor.execute('''SELECT jogos.nome, jogos.preco, carrinho.quantidade
                    FROM jogos
                    JOIN carrinho ON jogos.id = carrinho.jogo_id
                    WHERE carrinho.cliente_id = ?''', (user_id,))
    jogos_comprados = cursor.fetchall()  # Lista de jogos comprados/adicionados ao carrinho

    conexao.close()

    return render_template('usuario.html', usuario=usuario, jogos_comprados=jogos_comprados)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        endereco = request.form['endereco']
        telefone = request.form['telefone']

        hashed_senha = generate_password_hash(senha)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM clientes WHERE email = ?', (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            conn.close()
            return render_template('cadastro.html', error='Email já cadastrado.')

        try:
            cursor.execute('''INSERT INTO clientes (nome, email, senha, endereco, telefone)
                              VALUES (?, ?, ?, ?, ?)''', (nome, email, hashed_senha, endereco, telefone))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('cadastro.html', error='Erro ao cadastrar o cliente.')
        finally:
            conn.close()

    return render_template('cadastro.html')

@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return redirect('/login')  # Se o usuário não estiver logado, redireciona para o login

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Consulta os jogos no carrinho do usuário
    cursor.execute('''SELECT jogos.nome, jogos.preco, carrinho.quantidade
                      FROM jogos
                      JOIN carrinho ON jogos.id = carrinho.jogo_id
                      WHERE carrinho.cliente_id = ?''', (user_id,))
    cart_items = cursor.fetchall()
    conn.close()

    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart/<int:appid>', methods=['POST'])
def add_to_cart(appid):
    if 'user_id' not in session:
        return jsonify({'message': 'Você precisa estar logado para adicionar ao carrinho.'}), 400

    user_id = session['user_id']
    
    # Verificar se o jogo já está no carrinho
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT id FROM jogos WHERE appid = ?''', (appid,))
    jogo = cursor.fetchone()

    if not jogo:
        return jsonify({'message': 'Jogo não encontrado.'}), 404

    jogo_id = jogo[0]

    cursor.execute('''SELECT id FROM carrinho WHERE cliente_id = ? AND jogo_id = ?''', (user_id, jogo_id))
    existing_item = cursor.fetchone()

    if existing_item:
        # Se o jogo já estiver no carrinho, apenas aumenta a quantidade
        cursor.execute('''UPDATE carrinho SET quantidade = quantidade + 1 WHERE cliente_id = ? AND jogo_id = ?''', (user_id, jogo_id))
    else:
        # Caso contrário, adiciona o jogo ao carrinho
        cursor.execute('''INSERT INTO carrinho (cliente_id, jogo_id, quantidade) VALUES (?, ?, ?)''', (user_id, jogo_id, 1))

    conn.commit()
    conn.close()

    # Contar a quantidade de itens no carrinho
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM carrinho WHERE cliente_id = ?''', (user_id,))
    cart_count = cursor.fetchone()[0]
    conn.close()

    return jsonify({'message': 'Jogo adicionado ao carrinho!', 'cart_count': cart_count})

@app.route('/support')
def suporte():
    return render_template('support.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)