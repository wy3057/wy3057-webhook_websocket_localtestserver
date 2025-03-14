from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print("Received data:", data)
        # 这里可以添加处理数据的逻辑
        return jsonify({"status": "success", "message": "Data received"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)