from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
