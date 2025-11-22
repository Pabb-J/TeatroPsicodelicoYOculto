from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


def conectar_db():
    return pymysql.connect(
        host='25pabb.mysql.pythonanywhere-services.com',
        user='25pabb',
        password='Gladiadore7777',
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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Conexión a la base
        conn = conectar_db()
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        existente = cursor.fetchone()

        if existente:
            flash('El usuario ya existe.')
            cursor.close()
            conn.close()
            return redirect(url_for('registro'))

        # Hashear la contraseña
        password_segura = generate_password_hash(password)

        # Insertar nuevo usuario
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