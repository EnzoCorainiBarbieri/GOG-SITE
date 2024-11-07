from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

cache = {}
appids = [
     570, 730, 440, 578080, 292030, 271590, 578080, 1174180, 582010, 1091500, 
    105600, 292030, 49520, 271590, 1174180, 611500, 346110, 381210, 252490, 
    8930, 578080, 271590, 239140, 620, 500, 570, 440, 550, 730, 
    242760, 239140, 400, 8930, 105600, 8930, 4000, 221100, 457140, 282070,
    381210, 4000, 251570, 282070, 431240, 480, 221380, 216890, 107410, 814380
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
            price_str = game_data['price_overview']['final_formatted'] if 'price_overview' in game_data else 'Gratuito'
            if price_str != 'Gratuito':
                price = float(price_str.replace('$', '').replace(',', ''))
            else:
                price = 0.0
            
            game_info = {
                'name': game_data['name'],
                'price': price,  # Usar o valor convertido
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

    if usuario and check_password_hash(usuario[3], senha):
        return usuario
    else:
        return None
    
def get_game_details(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    response = requests.get(url)
    data = response.json()
    
    if data[str(appid)]['success']:
        game_data = data[str(appid)]['data']
        return {
            'name': game_data['name'],
            'description': game_data.get('short_description', 'Descrição não disponível'),
            'price': game_data['price_overview']['final_formatted'] if 'price_overview' in game_data else 'Preço não disponível',
            'image': game_data['header_image'] if 'header_image' in game_data else None
        }
    else:
        return None
    
@app.route('/game_details/<appid>')
def game_details(appid):
    game_info = get_game_details(appid)
    if game_info:
        return render_template('game_details.html', game=game_info)
    else:
        return render_template('error.html', message="Não foi possível carregar as informações do jogo.")

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

def get_meus_jogos(user_id):
    # Conectar ao banco de dados
    conn = sqlite3.connect('sua_base_de_dados.db')
    cursor = conn.cursor()

    # Consultar os jogos adquiridos pelo usuário
    cursor.execute('''
        SELECT jogos.nome, jogos.preco, jogos_usuario.data_compra
        FROM jogos
        JOIN jogos_usuario ON jogos.id = jogos_usuario.jogo_id
        WHERE jogos_usuario.usuario_id = ?
    ''', (user_id,))
    
    jogos_comprados = cursor.fetchall()
    conn.close()

    return jogos_comprados


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
        return redirect('/login')
    
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT jogos.nome, jogos.preco, carrinho.quantidade
                      FROM jogos
                      JOIN carrinho ON jogos.id = carrinho.jogo_id
                      WHERE carrinho.cliente_id = ?''', (user_id,))
    cart_items = cursor.fetchall()
    
    total_price = sum(float(item[1]) * item[2] for item in cart_items)  # Calcular o total do carrinho
    
    conn.close()

    return render_template('cart.html', cart_items=cart_items, total=total_price)

@app.route('/add_to_cart/<int:appid>', methods=['POST'])
def add_to_cart(appid):
    if 'user_id' not in session:
        return jsonify({'message': 'Você precisa estar logado para adicionar ao carrinho.'}), 400

    user_id = session['user_id']
    
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
        cursor.execute('''UPDATE carrinho SET quantidade = quantidade + 1 WHERE cliente_id = ? AND jogo_id = ?''', (user_id, jogo_id))
    else:
        cursor.execute('''INSERT INTO carrinho (cliente_id, jogo_id, quantidade) VALUES (?, ?, ?)''', (user_id, jogo_id, 1))

    conn.commit()
    conn.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM carrinho WHERE cliente_id = ?''', (user_id,))
    cart_count = cursor.fetchone()[0]
    conn.close()

    return jsonify({'message': 'Jogo adicionado ao carrinho!', 'cart_count': cart_count})

@app.route('/remove_from_cart/<appid>', methods=['POST'])
def remove_from_cart(appid):
    if 'user_id' not in session:
        return jsonify({'message': 'Você precisa estar logado para remover do carrinho.'}), 400

    user_id = session['user_id']
    
    # Obter o id do jogo pelo appid
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT id FROM jogos WHERE appid = ?''', (appid,))
    jogo = cursor.fetchone()
    
    if not jogo:
        return jsonify({'message': 'Jogo não encontrado.'}), 404
    
    jogo_id = jogo[0]
    
    # Remover o item do carrinho
    cursor.execute('''DELETE FROM carrinho WHERE cliente_id = ? AND jogo_id = ?''', (user_id, jogo_id))
    conn.commit()

    # Obter os itens restantes no carrinho
    cursor.execute('''SELECT jogos.nome, jogos.preco, carrinho.quantidade
                      FROM jogos
                      JOIN carrinho ON jogos.id = carrinho.jogo_id
                      WHERE carrinho.cliente_id = ?''', (user_id,))
    cart_items = cursor.fetchall()

    total_price = sum(float(item[1]) * item[2] for item in cart_items)  # Calcular o total atualizado

    conn.close()

    return jsonify({'message': 'Produto removido com sucesso!', 'total': total_price, 'cart_items': cart_items})

@app.route('/update_cart/<appid>', methods=['POST'])
def update_cart(appid):
    if 'user_id' not in session:
        return jsonify({'message': 'Você precisa estar logado para atualizar o carrinho.'}), 400
    
    user_id = session['user_id']
    new_quantity = int(request.form['quantity'])
    
    # Obter o id do jogo
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT id FROM jogos WHERE appid = ?''', (appid,))
    jogo = cursor.fetchone()

    if not jogo:
        return jsonify({'message': 'Jogo não encontrado.'}), 404
    
    jogo_id = jogo[0]
    
    # Atualizar a quantidade no carrinho
    cursor.execute('''UPDATE carrinho SET quantidade = ? WHERE cliente_id = ? AND jogo_id = ?''', (new_quantity, user_id, jogo_id))
    conn.commit()

    # Obter os itens do carrinho para retornar os dados atualizados
    cursor.execute('''SELECT jogos.nome, jogos.preco, carrinho.quantidade
                      FROM jogos
                      JOIN carrinho ON jogos.id = carrinho.jogo_id
                      WHERE carrinho.cliente_id = ?''', (user_id,))
    cart_items = cursor.fetchall()

    total_price = sum(float(item[1]) * item[2] for item in cart_items)  # Calcular o total atualizado

    conn.close()

    return jsonify({'message': 'Quantidade atualizada com sucesso!', 'total': total_price, 'cart_items': cart_items})

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    cliente_id = session.get('cliente_id')  # Obtendo o cliente logado
    if not cliente_id:
        return "Você precisa estar logado para finalizar a compra."

    # Acessa o carrinho do usuário
    conexao = sqlite3.connect('database.db')
    cursor = conexao.cursor()

    # Primeiro, obtém todos os jogos no carrinho do cliente
    cursor.execute('''
        SELECT jogo_id, quantidade FROM carrinho WHERE cliente_id = ?
    ''', (cliente_id,))
    jogos_no_carrinho = cursor.fetchall()

    if not jogos_no_carrinho:
        return "O carrinho está vazio."

    # Adiciona os jogos à tabela 'jogos_usuario'
    try:
        for jogo_id, quantidade in jogos_no_carrinho:
            cursor.execute('''
                INSERT INTO jogos_usuario (cliente_id, jogo_id, data_compra)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (cliente_id, jogo_id))

            # Atualiza o estoque no carrinho (se necessário)
            cursor.execute('''
                UPDATE carrinho
                SET quantidade = quantidade - ?
                WHERE cliente_id = ? AND jogo_id = ?
            ''', (quantidade, cliente_id, jogo_id))

        # Remove os itens do carrinho após a compra
        cursor.execute('DELETE FROM carrinho WHERE cliente_id = ?', (cliente_id,))
        conexao.commit()

        return "Compra finalizada com sucesso!"
    except Exception as e:
        print(f"Erro ao finalizar a compra: {e}")
        conexao.rollback()
        return "Erro ao finalizar a compra. Tente novamente."

    finally:
        conexao.close()

@app.route('/support')
def suporte():
    return render_template('support.html')

@app.route('/reset_cart')
def reset_cart():
    if 'user_id' not in session:
        return redirect('/login')  

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Remove todos os itens do carrinho para o usuário atual
    cursor.execute('DELETE FROM carrinho WHERE cliente_id = ?', (user_id,))
    conn.commit()
    conn.close()

    return redirect('/cart')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)