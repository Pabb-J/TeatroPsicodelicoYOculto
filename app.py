from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


def conectar_db():
    return pymysql.connect(
        host='25pabb.mysql.pythonanywhere-services.com',
        user='25pabb',
        password='Teatro2025!',
        db='25pabb$teatrobd',
        cursorclass=pymysql.cursors.DictCursor
    )
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Datos simulados para usuarios y obras
usuarios = {}
obras = [
    {'id': 1, 'titulo': 'Hamlet', 'descripcion': 'Tragedia de Shakespeare', 'precio': 500},
    {'id': 2, 'titulo': 'La Casa de Bernarda Alba', 'descripcion': 'Drama de Lorca', 'precio': 400},
    {'id': 3, 'titulo': 'El Fantasma de la Ópera', 'descripcion': 'Musical clásico', 'precio': 600}
]

@app.route('/mis_compras')
def mis_compras():
    if 'username' not in session:
        flash('Debés iniciar sesión para ver tus compras.')
        return redirect(url_for('login'))

    usuario = session['username']

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, o.titulo AS obra, e.cantidad, e.fecha, (e.cantidad * o.precio) AS total
        FROM entradas e
        JOIN obras o ON e.obra_id = o.id
        WHERE e.usuario = %s
    """, (usuario,))
    compras = cursor.fetchall()
    total_gastado = sum(compra['total'] for compra in compras)
    cursor.close()
    conn.close()

    return render_template('mis_compras.html', compras=compras, total_gastado=total_gastado)

@app.route('/comprar/<int:obra_id>', methods=['POST'])
def comprar(obra_id):
    if 'username' not in session:
        flash('Debés iniciar sesión para comprar entradas.')
        return redirect(url_for('login'))

    usuario = session['username']
    cantidad = int(request.form.get('cantidad', 1))

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO entradas (usuario, obra_id, cantidad) VALUES (%s, %s, %s)",
        (usuario, obra_id, cantidad)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash('Compra realizada con éxito.')
    return redirect(url_for('teatro'))

@app.route('/eliminar_compra/<int:compra_id>', methods=['POST'])
def eliminar_compra(compra_id):
    if 'username' not in session:
        flash('Debés iniciar sesión para eliminar compras.')
        return redirect(url_for('login'))

    usuario = session['username']

    conn = conectar_db()
    cursor = conn.cursor()

    # Eliminar solo si la compra pertenece al usuario logueado
    cursor.execute("DELETE FROM entradas WHERE id = %s AND usuario = %s", (compra_id, usuario))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Compra eliminada correctamente.')
    return redirect(url_for('mis_compras'))

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('teatro'))
    else:
        return redirect(url_for('login'))

@app.route('/teatro')
def teatro():
    if 'username' not in session:
        flash('Debés iniciar sesión para ver las obras.')
        return redirect(url_for('login'))
    return render_template('teatro.html', obras=obras)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Conexión a la base
        conn = conectar_db()
        cursor = conn.cursor()

        # Buscar usuario
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario and check_password_hash(usuario['password'], password):
            session['username'] = username
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('teatro'))
        else:
            flash('Usuario o contraseña incorrectos.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash('Completá todos los campos.')
            return redirect(url_for('registro'))

        conn = conectar_db()
        cursor = conn.cursor()

        # Validar existencia por username o email
        cursor.execute("SELECT id FROM usuarios WHERE username = %s OR email = %s", (username, email))
        existente = cursor.fetchone()
        if existente:
            flash('El usuario o el email ya están registrados.')
            cursor.close()
            conn.close()
            return redirect(url_for('registro'))

        password_segura = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password_segura)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Registro exitoso. Ya podés iniciar sesión.')
        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Sesión cerrada correctamente.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)