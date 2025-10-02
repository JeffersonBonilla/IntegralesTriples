from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales Triples funcionando 🚀"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr", "")
    x1, x2 = data.get("x1"), data.get("x2")
    y1, y2 = data.get("y1"), data.get("y2")
    z1, z2 = data.get("z1"), data.get("z2")

    try:
        # Definir variables según los límites recibidos
        variables = {}
        if x1 and x2: variables['x'] = symbols('x')
        if y1 and y2: variables['y'] = symbols('y')
        if z1 and z2: variables['z'] = symbols('z')

        # Convertir la expresión recibida en objeto sympy
        expr = sympify(expr_str)
        pasos = []
        current_expr = expr

        # Integración respecto a z
        if 'z' in variables:
            paso = integrate(current_expr, (variables['z'], float(z1), float(z2)))
            pasos.append(
                f"\\textbf{{Integrando respecto a z:}} \\\\ "
                f"$\\int_{{{z1}}}^{{{z2}}} {latex(current_expr)} \\, dz = {latex(paso)}$"
            )
            current_expr = paso

        # Integración respecto a y
        if 'y' in variables:
            paso = integrate(current_expr, (variables['y'], float(y1), float(y2)))
            pasos.append(
                f"\\textbf{{Integrando respecto a y:}} \\\\ "
                f"$\\int_{{{y1}}}^{{{y2}}} {latex(current_expr)} \\, dy = {latex(paso)}$"
            )
            current_expr = paso

        # Integración respecto a x
        if 'x' in variables:
            paso = integrate(current_expr, (variables['x'], float(x1), float(x2)))
            pasos.append(
                f"\\textbf{{Integrando respecto a x:}} \\\\ "
                f"$\\int_{{{x1}}}^{{{x2}}} {latex(current_expr)} \\, dx = {latex(paso)}$"
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


