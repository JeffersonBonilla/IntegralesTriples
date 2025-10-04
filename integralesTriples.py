from flask import Flask, request, jsonify
from sympy import symbols, sympify, integrate, pi

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def calcular_integral():
    try:
        data = request.json

        # Datos recibidos
        funcion = data.get("funcion", "")
        orden = data.get("orden", "")
        x1 = sympify(data.get("x1", "0"))
        x2 = sympify(data.get("x2", "0"))
        y1 = sympify(data.get("y1", "0"))
        y2 = sympify(data.get("y2", "0"))
        z1 = data.get("z1", None)
        z2 = data.get("z2", None)

        # Variables
        x, y, z, r, theta, phi = symbols('x y z r theta phi')

        # Reemplazar caracteres especiales
        funcion = funcion.replace("π", "pi")
        funcion = funcion.replace("θ", "theta")
        funcion = funcion.replace("φ", "phi")
        funcion = funcion.replace("√", "sqrt")

        expr = sympify(funcion)

        # Integración
        if z1 is not None and z2 is not None:  # Integral triple
            z1 = sympify(z1)
            z2 = sympify(z2)
            # Orden de integración según string
            if orden == "dzdydx":
                integral = integrate(expr, (z, z1, z2), (y, y1, y2), (x, x1, x2))
            elif orden == "dzdxdy":
                integral = integrate(expr, (z, z1, z2), (x, x1, x2), (y, y1, y2))
            else:
                return jsonify({"error": "Orden no soportado"}), 400
        else:  # Integral doble
            if orden == "dydx":
                integral = integrate(expr, (y, y1, y2), (x, x1, x2))
            elif orden == "dxdy":
                integral = integrate(expr, (x, x1, x2), (y, y1, y2))
            else:
                return jsonify({"error": "Orden no soportado"}), 400

        # Respuesta
        return jsonify({
            "resultado": str(integral.evalf()),
            "latex": str(integral)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





