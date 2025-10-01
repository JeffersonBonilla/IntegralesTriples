from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales Triples funcionando 🚀"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr")
    var_str = data.get("var")

    x = symbols(var_str)
    expr = eval(expr_str)  # ⚠️ para prototipo, luego mejor parser
    result = integrate(expr, x)

    return jsonify({
        "resultado": str(result),
        "latex": latex(result)
    })

if __name__ == "__main__":
    # Render usa el puerto que te da la variable de entorno PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






