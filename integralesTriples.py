from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin, pi
import os
app = Flask(__name__)

# Limpiar expresión para SymPy
def limpiar_expr(expr):
    if not expr:
        return "0"
    expr = expr.replace("π", "pi")
    expr = expr.replace("\\theta", "theta")
    expr = expr.replace("\\phi", "phi")
    expr = expr.replace("\n", "")
    expr = expr.replace("$", "")
    return expr

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = limpiar_expr(data.get("expr", ""))
    orden = data.get("orden", [])
    limites = data.get("limites", {})
    tipo = data.get("tipo", "Cartesiana")  # Cartesiana, Cilíndrica, Esférica

    try:
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        is_cil = tipo == "Cilíndrica"
        is_esp = tipo == "Esférica"

        for var_name in orden:
            v = symbols(var_name)
            if var_name not in limites:
                return jsonify({"error": f"Variable {var_name} no tiene límites"}), 400

            a_str, b_str = limpiar_expr(limites[var_name][0]), limpiar_expr(limites[var_name][1])
            a, b = sympify(a_str), sympify(b_str)

            # Expresión con jacobiano
            expr_aux = current
            if is_cil and var_name == "r":
                expr_aux *= r
            if is_esp and var_name == "r":
                expr_aux *= r**2 * sin(phi)

            # Integrar
            integral_intermedia = integrate(expr_aux, (v, a, b))
            paso_latex = (
                f"\\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(expr_aux)} \\, d{var_name} = {latex(integral_intermedia)}"
            )
            pasos.append(paso_latex)
            current = integral_intermedia

        try:
            resultado_decimal = float(N(current))
        except:
            resultado_decimal = str(N(current))

        return jsonify({
            "resultado": latex(current),       # Para mostrar simbólico
            "resultado_decimal": resultado_decimal,
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=5000, debug=True)




