from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales funcionando Papi"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr")      # función como string, ej: "x*y + z"
    x1 = data.get("x1")
    x2 = data.get("x2")
    y1 = data.get("y1")
    y2 = data.get("y2")
    z1 = data.get("z1")
    z2 = data.get("z2")

    try:
        # Crear símbolos según los datos recibidos
        variables = {}
        if x1 and x2:
            variables['x'] = symbols('x')
        if y1 and y2:
            variables['y'] = symbols('y')
        if z1 and z2:
            variables['z'] = symbols('z')

        expr = sympify(expr_str)  # Convertir string a expresión Sympy

        # Integración paso a paso según límites disponibles
        result = expr
        pasos = []

        if 'z' in variables:
            result = integrate(result, (variables['z'], float(z1), float(z2)))
            pasos.append(f"Integrando respecto a z: {latex(result)}")
        if 'y' in variables:
            result = integrate(result, (variables['y'], float(y1), float(y2)))
            pasos.append(f"Integrando respecto a y: {latex(result)}")
        if 'x' in variables:
            result = integrate(result, (variables['x'], float(x1), float(x2)))
            pasos.append(f"Integrando respecto a x: {latex(result)}")

        return jsonify({
            "resultado": str(result),
            "latex": latex(result),
            "pasos": pasos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



