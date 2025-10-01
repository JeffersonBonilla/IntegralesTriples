from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr")
    x1, x2 = data.get("x1"), data.get("x2")
    y1, y2 = data.get("y1"), data.get("y2")
    z1, z2 = data.get("z1"), data.get("z2")

    try:
        variables = {}
        if x1 and x2: variables['x'] = symbols('x')
        if y1 and y2: variables['y'] = symbols('y')
        if z1 and z2: variables['z'] = symbols('z')

        expr = sympify(expr_str)
        pasos = []
        current_expr = expr

        # Integración paso a paso
        if 'z' in variables:
            paso = integrate(current_expr, (variables['z'], float(z1), float(z2)))
            pasos.append(f"\\textbf{{1. Integrando respecto a z:}} \\\\ $\\int_{{{z1}}}^{{{z2}}} {latex(current_expr)} \\, dz = {latex(paso)}$")
            current_expr = paso
        if 'y' in variables:
            paso = integrate(current_expr, (variables['y'], float(y1), float(y2)))
            pasos.append(f"\\textbf{{2. Integrando respecto a y:}} \\\\ $\\int_{{{y1}}}^{{{y2}}} {latex(current_expr)} \\, dy = {latex(paso)}$")
            current_expr = paso
        if 'x' in variables:
            paso = integrate(current_expr, (variables['x'], float(x1), float(x2)))
            pasos.append(f"\\textbf{{3. Integrando respecto a x:}} \\\\ $\\int_{{{x1}}}^{{{x2}}} {latex(current_expr)} \\, dx = {latex(paso)}$")
            current_expr = paso

        return jsonify({
            "resultado": str(current_expr),
            "latex": latex(current_expr),
            "pasos": pasos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400




