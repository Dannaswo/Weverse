import os
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_INVENTARIO = os.path.join(CARPETA, "inventario.db")
RUTA_USUARIOS = os.path.join(CARPETA, "usuarios.db")


def conectar(ruta):
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    return conexion


def iniciar_bases():
    # Base 1: inventario
    with conectar(RUTA_INVENTARIO) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)
        productos = [
            ("BTS Island Figure V4", 85.14, 15),
            ("Proof (Collector's Edition)", 212.48, 8),
            ("Agust D (BTS) 'D-DAY' (Set)", 26.46, 20),
        ]
        for nombre, precio, stock in productos:
            conn.execute(
                "INSERT OR IGNORE INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                (nombre, precio, stock),
            )

    # Base 2: usuarios
    with conectar(RUTA_USUARIOS) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                username TEXT,
                correo TEXT,
                fecha TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        # Si la tabla ingresos es la versión vieja (sin username y correo),
        # le agrega esas columnas y llena los ingresos que ya existían.
        columnas = [c["name"] for c in conn.execute("PRAGMA table_info(ingresos)")]
        if "username" not in columnas:
            conn.execute("ALTER TABLE ingresos ADD COLUMN username TEXT")
            conn.execute("ALTER TABLE ingresos ADD COLUMN correo TEXT")
            conn.execute("""
                UPDATE ingresos SET
                    username = (SELECT nombre FROM usuarios WHERE usuarios.id = ingresos.usuario_id),
                    correo = (SELECT correo FROM usuarios WHERE usuarios.id = ingresos.usuario_id),
                    fecha = datetime(fecha, '-5 hours')
            """)

        conn.execute("DROP VIEW IF EXISTS vista_ingresos")


def ver_inventario():
    with conectar(RUTA_INVENTARIO) as conn:
        filas = conn.execute("SELECT nombre, precio, stock FROM productos").fetchall()
        return [dict(f) for f in filas]


def comprar(items):
    if not items:
        return False, "El carrito está vacío"

    totales = {}
    for item in items:
        nombre = item.get("nombre")
        try:
            cantidad = int(item.get("cantidad", 1))
        except (TypeError, ValueError):
            return False, "Cantidad inválida"
        if cantidad < 1:
            return False, "Cantidad inválida"
        totales[nombre] = totales.get(nombre, 0) + cantidad

    with conectar(RUTA_INVENTARIO) as conn:
        for nombre, cantidad in totales.items():
            fila = conn.execute(
                "SELECT stock FROM productos WHERE nombre = ?", (nombre,)
            ).fetchone()
            if fila is None:
                return False, f"El producto '{nombre}' no existe en el inventario"
            if fila["stock"] < cantidad:
                return False, f"No hay suficiente stock de '{nombre}' (quedan {fila['stock']})"

        for nombre, cantidad in totales.items():
            conn.execute(
                "UPDATE productos SET stock = stock - ? WHERE nombre = ?",
                (cantidad, nombre),
            )
    return True, "Compra realizada con éxito"


def crear_cuenta(username, correo, contrasena, confirmar):
    username = (username or "").strip()
    correo = (correo or "").strip().lower()
    contrasena = contrasena or ""

    if not correo:
        return False, "Escribe un correo"
    if not username or len(username) > 32:
        return False, "El username debe tener entre 1 y 32 caracteres"
    if not 8 <= len(contrasena) <= 32:
        return False, "La contraseña debe tener entre 8 y 32 caracteres"

    tiene_letra = any(c.isalpha() for c in contrasena)
    tiene_numero = any(c.isdigit() for c in contrasena)
    tiene_especial = any(not c.isalnum() for c in contrasena)
    if not (tiene_letra and tiene_numero and tiene_especial):
        return False, "La contraseña debe incluir letras, números y un carácter especial (ej: ! @ # $)"
    if contrasena != (confirmar or ""):
        return False, "Las contraseñas no coinciden"

    try:
        with conectar(RUTA_USUARIOS) as conn:
            conn.execute(
                "INSERT INTO usuarios (nombre, correo, contrasena) VALUES (?, ?, ?)",
                (username, correo, generate_password_hash(contrasena)),
            )
        return True, "Cuenta creada"
    except sqlite3.IntegrityError:
        return False, "Ese correo ya tiene una cuenta"


def iniciar_sesion(correo, contrasena):
    correo = (correo or "").strip().lower()
    with conectar(RUTA_USUARIOS) as conn:
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE correo = ?", (correo,)
        ).fetchone()

        if usuario is None:
            return False, "No existe una cuenta con ese correo"
        if not check_password_hash(usuario["contrasena"], contrasena or ""):
            return False, "Contraseña incorrecta"

        conn.execute(
            "INSERT INTO ingresos (usuario_id, username, correo, fecha) "
            "VALUES (?, ?, ?, datetime('now', '-5 hours'))",
            (usuario["id"], usuario["nombre"], usuario["correo"]),
        )
        return True, usuario["nombre"]


def alerta(mensaje, destino=None):
    texto = json.dumps(mensaje).replace("<", "\\u003c")
    despues = f"location.href = {json.dumps(destino)};" if destino else "history.back();"
    return f"<script>alert({texto}); {despues}</script>"


iniciar_bases()


if __name__ == "__main__":
    print("INVENTARIO ACTUAL:")
    for p in ver_inventario():
        print(" -", p["nombre"], "| USD", p["precio"], "| stock:", p["stock"])