from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lista global temporal para guardar los productos del carrito
cart_items = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/d-day')
def dday_detail():
    return render_template('d-day.html')

# Ruta para tu nuevo producto (puedes agregar más siguiendo esta misma estructura)
@app.route('/island')
def island_detail():
    return render_template('island.html') # Asegúrate de que tu archivo HTML nuevo se llame así o cámbiale el nombre aquí


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    name = request.form.get('product_name')
    price = request.form.get('product_price')
    image = request.form.get('product_image')

    cart_items.append({'name': name, 'price': price, 'image': image})
    return redirect(request.referrer or url_for('view_cart'))
    
    # Agrega el producto seleccionado a la lista
    cart_items.append({'name': name, 'price': price})
    
    # Te devuelve exactamente a la página del producto desde donde hiciste la compra
    return redirect(request.referrer or url_for('view_cart'))

@app.route('/remove-from-cart/<int:index>', methods=['POST'])
def remove_from_cart(index):
    if 0 <= index < len(cart_items):
        cart_items.pop(index) # Elimina el producto correcto de la lista
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    total = sum(float(item['price']) for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/proof')
def proof_detail():
    return render_template('proof.html')

if __name__ == '__main__':
    app.run(debug=True)