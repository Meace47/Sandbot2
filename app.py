from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "🚛 SandBot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    print(update) # This prints Telegram messages to the console
    return {"ok": True}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)