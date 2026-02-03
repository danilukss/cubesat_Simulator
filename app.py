from flask import Flask, render_template_string, request
import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot

app = Flask(__name__)

# -------------------------
# Симуляция CubeSat
# -------------------------
def simulate(angle0, algo="PID"):
    dt = 0.01
    T = 8
    steps = int(T/dt)
    I = 0.01
    state = np.array([angle0,0.0])
    history = []

    if algo == "PID":
        kp, ki, kd = 5, 0.1, 2
        integral = 0
        prev_error = 0
    else:  # LQR
        A = np.array([[0,1],[0,0]])
        B = np.array([[0],[1/I]])
        Q = np.diag([10,1])
        R = np.array([[0.1]])
        K = np.array([[1.0,1.0]])  # упрощение для демонстрации

    for _ in range(steps):
        error = -state[0]
        if algo=="PID":
            integral += error*dt
            derivative = (error-prev_error)/dt
            prev_error = error
            torque = kp*error + ki*integral + kd*derivative
        else:
            torque = float(-K @ state)
        state[0] += state[1]*dt
        state[1] += torque/I*dt
        history.append(state[0])
    return history

# -------------------------
# 3D куб CubeSat через Plotly
# -------------------------
def cube_3d(angle):
    r = [-0.5,0.5]
    X, Y = np.meshgrid(r,r)
    Z = np.zeros_like(X)
    c,s = np.cos(angle), np.sin(angle)
    Xr = c*X - s*Y
    Yr = s*X + c*Y
    Zr = Z
    data = [go.Surface(z=Zr, x=Xr, y=Yr, colorscale='Viridis', opacity=0.7)]
    layout = go.Layout(scene=dict(
        xaxis=dict(range=[-1,1]),
        yaxis=dict(range=[-1,1]),
        zaxis=dict(range=[-1,1])
    ))
    fig = go.Figure(data=data, layout=layout)
    return plot(fig, output_type='div', include_plotlyjs=False)

# -------------------------
# HTML шаблон с CSS
# -------------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CubeSat Simulator Pro</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
body {font-family: 'Arial', sans-serif; background-color: #0d1b2a; color: #e0e1dd; padding: 20px;}
h1 {color:#fca311;}
button {padding: 10px 20px; margin:5px; font-size:16px; cursor:pointer; border:none; border-radius:5px;}
button:hover {opacity:0.8;}
#pid {background-color:#f77f00; color:white;}
#lqr {background-color:#219ebc; color:white;}
#compare {background-color:#8ac926; color:white;}
input[type=text]{padding:5px; width:80px;}
a {color:#fca311; text-decoration:none; margin-left:10px;}
a:hover {text-decoration:underline;}
</style>
</head>
<body>
<h1>🛰 CubeSat Simulator Pro</h1>
<p>Интерактивное моделирование системы ориентации CubeSat.</p>

<form method="post">
<label>Начальный угол (рад):</label><br>
<input type="text" name="angle" value="0.5"><br><br>

<button type="submit" name="algo" value="PID" id="pid">Запустить PID</button>
<button type="submit" name="algo" value="LQR" id="lqr">Запустить LQR</button>
<button type="submit" name="algo" value="Compare" id="compare">Сравнить PID vs LQR</button>
</form>

{% if plot_div %}
<h2>График ориентации CubeSat</h2>
{{ plot_div|safe }}
{% endif %}

{% if cube_div %}
<h2>3D CubeSat</h2>
{{ cube_div|safe }}
{% endif %}

<p>Полезные ресурсы: 
<a href="https://ru.wikipedia.org/wiki/CubeSat" target="_blank">CubeSat Wiki</a> | 
<a href="https://www.nasa.gov/mission_pages/cubesats/main/index.html" target="_blank">NASA CubeSats</a>
</p>
</body>
</html>
"""

# -------------------------
# Маршрут Flask
# -------------------------
@app.route("/", methods=["GET","POST"])
def index():
    plot_div = None
    cube_div = None
    if request.method=="POST":
        angle0 = request.form.get("angle","0.5").replace(",", ".")
        try:
            angle0 = float(angle0)
        except ValueError:
            angle0 = 0.5

        algo = request.form.get("algo","PID")
        if algo=="Compare":
            pid_hist = simulate(angle0,"PID")
            lqr_hist = simulate(angle0,"LQR")
            t = np.arange(len(pid_hist))*0.01
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=pid_hist, mode='lines', name='PID'))
            fig.add_trace(go.Scatter(x=t, y=lqr_hist, mode='lines', name='LQR'))
            fig.update_layout(title='Сравнение PID vs LQR', xaxis_title='Время, с', yaxis_title='Угол, рад')
            plot_div = plot(fig, output_type='div', include_plotlyjs=True)
            cube_div = cube_3d(lqr_hist[-1])
        else:
            hist = simulate(angle0, algo)
            t = np.arange(len(hist))*0.01
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=hist, mode='lines', name=algo))
            fig.update_layout(title=f'Ориентация CubeSat ({algo})', xaxis_title='Время, с', yaxis_title='Угол, рад')
            plot_div = plot(fig, output_type='div', include_plotlyjs=True)
            cube_div = cube_3d(hist[-1])

    return render_template_string(HTML, plot_div=plot_div, cube_div=cube_div)

# -------------------------
# Запуск
# -------------------------
if __name__=="__main__":
    app.run(debug=True)
