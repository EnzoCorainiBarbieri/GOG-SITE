from flask import Flask, render_template, jsonify
import requests
from flask_cors import CORS
import mysql.connector
import random

app = Flask(__name__)
CORS(app)

# Função para obter a conexão com o banco de dados MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="loja_de_jogos"
    )

# Página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Página da loja
@app.route('/loja')
def loja():
    jogos = get_jogos_da_api()  
    return render_template('loja.html', jogos=jogos)

def get_jogos_da_api():
    url = "https://api.rawg.io/api/games"
    params = {
        'key': 'e9a7d9e5b4664ac0b222673884e1a112',
        'page_size': 245,
        'ordering': '-rating'
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        jogos = data['results']

        # Adicionar preços aleatórios aos jogos
        for jogo in jogos:
            jogo['preco'] = round(random.uniform(10.0, 200.0), 2)  # Gera um preço entre R$ 10,00 e R$ 200,00

        return jogos  # Retorna a lista de jogos com preços
    else:
        print(f"Erro ao buscar jogos: {response.status_code}")
        return []  # Retorna uma lista vazia em caso de erro
    
# Página sobre
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# Página comunidade
@app.route('/comunidade')
def comunidade():
    return render_template('comunidade.html')

# Página de suporte
@app.route('/suporte')
def suporte():
    return render_template('suporte.html')

# Rota para buscar os jogos da API da RAWG
@app.route('/games')
def get_games():
    url = "https://api.rawg.io/api/games"
    params = {
        'key': 'e9a7d9e5b4664ac0b222673884e1a112',
        'page_size': 10,  # Número de jogos a serem retornados
        'ordering': '-rating'  # Ordenar por popularidade ou avaliação
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data['results'])  # RAWG retorna os jogos em 'results'
    else:
        return jsonify({'error': 'Erro ao buscar jogos'}), response.status_code

# Função para atualizar os jogos no banco de dados
def atualizar_jogos():
    url = "https://api.rawg.io/api/games"
    params = {
        'key': 'e9a7d9e5b4664ac0b222673884e1a112',
        'page_size': 10,
        'ordering': '-rating'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        jogos = data.get('results', [])  # Use um valor padrão vazio se 'results' não existir

        connection = get_db_connection()
        cursor = connection.cursor()

        for jogo in jogos:
            # Extrair informações do jogo
            nome = jogo.get('name', 'Nome não disponível')
            descricao = jogo.get('description_raw', 'Descrição não disponível')  # Usar 'description_raw' para descrição
            preco = 0.00  # RAWG não fornece preços, ajuste conforme necessário
            data_lancamento = jogo.get('released', None)
            categoria = ', '.join([genre['name'] for genre in jogo.get('genres', [])])  # Lista de gêneros
            imagem = jogo.get('background_image', 'imagem_padrao.jpg')  # Usar a imagem de fundo

            # Inserir ou atualizar jogo no banco de dados
            cursor.execute('''
                INSERT INTO jogos (nome, descricao, preco, data_lancamento, categoria, imagem)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    descricao = VALUES(descricao), 
                    preco = VALUES(preco), 
                    data_lancamento = VALUES(data_lancamento), 
                    categoria = VALUES(categoria), 
                    imagem = VALUES(imagem)
            ''', (nome, descricao, preco, data_lancamento, categoria, imagem))

        connection.commit()
        cursor.close()
        connection.close()
    else:
        print(f"Erro ao buscar dados da API: {response.status_code}")

if __name__ == '__main__':
    app.run(debug=True)
