# Activar el entorno virtual => source venv/scripts/activate (windows con una bash shell)

from flask import Flask
from flask import render_template, request, redirect, url_for, send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)
mysql = MySQL()


app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "MyRootCabezones111111!"
app.config["MYSQL_DATABASE_DB"] = "empleados"

UPLOADS = os.path.join("src/uploads")
app.config["UPLOADS"] = UPLOADS

mysql.init_app(app)

@app.route("/")
def index():
    conn = mysql.connect()
    cursor = conn.cursor()

    sql= 'SELECT * FROM empleados;'
    cursor.execute(sql)
    empleados = cursor.fetchall()

    print(empleados)
    conn.commit()
    return render_template("empleados/index.html", empleados=empleados)


@app.route('/foto_perfil/<path:nombre_foto>')
def uploads(nombre_foto):
    return send_from_directory(os.path.join("uploads"), nombre_foto)


@app.route("/create")
def create():
    return render_template("empleados/create.html")

@app.route('/store', methods=['POST'])
def store():
    _nombre = request.form["txtNombre"]
    _correo = request.form["txtCorreo"]
    _foto = request.files["txtFoto"]

    now = datetime.now()
    print(now)
    tiempo = now.strftime("%Y%H%M%S")
    print(tiempo)

    if _foto.filename != "":
        nuevo_nombre_foto = tiempo + "_" + _foto.filename
        _foto.save("src/uploads/" + nuevo_nombre_foto)

    sql = "INSERT INTO empleados (nombre, correo, foto) values (%s, %s, %s);"
    datos = (_nombre, _correo, nuevo_nombre_foto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    return redirect("/")


@app.route('/delete/<int:id>')
def delete(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = f'SELECT foto FROM empleados WHERE id={id}'
    cursor.execute(sql)
    nombre_foto = cursor.fetchone()[0]

    try:
        os.remove(os.path.join(app.config["UPLOADS"], nombre_foto)) # borra la foto en carpeta
    except:
        pass

    sql = "DELETE FROM empleados WHERE id=%s" # borra la fila de la DB
    cursor.execute(sql, (id))
    conn.commit()

    return redirect("/")

@app.route('/modify/<int:id>')
def modify(id):
    sql = f'SELECT * FROM empleados WHERE id="{id}"'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleado = cursor.fetchone()
    conn.commit()

    return render_template("empleados/edit.html", empleado= empleado)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form["txtNombre"]
    _correo = request.form["txtCorreo"]
    _foto = request.files["txtFoto"]
    id = request.form["txtId"]
    # id = int(id)
    print("="*20)
    print(id)

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = f'UPDATE empleados SET nombre="{_nombre}", correo="{_correo}" WHERE id={id}'

    if _foto.filename != "":
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevo_nombre_foto = tiempo + "_" + _foto.filename
        _foto.save("src/uploads/" + nuevo_nombre_foto) # guardo la imagen en carpeta

        sql_if = f'SELECT foto FROM empleados WHERE id="{id}"'
        cursor.execute(sql_if)
        foto_anterior = cursor.fetchone()[0] # selecciono foto que estaba en DB

        borrar_foto_anterior = os.path.join(app.config["UPLOADS"], foto_anterior)
        print(borrar_foto_anterior)

        os.remove(borrar_foto_anterior)

        sql_if = f'UPDATE empleados SET foto="{nuevo_nombre_foto}" WHERE id={id}'
        cursor.execute(sql_if)
        conn.commit()

    cursor.execute(sql)
    conn.commit()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)
    