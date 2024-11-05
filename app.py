from flask import Flask, render_template, request, jsonify, session, redirect 
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

cache = {}  # Inicializando o cache

appids = [
    570, 730, 440, 578080, 292030, 271590, 578080, 1174180, 582010, 1091500, 
    105600, 292030, 49520, 271590, 1174180, 611500, 346110, 381210, 252490, 
    8930, 578080, 271590, 239140, 620, 500, 570, 440, 550, 730, 
    242760, 239140, 400, 8930, 105600, 8930, 4000, 221100, 457140, 282070,
    381210, 4000, 251570, 282070, 431240, 480, 221380, 216890, 107410, 814380
]

# Inicializar banco de dados SQLite e criar tabelas
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS jogos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appid INTEGER UNIQUE NOT NULL,
        nome VARCHAR(255) NOT NULL,
        preco VARCHAR(50),
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
    
    conn.commit()
    conn.close()

# Função para inserir um jogo na tabela se ainda não existir
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

# Função para obter dados do jogo via API
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

# Função para popular o banco de dados com jogos
def populate_games():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jogos")
    count = cursor.fetchone()[0]
    conn.close()
    
    # Apenas popular se não houver jogos no banco de dados
    if count == 0:
        for appid in appids:
            get_steam_game_data(appid)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Chamar populate_games para garantir que o BD está atualizado
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
    
    # Debugging: Quantidade de jogos encontrados
    print(f'Total de jogos encontrados: {len(jogos)}')
    
    return render_template('index.html', jogos=jogos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes WHERE email = ?', (email,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario and check_password_hash(usuario[3], senha):  # Verifique a senha
            session['usuario_id'] = usuario[0]  # Armazena o ID do usuário na sessão
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Email ou senha incorretos.')

    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        endereco = request.form['endereco']
        telefone = request.form['telefone']

        hashed_senha = generate_password_hash(senha)  # Gera um hash para a senha

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Debugging: Verificar se o email já está no banco
        cursor.execute('SELECT * FROM clientes WHERE email = ?', (email,))
        usuario_existente = cursor.fetchone()
        print(f'Email verificado: {email}, Usuario encontrado: {usuario_existente}')  # Adiciona esta linha para verificar o resultado

        if usuario_existente:
            conn.close()
            return render_template('cadastro.html', error='Email já cadastrado.')

        # Tente inserir o novo cliente no banco de dados
        try:
            cursor.execute('''INSERT INTO clientes (nome, email, senha, endereco, telefone)
                              VALUES (?, ?, ?, ?, ?)''', (nome, email, hashed_senha, endereco, telefone))
            conn.commit()  # Certifique-se de que os dados sejam salvos
            print(f'Usuário {nome} cadastrado com sucesso')  # Adiciona uma mensagem de sucesso para verificação
            return redirect(url_for('login'))  # Redireciona para a página de login após o cadastro
        except sqlite3.IntegrityError as e:
            print(f'Erro ao cadastrar: {e}')  # Exibe o erro em caso de falha
            return render_template('cadastro.html', error='Erro ao cadastrar o cliente.')
        finally:
            conn.close()

    return render_template('cadastro.html')

@app.route('/add_to_cart/<int:appid>', methods=['POST'])
def add_to_cart(appid):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jogos WHERE appid = ?', (appid,))
    jogo = cursor.fetchone()
    
    if jogo:  # Verifica se o jogo foi encontrado
        cart = session.get('cart', [])
        
        # Adiciona o jogo ao carrinho, se não estiver lá
        if not any(item[0] == jogo[0] for item in cart):  # Verifique com base no appid
            cart.append((jogo[0], jogo[1], jogo[2]))  # Adiciona appid, nome e preço
            session['cart'] = cart
        
        return jsonify({'message': 'Adicionado ao carrinho', 'cart_count': len(session['cart'])})
    else:
        return jsonify({'message': 'Jogo não encontrado', 'cart_count': len(session.get('cart', []))})




@app.route('/remove_from_cart/<int:appid>', methods=['POST'])
def remove_from_cart(appid):
    cart = session.get('cart', [])
    cart = [item for item in cart if item[0] != appid]  # Remove o jogo pelo appid
    session['cart'] = cart
    return jsonify({'message': 'Jogo removido do carrinho', 'cart_count': len(session['cart'])})

@app.route('/update_cart/<int:appid>', methods=['POST'])
def update_cart(appid):
    quantity = request.form.get('quantity', type=int)
    if quantity is None or quantity < 1:
        return jsonify({'message': 'Quantidade inválida'})

    cart = session.get('cart', [])
    for item in cart:
        if item[0] == appid:
            # Aqui você pode querer atualizar a quantidade no carrinho, se você mantiver uma estrutura com quantidade
            # Por exemplo, se cada item for uma tupla (appid, nome, preco, quantidade):
            # item[3] = quantity  # Se a estrutura suportar quantidade
            break
    session['cart'] = cart
    return jsonify({'message': 'Quantidade atualizada', 'cart_count': len(session['cart'])})

@app.route('/cart')
def view_cart():
    return render_template('cart.html', cart=session.get('cart', []))

if __name__ == '__main__':
    init_db()  # Inicializa o banco de dados ao iniciar o aplicativo
    app.run(debug=True)
