from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales Triples Universal funcionando!"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr", "")
    orden = data.get("orden", [])       # ej: ["z","r","theta"]
    limites = data.get("limites", {})   # ej: { "x":["0","2"], "y":["0","1"], "z":["0","r"] }

    try:
        # Definir todas las variables posibles
        x, y, z, r, theta, phi, rho = symbols("x y z r theta phi rho")
        expr = sympify(expr_str)

        # Detectar coordenadas y factor jacobiano
        variables_set = set(orden)
        factor = 1
        if {"r", "theta", "z"} <= variables_set:
            factor = r                  # cilíndricas
        elif {"rho", "theta", "phi"} <= variables_set:
            factor = rho**2 * sin(phi) # esféricas

        expr = expr * factor

        pasos = []
        current_expr = expr

        for var in orden:
            if var in limites:
                v = symbols(var)
                a, b = limites[var]
                paso_simb = integrate(current_expr, (v, sympify(a), sympify(b)))
                paso_num = N(paso_simb)
                
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
        print("ERROR en API:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

