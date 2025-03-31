
from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from bot_unificado import execute_bot

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/executar', methods=['POST'])
def executar():
    try:
        num_execucoes = int(request.form['num_execucoes'])
        if num_execucoes <= 0:
            return jsonify({"error": "O número de execuções deve ser maior que zero"}), 400

        sucessos = 0
        for i in range(num_execucoes):
            if execute_bot():
                sucessos += 1

        return jsonify({
            "message": f"Execuções concluídas. {sucessos} de {num_execucoes} foram bem-sucedidas.",
            "sucessos": sucessos,
            "total": num_execucoes
        })

    except ValueError:
        return jsonify({"error": "Número de execuções inválido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
