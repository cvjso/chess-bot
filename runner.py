from flask import Flask
import subprocess
from threading import Thread

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/info")
def info():
    return subprocess.run(["bash", "-c", "ps aux | grep python"], capture_output=True).stdout.decode("utf-8")

def bot():
    subprocess.run(["python", "main.py"])

if __name__ == "__main__":  
    b = Thread(target=bot)
    b.start()
    app.run(debug = True)