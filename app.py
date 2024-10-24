from flask import Flask, render_template, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Página da loja
@app.route('/loja')
def loja():
    return render_template('loja.html')

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

# Rota para buscar os jogos da API da GOG
@app.route('/games')
def get_games():
    url = "https://www.gog.com/games/ajax/filtered"
    params = {
        'mediaType': 'game',
        'sortBy': 'popularity'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data['products'])
    else:
        return jsonify({'error': 'Erro ao buscar jogos'}), response.status_code
    
def atualizar_jogos():
    url = "https://www.gog.com/games/ajax/filtered"
    params = {
        'mediaType': 'game',
        'sortBy': 'popularity'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        jogos = data.get('products', [])  # Use um valor padrão vazio se 'products' não existir

        connection = get_db_connection()
        cursor = connection.cursor()

        for jogo in jogos:
            # Extrair informações do jogo
            nome = jogo.get('title', 'Nome não disponível')
            descricao = jogo.get('description', 'Descrição não disponível')
            preco = jogo.get('price', {}).get('amount', 0.00)  # Acesse o valor do dicionário corretamente
            moeda = jogo.get('price', {}).get('currency', 'USD')  # Acesse a moeda corretamente
            data_lancamento = jogo.get('release_date', None)  # Ajuste conforme necessário
            categoria = jogo.get('category', 'Outro')
            imagem = jogo.get('image', 'imagem_padrao.jpg')  # Coloque uma imagem padrão se não houver

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
        {jogo.title}
        connection.commit()
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)


