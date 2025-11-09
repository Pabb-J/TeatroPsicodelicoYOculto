from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Conexión a InfinityFree
db = mysql.connector.connect(
    host="sqlXXX.infinityfree.com",  # ← reemplazá con tu host
    user="tu_usuario",               # ← tu usuario InfinityFree
    password="tu_contraseña",        # ← tu contraseña InfinityFree
    database="tu_base_de_datos"      # ← nombre de tu base
)
cursor = db.cursor()

@app.route('/')
def index():
    cursor.execute("SELECT * FROM obras")
    obras = cursor.fetchall()
    return render_template('teatro.html', obras=obras)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND clave=%s", (usuario, clave))
        user = cursor.fetchone()
        if user:
            session['usuario'] = usuario
            return redirect('/')
        else:
            return "Login incorrecto"
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        cursor.execute("INSERT INTO usuarios (usuario, clave) VALUES (%s, %s)", (usuario, clave))
        db.commit()
        return redirect('/login')
    return render_template('registro.html')

@app.route('/reservar/<int:obra_id>')
def reservar(obra_id):
    if 'usuario' not in session:
        return redirect('/login')
    cursor.execute("INSERT INTO reservas (usuario, obra_id) VALUES (%s, %s)", (session['usuario'], obra_id))
    db.commit()
    return "Reserva realizada con éxito"

if __name__ == '__main__':
    app.run(debug=True)
