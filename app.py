from flask import Flask, render_template_string, jsonify
import random
import time

app = Flask(__name__)

# состояния CubeSat
state = {
    "power": False,
    "communication": False,
    "payload": False
}

# история телеметрии
history = {
    "time": [],
    "temperature": [],
    "voltage": []
}

# HTML шаблон как строка
BASE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>CubeSat Control Center</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body { background:#0b1020; color:white; font-family:Arial; text-align:center; }
.block { background:#1e2747; padding:15px; margin:10px; display:inline-block; width:200px; border-radius:12px; }
.on { color:#00ff9c; font-weight:bold; }
.off { color:#ff5c5c; font-weight:bold; }
button { width:100%; padding:10px; margin-top:10px; border:none; border-radius:8px; background:#2563eb; color:white; cursor:pointer; }
button:hover { background:#1d4ed8; }
a { color:#7dd3fc; }
</style>
</head>
<body>

<h1>🛰 CubeSat Control Center</h1>
<a href="/mission">➡ Mission page</a><br><br>

<div class="block">
🔋 Power<br>
<span id="power" class="{{ 'on' if state.power else 'off' }}">{{ 'ON' if state.power else 'OFF' }}</span>
<button onclick="toggle('power')">Toggle</button>
</div>

<div class="block">
📡 Communication<br>
<span id="communication" class="{{ 'on' if state.communication else 'off' }}">{{ 'ON' if state.communication else 'OFF' }}</span>
<button onclick="toggle('communication')">Toggle</button>
</div>

<div class="block">
🧪 Payload<br>
<span id="payload" class="{{ 'on' if state.payload else 'off' }}">{{ 'ON' if state.payload else 'OFF' }}</span>
<button onclick="toggle('payload')">Toggle</button>
</div>

<h2>📊 Telemetry</h2>
<canvas id="chart" width="400" height="200"></canvas><br>
<button onclick="updateTelemetry()">🔄 Update</button>

<script>
const ctx = document.getElementById('chart');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Temperature °C', data: [], borderWidth: 2, borderColor:'orange', fill:false },
            { label: 'Voltage V', data: [], borderWidth: 2, borderColor:'lightgreen', fill:false }
        ]
    },
    options: { responsive: true, animation: false }
});

function toggle(name){
    fetch('/toggle/' + name)
    .then(res => res.json())
    .then(d => {
        for(let k in d){
            let el = document.getElementById(k);
            el.textContent = d[k] ? 'ON' : 'OFF';
            el.className = d[k] ? 'on' : 'off';
        }
    });
}

function updateTelemetry(){
    fetch('/telemetry')
    .then(res => res.json())
    .then(d => {
        chart.data.labels = d.time;
        chart.data.datasets[0].data = d.temperature;
        chart.data.datasets[1].data = d.voltage;
        chart.update();
    });
}

// автообновление каждые 5 секунд
setInterval(updateTelemetry, 5000);
</script>

</body>
</html>"""

MISSION_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Mission</title>
<style>
body { background:#0b1020; color:white; font-family:Arial; padding:40px; }
a { color:#7dd3fc; }
</style>
</head>
<body>
<h1>🎯 CubeSat Mission</h1>
<p>Цель миссии — демонстрация работы малогабаритного CubeSat, включая:</p>
<ul>
<li>Контроль систем спутника</li>
<li>Сбор и отображение телеметрии</li>
<li>Обновление данных и графики в реальном времени</li>
<li>Подготовка к будущим научным экспериментам</li>
</ul>
<a href="/">⬅ Back to control</a>
</body>
</html>"""

# генерация случайной телеметрии
def generate_telemetry():
    return {
        "temperature": round(random.uniform(-20, 60), 1),
        "voltage": round(random.uniform(3.6, 4.2), 2),
        "light": round(random.uniform(0, 100), 1)
    }

# маршруты
@app.route("/")
def index():
    return render_template_string(BASE_HTML, state=state)

@app.route("/mission")
def mission():
    return render_template_string(MISSION_HTML)

@app.route("/toggle/<name>")
def toggle_state(name):
    if name in state:
        state[name] = not state[name]
    return jsonify(state)

@app.route("/telemetry")
def telemetry():
    data = generate_telemetry()
    history["time"].append(time.strftime("%H:%M:%S"))
    history["temperature"].append(data["temperature"])
    history["voltage"].append(data["voltage"])

    # храним последние 10 значений
    if len(history["time"]) > 10:
        for k in history:
            history[k].pop(0)

    return jsonify({
        "time": history["time"],
        "temperature": history["temperature"],
        "voltage": history["voltage"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    