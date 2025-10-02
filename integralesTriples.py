from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales Triples funcionando!"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr", "")
    orden = data.get("orden", [])       # ej: ["z","r","theta"]
    limites = data.get("limites", {})   # ej: { "x":["0","2"], "y":["0","1"], "z":["0","r"] }

    try:
        # Variables simbólicas
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)  # reconoce pi, sqrt(), theta, etc.

        pasos = []
        current_expr = expr

        for var in orden:
            if var in limites:
                v = symbols(var)
                a, b = limites[var]
                paso_simb = integrate(current_expr, (v, sympify(a), sympify(b)))
                paso_num = N(paso_simb)  # evalúa numéricamente
                
                # Paso detallado con simbólico y decimal
                pasos.append(
                    f"\\textbf{{Integrando respecto a {var}:}} \\\\ "
                    f"$\\int_{{{a}}}^{{{b}}} {latex(current_expr)} \\, d{var} = {latex(paso_simb)} = {paso_num}$"
                )
                current_expr = paso_simb

        return jsonify({
            "resultado": str(current_expr),
            "resultado_decimal": float(N(current_expr)),
            "latex": latex(current_expr),
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


