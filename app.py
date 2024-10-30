from flask import Flask, render_template, request, jsonify, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

appids = [
    570, 730, 440, 578080, 292030, 271590, 578080, 1174180, 582010, 1091500, 
    105600, 292030, 49520, 271590, 1174180, 611500, 346110, 381210, 252490, 
    8930, 578080, 271590, 239140, 620, 500, 570, 440, 550, 730, 
    242760, 239140, 400, 8930, 105600, 8930, 4000, 221100, 457140, 282070,
    381210, 4000, 251570, 282070, 431240, 480, 221380, 216890, 107410, 814380
]

cache = {}
cart = []

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
            return game_info
    return None

@app.route('/', methods=['GET', 'POST'])
def home():
    search_query = request.args.get('search_query', '').lower()
    games = []

    for appid in appids:
        game = get_steam_game_data(appid)
        if game:
            games.append(game)

    if search_query:
        games = [game for game in games if search_query in game['name'].lower()]

    return render_template('index.html', games=games)

@app.route('/add_to_cart/<int:appid>', methods=['POST'])
def add_to_cart(appid):
    game = get_steam_game_data(appid)
    if game:
        cart.append(game)
        session['cart'] = cart
    return jsonify({'message': 'Adicionado ao carrinho', 'cart_count': len(cart)})

@app.route('/cart')
def view_cart():
    return render_template('cart.html', cart=session.get('cart', []))

if __name__ == '__main__':
    app.run(debug=True)
