from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

state = {
    "power": False,
    "communication": False,
    "payload": False
}

history = {
    "time": [],
    "temperature": [],
    "voltage": []
}

def telemetry():
    return {
        "temperature": round(random.uniform(-20, 60), 1),
        "voltage": round(random.uniform(3.6, 4.2), 2),
        "light": round(random.uniform(0, 100), 1)
    }

@app.route("/")
def index():
    return render_template("index.html", state=state)

@app.route("/mission")
def mission():
    return render_template("mission.html")

@app.route("/toggle/<name>")
def toggle(name):
    if name in state:
        state[name] = not state[name]
    return jsonify(state)

@app.route("/telemetry")
def get_telemetry():
    data = telemetry()

    history["time"].append(time.strftime("%H:%M:%S"))
    history["temperature"].append(data["temperature"])
    history["voltage"].append(data["voltage"])

    if len(history["time"]) > 10:
        history["time"].pop(0)
        history["temperature"].pop(0)
        history["voltage"].pop(0)

    response = {
        "time": history["time"],
        "temperature": history["temperature"],
        "voltage": history["voltage"]
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
    
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>CubeSat Control</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body { background:#0b1020; color:white; font-family:Arial; text-align:center; }
.block { background:#1e2747; padding:15px; margin:10px; display:inline-block; width:200px; border-radius:12px; }
.on { color:#00ff9c; }
.off { color:#ff5c5c; }
button { width:100%; padding:10px; margin-top:10px; border:none; border-radius:8px; background:#2563eb; color:white; }
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
<canvas id="chart" width="400"></canvas><br>
<button onclick="update()">🔄 Update</button>

<script>
const ctx = document.getElementById('chart');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Temperature °C', data: [], borderWidth: 2 },
            { label: 'Voltage V', data: [], borderWidth: 2 }
        ]
    }
});

function toggle(name){
    fetch('/toggle/' + name)
    .then(r=>r.json())
    .then(d=>{
        for(let k in d){
            let el=document.getElementById(k);
            el.textContent=d[k]?'ON':'OFF';
            el.className=d[k]?'on':'off';
        }
    });
}

function update(){
    fetch('/telemetry')
    .then(r=>r.json())
    .then(d=>{
        chart.data.labels = d.time;
        chart.data.datasets[0].data = d.temperature;
        chart.data.datasets[1].data = d.voltage;
        chart.update();
    });
}
</script>

</body>
</html>