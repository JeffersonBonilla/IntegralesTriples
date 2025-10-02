from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin
import os

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr", "")
    orden = data.get("orden", [])
    limites = data.get("limites", {})
    tipo = data.get("tipo", "Cartesiana")  # Recibe el tipo de integral

    try:
        # Definir símbolos, eliminando rho y usando r para esféricas
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        is_cil = tipo == "Cilíndrica"
        is_esp = tipo == "Esférica"

        # Realizar la integración según el orden especificado
        for var in orden:
            v = symbols(var)
            if var in limites:
                a, b = limites[var]
                expr_aux = current
                # Aplicar jacobiano según el tipo de integral
                if is_cil and var == "r":
                    expr_aux *= r
                if is_esp and var == "r":
                    expr_aux *= r**2 * sin(phi)  # Corregido de rho a r
                paso = integrate(expr_aux, (v, sympify(a), sympify(b)))
                pasos.append(f"\\textbf{{Integrando respecto a {var}:}} \\\\ $\\int_{{{a}}}^{{{b}}} {latex(expr_aux)} \\, d{var} = {latex(paso)}$")
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
