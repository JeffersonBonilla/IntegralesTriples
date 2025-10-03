from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N
import os
import re

app = Flask(__name__)

# --- Limpiar expresión para SymPy ---
def limpiar_expr(expr):
    if not expr:
        return "0"
    expr = expr.replace("π", "pi")
    expr = expr.replace("\\theta", "theta")
    expr = expr.replace("\\phi", "phi")
    expr = expr.replace("\n", "")
    expr = expr.replace("$", "")

    # Insertar multiplicaciones implícitas
    expr = re.sub(r'(\d)([A-Za-z\(])', r'\1*\2', expr)
    expr = re.sub(r'([A-Za-z\)])(\d|\()', r'\1*\2', expr)

    expr = expr.replace("^", "**")
    return expr.strip()

# --- Ruta de integral ---
@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = limpiar_expr(data.get("expr", ""))
    orden = data.get("orden", [])
    limites = data.get("limites", {})

    try:
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        # --- SOLO CARTESIANA ---
        for var in orden:
            v = symbols(var)
            if var in limites:
                a, b = limpiar_expr(limites[var][0]), limpiar_expr(limites[var][1])
                paso = integrate(current, (v, sympify(a), sympify(b)))
                pasos.append(f"\\textbf{{Integrando respecto a {var}:}} \\\\ "
                             f"$\\int_{{{a}}}^{{{b}}} {latex(current)} \\, d{var} = {latex(paso)}$")
                current = paso

        try:
            resultado_decimal = float(N(current))
        except:
            resultado_decimal = str(N(current))

        return jsonify({
            "resultado": str(current),
            "resultado_decimal": resultado_decimal,
            "latex": latex(current),
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)




