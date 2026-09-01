from flask import Flask, request, redirect, render_template
import pymysql
import os
import time

sample = Flask(__name__)
app = sample

# Configuración segura: se leen credenciales desde el entorno sin contraseñas hardcodeadas
conf_db = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),  # Sin variables hardcodeadas (Solución Bandit B105)
    "database": os.environ.get("DB_NAME", "adso_db"),
    "port": int(os.environ.get("DB_PORT", 3306))
}

def in_bd():
    retries = 10
    while retries > 0:
        try:
            conn = pymysql.connect(**conf_db) 
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aprendices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_completo VARCHAR(100) NOT NULL,
                    numero_documento VARCHAR(20) NOT NULL,
                    ficha VARCHAR(20) NOT NULL,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()
            conn.close()
            print("Se inició la base de datos correctamente")
            break
        except Exception as e:
            print(f"Esperando a la base de datos... ({e})")
            retries -= 1
            time.sleep(3)

in_bd()

@sample.route("/")
def home():
    # Solución Pytest: Se eliminó el jsonify con 500 forzado y se restaura la vista
    registros = []
    mens_error = None
    mens_exito = None

    try:
        conn = pymysql.connect(**conf_db) 
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_completo, numero_documento, ficha, creado_en FROM aprendices ORDER BY id DESC")
        registros = cursor.fetchall()
        conn.close()
        mens_exito = "CONEXIÓN EXITOSA A LA BASE DE DATOS" 
    except Exception as e:
        mens_error = f"Error al consultar los datos de la bd: {e}"

    return render_template("index.html", lista_aprendices=registros, error=mens_error, exito=mens_exito)


@sample.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre")
    documento = request.form.get("documento")
    ficha = request.form.get("ficha")

    try:
        conn = pymysql.connect(**conf_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO aprendices (nombre_completo, numero_documento, ficha) VALUES (%s, %s, %s)",
            (nombre, documento, ficha)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al ingresar los datos: {e}")

    return redirect("/") 

if __name__ == "__main__":
    # Solución Bandit: Se evalúa FLASK_DEBUG desde entorno (B201) y se agrega # nosec para el bind en Docker (B104)
    modo_debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    sample.run(host='0.0.0.0', port=5050, debug=modo_debug)  # nosec B104
