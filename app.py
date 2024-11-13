from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
import pytz
import os

brasil_tz = pytz.timezone('America/Sao_Paulo')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta_aqui'
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    compras = db.relationship('Compra', backref='usuario', lazy=True)

class Jogo(db.Model):
    __tablename__ = 'jogos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.DECIMAL(10, 2), nullable=False)
    imagem = db.Column(db.String(255))

class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    jogo_id = db.Column(db.Integer, db.ForeignKey('jogos.id'), nullable=False)
    valor = db.Column(db.DECIMAL(10, 2), nullable=False, default=0.00)
    nome_jogo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.now(brasil_tz)) 
    
    jogo = db.relationship('Jogo', backref='compras', lazy=True)
    
with app.app_context():
    db.create_all()
    
# URL da API da Steam para listar jogos (adicione sua chave da API se necessário)
STEAM_API_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

@app.route('/')
def listar_jogos():
    ids_jogos_steam = [570, 730, 440, 578080, 292030, 271590, 578080, 1174180, 582010, 1091500, 381210, 4000, 251570, 282070, 431240, 480, 221380, 216890, 107410, 814380]
    jogos = []
    carrinho = session.get('carrinho', [])


    termo_pesquisa = request.args.get('search', '').lower()

    for id_jogo in ids_jogos_steam:
        resposta = requests.get(f"https://store.steampowered.com/api/appdetails?appids={id_jogo}&l=portuguese")
        

        if resposta.status_code == 200:
            dados_resposta = resposta.json().get(str(id_jogo), None)
            
 
            if dados_resposta and 'data' in dados_resposta:
                dados_jogo = dados_resposta['data']
                titulo_jogo = dados_jogo.get('name', 'Jogo Desconhecido')
                

                if termo_pesquisa in titulo_jogo.lower() or not termo_pesquisa:
                    jogos.append({
                        'id': id_jogo,
                        'titulo': titulo_jogo,
                        'descricao': dados_jogo.get('short_description', ''),
                        'imagem': dados_jogo.get('header_image', ''),
                        'preco': dados_jogo.get('price_overview', {}).get('final_formatted', 'Grátis'),
                        'no_carrinho': id_jogo in carrinho
                    })

    return render_template('index.html', jogos=jogos)

@app.route('/jogo/<int:jogo_id>')
def detalhes_jogo(jogo_id):
    resposta = requests.get(f"https://store.steampowered.com/api/appdetails?appids={jogo_id}&l=portuguese")
    dados_jogo = resposta.json().get(str(jogo_id), {}).get('data', {})

    if not dados_jogo:
        return "Jogo não encontrado", 404

    jogo = {
        'id': jogo_id,
        'titulo': dados_jogo.get('name', 'Jogo Desconhecido'),
        'descricao': dados_jogo.get('detailed_description', ''),
        'imagem': dados_jogo.get('header_image', ''),
        'preco': dados_jogo.get('price_overview', {}).get('final_formatted', 'Grátis'),
        'desenvolvedor': dados_jogo.get('developers', []),
        'publicador': dados_jogo.get('publishers', []),
        'data_lancamento': dados_jogo.get('release_date', {}).get('date', 'Data não disponível'),
        'genero': [genre['description'] for genre in dados_jogo.get('genres', [])],
        'avaliacoes': dados_jogo.get('metacritic', {}).get('score', 'Sem avaliações')
    }

    return render_template('detalhes_jogo.html', jogo=jogo)

@app.route('/suporte')
def suporte():
    return render_template('suporte.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('listar_jogos'))
        else:
            flash('Credenciais inválidas!', 'danger')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado!', 'danger')
            return redirect(url_for('cadastro'))

        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar o perfil!', 'warning')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    usuario = db.session.get(Usuario, usuario_id)

    if not usuario:
        flash('Usuário não encontrado!', 'warning')
        return redirect(url_for('login'))

    compras = Compra.query.filter_by(usuario_id=usuario.id).all()
    return render_template('perfil.html', usuario=usuario, compras=compras)

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Você saiu com sucesso!', 'info')
    return redirect(url_for('listar_jogos'))

@app.route('/comprar_jogo/<int:jogo_id>', methods=['POST'])
def comprar_jogo(jogo_id):
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para comprar um jogo!', 'warning')
        return redirect(url_for('login'))

    if 'carrinho' not in session:
        session['carrinho'] = []

    if jogo_id not in session['carrinho']:
        session['carrinho'].append(jogo_id)

    flash('Jogo adicionado ao carrinho!', 'success')
    return redirect(url_for('listar_jogos'))

@app.route('/adicionar_ao_carrinho/<int:jogo_id>', methods=['POST'])
def adicionar_ao_carrinho(jogo_id):
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para adicionar um jogo ao carrinho!', 'warning')
        return redirect(url_for('login'))

    if 'carrinho' not in session:
        session['carrinho'] = []

    if jogo_id not in session['carrinho']:
        session['carrinho'].append(jogo_id)

    flash(f'Jogo {jogo_id} adicionado ao carrinho!', 'success')
    return redirect(url_for('listar_jogos'))

@app.route('/carrinho')
def carrinho():
    if 'carrinho' not in session or not session['carrinho']:
        return render_template('carrinho.html', jogos=[])

    jogos_no_carrinho = []
    total = 0.0  
    for jogo_id in session['carrinho']:
        resposta = requests.get(f"https://store.steampowered.com/api/appdetails?appids={jogo_id}&l=portuguese")
        dados_jogo = resposta.json().get(str(jogo_id), {}).get('data', {})
        if dados_jogo:
            jogo = {
                'id': jogo_id,
                'titulo': dados_jogo.get('name', 'Jogo Desconhecido'),
                'descricao': dados_jogo.get('short_description', ''),
                'imagem': dados_jogo.get('header_image', ''),
                'preco': dados_jogo.get('price_overview', {}).get('final_formatted', 'Grátis')
            }
            jogos_no_carrinho.append(jogo)

            
            price_overview = dados_jogo.get('price_overview', {})
            preco_centavos = price_overview.get('final', 0)  
            preco = preco_centavos / 100.0 
            total += preco  
        else:
            jogos_no_carrinho.append({
                'id': jogo_id,
                'titulo': 'Jogo Desconhecido',
                'descricao': '',
                'imagem': '',
                'preco': 'Grátis'
            })

    return render_template('carrinho.html', jogos=jogos_no_carrinho, total=total)

@app.route('/cancelar_compra/<int:compra_id>', methods=['POST'])
def cancelar_compra(compra_id):
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para cancelar uma compra!', 'warning')
        return redirect(url_for('login'))

    compra = Compra.query.get(compra_id)
    if not compra or compra.usuario_id != session['usuario_id']:
        flash('Compra não encontrada ou não pertence a você!', 'danger')
        return redirect(url_for('perfil'))

    db.session.delete(compra)
    db.session.commit()

    flash('Pedido excluído com sucesso!', 'success')
    return redirect(url_for('perfil'))

@app.route('/remover_do_carrinho/<int:jogo_id>', methods=['POST'])
def remover_do_carrinho(jogo_id):
    if 'carrinho' not in session or jogo_id not in session['carrinho']:
        flash('Jogo não encontrado no carrinho!', 'warning')
        return redirect(url_for('carrinho'))

    session['carrinho'].remove(jogo_id)
    flash('Jogo removido do carrinho!', 'success')
    return redirect(url_for('carrinho'))

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para finalizar a compra!', 'warning')
        return redirect(url_for('login'))

    carrinho = session.get('carrinho', [])
    
    if not carrinho:
        flash('Seu carrinho está vazio!', 'warning')
        return redirect(url_for('listar_jogos'))

    usuario_id = session['usuario_id']

    for jogo_id in carrinho:
        resposta = requests.get(f"https://store.steampowered.com/api/appdetails?appids={jogo_id}&l=portuguese")
        dados_jogo = resposta.json().get(str(jogo_id), {}).get('data', {})

        if dados_jogo:
            nome_jogo = dados_jogo.get('name', 'Jogo Desconhecido')
            price_overview = dados_jogo.get('price_overview', {})
            preco = price_overview.get('final', 0) if price_overview else 0

            if preco:
                preco_formatado = float(preco) / 100  
            else:
                preco_formatado = 0.0
        else:
            nome_jogo = 'Jogo Desconhecido'
            preco_formatado = 0.0

        nova_compra = Compra(usuario_id=usuario_id, jogo_id=jogo_id, valor=preco_formatado, nome_jogo=nome_jogo)
        db.session.add(nova_compra)

    db.session.commit()
    session['carrinho'] = []
    
    flash('Compra realizada com sucesso!', 'success')  
    return redirect(url_for('listar_jogos'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

