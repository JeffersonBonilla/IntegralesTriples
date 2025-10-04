from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin
import os

app = Flask(__name__)

def limpiar_expr(expr):
    if not expr:
        return "0"
    expr = expr.replace("π", "pi")
    expr = expr.replace("\\theta", "theta")
    expr = expr.replace("\\phi", "phi")
    expr = expr.replace("\n", "")
    expr = expr.replace("$", "")
    expr = expr.replace(" ", "*")  # convierte "2 y" en "2*y"
    return expr

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = limpiar_expr(data.get("expr", ""))
    orden = data.get("orden", [])
    limites = data.get("limites", {})
    tipo = data.get("tipo", "Cartesiana")

    try:
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        is_cil = tipo == "Cilíndrica"
        is_esp = tipo == "Esférica"

        for i, var_name in enumerate(orden, start=1):
            v = symbols(var_name)
            if var_name not in limites:
                return jsonify({"error": f"No hay límites para {var_name}"}), 400
            a, b = sympify(limites[var_name][0]), sympify(limites[var_name][1])

            integrando = current
            # Aplicar jacobiano
            if is_cil and var_name == "r":
                integrando *= r
            if is_esp and var_name == "r":
                integrando *= r**2 * sin(phi)

            paso_simbolico = integrate(integrando, (v, a, b))
            # Evaluar límites para mostrar paso a paso
            paso_evaluado = paso_simbolico

            pasos.append(f"\\textbf{{Paso {i}: Integrando respecto a {var_name}}} \\\\ "
                         f"$$\\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(integrando)} \\, d{var_name} = {latex(paso_simbolico)}$$ \\\\ "
                         f"Evaluando los límites: {latex(paso_evaluado)}")

            current = paso_evaluado

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





