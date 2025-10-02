from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales Triples funcionando!"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr", "")
    orden = data.get("orden", [])   # 👈 nuevo campo
    limites = data.get("limites", {})  # { "x": ["0","2pi"], "y": ["0","1"], "z":["0","r"] }

    try:
        # Variables dinámicas
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)  # reconoce pi, sqrt, theta, etc.

        pasos = []
        current_expr = expr

        # Iterar según el orden que manda la app
        for var in orden:
            if var in limites:
                v = symbols(var)
                a, b = limites[var]
                paso = integrate(current_expr, (v, sympify(a), sympify(b)))
                pasos.append(
                    f"\\textbf{{Integrando respecto a {var}:}} \\\\ "
                    f"$\\int_{{{a}}}^{{{b}}} {latex(current_expr)} \\, d{var} = {latex(paso)}$"
                )
                current_expr = paso

        return jsonify({
            "resultado": str(current_expr),
            "latex": latex(current_expr),
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # Render necesita host=0.0.0.0 y puerto dinámico
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



