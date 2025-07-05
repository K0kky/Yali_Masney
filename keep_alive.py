from flask import Flask
from threading import Thread

app = Flask(name)

@app.route('/')
def home():
    return "Bot is running."

def run():
    app.run(host='0.0.0.0', port=10000)  # Renderが検知できるように明示

def start_server():
    t = Thread(target=run)
    t.start()
