from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin
import os

app = Flask(__name__)

# Función para limpiar expresiones y límites
def limpiar_expr(expr):
    if not expr:
        return "0"
    expr = expr.replace("π", "pi")
    expr = expr.replace("\\theta", "theta")
    expr = expr.replace("\\phi", "phi")
    expr = expr.replace("\n", "")
    expr = expr.replace("$", "")
    expr = expr.replace(" ", "*")  # Opcional: convierte "2 y" a "2*y"
    return expr

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = limpiar_expr(data.get("expr", ""))
    orden = data.get("orden", [])
    limites = data.get("limites", {})
    tipo = data.get("tipo", "Cartesiana")  # Cartesiana, Cilíndrica, Esférica

    try:
        # Definir símbolos
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        is_cil = tipo == "Cilíndrica"
        is_esp = tipo == "Esférica"

        # Integración según el orden
        for var in orden:
            v = symbols(var)
            if var in limites:
                a, b = limpiar_expr(limites[var][0]), limpiar_expr(limites[var][1])
                expr_aux = current

                # Aplicar jacobiano según tipo
                if is_cil and var == "r":
                    expr_aux *= r
                if is_esp and var == "r":
                    expr_aux *= r**2 * sin(phi)

                # Integrar
                paso = integrate(expr_aux, (v, sympify(a), sympify(b)))

                # Guardar paso en formato LaTeX limpio
                paso_latex = f"\\int_{{{latex(sympify(a))}}}^{{{latex(sympify(b))}}} {latex(expr_aux)} \\, d{latex(v)} = {latex(paso)}"
                pasos.append(paso_latex)

                # Actualizar "current"
                current = paso

        try:
            resultado_decimal = float(N(current))
        except:
            resultado_decimal = str(N(current))

        return jsonify({
            "resultado": latex(current),            # <-- siempre LaTeX
            "resultado_decimal": resultado_decimal,
            "pasos": pasos                          # <-- lista de pasos en LaTeX limpio
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

