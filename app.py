from flask import Flask, render_template, request, redirect, url_for
from basedatos import comprar, crear_cuenta, iniciar_sesion, alerta   # NUEVO

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Capturamos los datos que el usuario escribió en el formulario
        email = request.form.get('email')
        password = request.form.get('password')

        # NUEVO: revisa el correo y la contraseña en la base de datos
        # NUEVO: y, si son correctos, guarda el ingreso en la tabla "ingresos"
        ok, resultado = iniciar_sesion(email, password)   # NUEVO
        if not ok:                                         # NUEVO
            return alerta(resultado)                       # NUEVO
        
        print(f"Correo recibido: {email}") # Esto saldrá en tu terminal para confirmar
        
        # Por ahora, los redirigimos de regreso a la tienda principal al ingresar
        return redirect(url_for('index'))
        
    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')

        # NUEVO: revisa los datos y crea la cuenta en la base de datos
        ok, mensaje = crear_cuenta(username, email, password, request.form.get('confirm_password'))   # NUEVO
        if not ok:                                                                                     # NUEVO
            return alerta(mensaje)                                                                     # NUEVO
        
        print(f"Nuevo usuario registrado -> Email: {email}, Username: {username}")
        
        # Una vez registrado, lo mandamos al login para que ingrese
        return redirect(url_for('login'))
        
    return render_template('register.html')


# NUEVO: ruta que usan los botones "Buy Now" y "Buy N products" del carrito.
# NUEVO: descuenta del inventario lo comprado y lo saca del carrito.
@app.route('/comprar', methods=['POST'])                                                  # NUEVO
def comprar_carrito():                                                                    # NUEVO
    datos = request.get_json(silent=True) or {}                                           # NUEVO
    items = []                                                                            # NUEVO
    indices = []                                                                          # NUEVO
    for pedido in datos.get('pedidos', []):                                               # NUEVO
        try:                                                                              # NUEVO
            i = int(pedido['indice'])                                                     # NUEVO
            cantidad = int(pedido.get('cantidad', 1))                                     # NUEVO
        except (KeyError, TypeError, ValueError):                                         # NUEVO
            return {'ok': False, 'mensaje': 'Datos inválidos'}, 400                       # NUEVO
        if not 0 <= i < len(cart_items):                                                  # NUEVO
            return {'ok': False, 'mensaje': 'Ese producto ya no está en el carrito. Recarga la página.'}, 400   # NUEVO
        items.append({'nombre': cart_items[i]['name'], 'cantidad': cantidad})             # NUEVO
        indices.append(i)                                                                 # NUEVO
                                                                                          # NUEVO
    ok, mensaje = comprar(items)                                                          # NUEVO
    if ok:                                                                                # NUEVO
        for i in sorted(set(indices), reverse=True):                                      # NUEVO
            cart_items.pop(i)                                                             # NUEVO
    return {'ok': ok, 'mensaje': mensaje}, (200 if ok else 400)                           # NUEVO


if __name__ == '__main__':
    app.run(debug=True)