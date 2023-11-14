from flask import Flask, render_template, request, redirect, url_for, make_response, flash
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from auth.auth import usuarios, autenticar, registrar 
import matplotlib
import os


matplotlib.use('Agg')

app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'tu_clave_secreta'

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        if autenticar(usuario, contrasena):
            # Autenticación exitosa, establecer una cookie para el usuario
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('usuario', usuario)
            return resp

        else:
            return "Credenciales incorrectas. Intente nuevamente."

    return render_template('login.html')

# Página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        if registrar(usuario, contrasena):
            # Registro exitoso, redirigir al inicio de sesión
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('usuario', usuario)
            return resp

        else:
            return "El usuario ya existe. Elija otro nombre de usuario."

    return render_template('register.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    usuario = request.cookies.get('usuario')

    if request.method == 'POST':
        try:
            r = float(request.form.get('r'))
            K = float(request.form.get('K'))
            y0 = float(request.form.get('y0'))

            # Obtener procedimientos simulados
            procedimientos = obtener_procedimientos_simulados(r, K, y0)

            # Título personalizado
            titulo = "Resultado de la simulación para r={}, K={}, y0={}".format(r, K, y0)

            # Realizar la simulación
            t_span = (0, 50)
            t_eval = np.linspace(0, 50, 500)

            solution = solve_ivp(logistic_growth, t_span, [y0], t_eval=t_eval, args=(r, K), method='RK45')

            plt.figure(figsize=(10, 6))
            plt.plot(solution.t, solution.y[0])
            plt.xlabel('Tiempo')
            plt.ylabel('Población del Cultivo')
            plt.title('Modelo de Crecimiento Logístico de un Cultivo')
            plt.grid(True)

            # Verificar y crear el directorio 'static'
            static_dir = os.path.join(app.root_path, app.static_folder)
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)

            plt.savefig(os.path.join(static_dir, 'plot.png'))
            plt.close()

            return render_template('result.html', procedimientos=procedimientos, usuario=usuario, titulo=titulo, solution=solution)

        except ValueError:
            flash("Ingrese valores numéricos válidos para r, K y y0.", "error")
            return redirect(url_for('index'))

    # Lógica para solicitudes GET
    return render_template('result.html', usuario=usuario, titulo="Resultado de la simulación")

# Define la ecuación diferencial para el modelo de crecimiento logístico
def logistic_growth(t, y, r, K):
    dydt = r * y * (1 - y / K)
    return dydt

@app.route('/logout')
def logout():
    # Limpiar la cookie de usuario
    resp = redirect(url_for('index'))
    resp.delete_cookie('usuario')
    return resp
    
def obtener_procedimientos_simulados(r, K, y0):
    procedimientos = {
        'Procedimiento 1': {
            'descripcion': "Describe la ecuación diferencial para el modelo de crecimiento logístico:"
        },
        'Procedimiento 2': {
            'descripcion': f"La ecuación diferencial utilizada es dy/dt = {r} * y * (1 - y / {K}), que modela el crecimiento logístico de un cultivo en función del tiempo t."
        },
        'Procedimiento 3': {
            'descripcion': "Remplaza los parámetros r, K, y y0 en la ecuación:"
        },
        'Procedimiento 4': {
            'descripcion': f"r representa la tasa de crecimiento ({r}), K es la capacidad de carga del entorno ({K}) para la población del cultivo, y y0 es la población inicial ({y0}) en el tiempo t=0."
        },
        'Procedimiento 5': {
            'descripcion': "Hace los calculos para resolver la ecuación diferencial utilizando solve_ivp:"
        },
        'Procedimiento 6': {
            'descripcion': "Utilizamos la función solve_ivp de SciPy para resolver numéricamente la ecuación diferencial. Se especifica el intervalo de tiempo y los valores iniciales, y la solución se evalúa en varios puntos dentro del intervalo."
        },
        'Procedimiento 7': {
            'descripcion': "Detalla cómo se genera y guarda el gráfico utilizando matplotlib:"
        },
        'Procedimiento 8': {
            'descripcion': "Matplotlib se utiliza para visualizar la solución de la ecuación diferencial. Creamos un gráfico que representa la población del cultivo en función del tiempo y lo guardamos como una imagen estática (plot.png) en la carpeta static."
        },
    }
    return procedimientos



# Página principal con el formulario y manejo de inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def index():
    usuario = request.cookies.get('usuario')
    procedimientos = None

    if request.method == 'POST':
        try:
            r = float(request.form['r'])
            K = float(request.form['K'])
            y0 = float(request.form['y0'])
        except ValueError:
            flash("Ingrese valores numéricos válidos para r, K y y0.", "error")
            return redirect(url_for('index'))

        if usuario:
            # Usuario autenticado, realizar la simulación
            t_span = (0, 50)
            t_eval = np.linspace(0, 50, 500)

            solution = solve_ivp(logistic_growth, t_span, [y0], t_eval=t_eval, args=(r, K), method='RK45')

            plt.figure(figsize=(10, 6))
            plt.plot(solution.t, solution.y[0])
            plt.xlabel('Tiempo')
            plt.ylabel('Población del Cultivo')
            plt.title('Modelo de Crecimiento Logístico de un Cultivo')
            plt.grid(True)

            # Verificar y crear el directorio 'static'
            static_dir = os.path.join(app.root_path, app.static_folder)
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)

            plt.savefig(os.path.join(static_dir, 'plot.png'))
            plt.close()

            # Crear información de procedimientos
            procedimientos = obtener_procedimientos_simulados(r, K, y0)

            return render_template('result.html', procedimientos=procedimientos, usuario=usuario)

        else:
            # Usuario no autenticado, redirigir a la página de inicio de sesión
            return redirect(url_for('login'))

    return render_template('index.html', usuario=usuario)



if __name__ == '__main__':
    app.run(debug=True)

