from flask import Flask, request, jsonify
from sympy import symbols, sympify, integrate, latex

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def calcular_integral():
    try:
        data = request.json

        # Función y reemplazos
        funcion = data.get("funcion", "").replace("π", "pi").replace("√", "sqrt")

        orden = data.get("orden", "")
        x1 = sympify(data.get("x1", "0").replace(",", "."))
        x2 = sympify(data.get("x2", "0").replace(",", "."))
        y1 = sympify(data.get("y1", "0").replace(",", "."))
        y2 = sympify(data.get("y2", "0").replace(",", "."))

        z1 = data.get("z1", None)
        z2 = data.get("z2", None)
        if z1 is not None and z2 is not None and z1 != "" and z2 != "":
            z1 = sympify(z1.replace(",", "."))
            z2 = sympify(z2.replace(",", "."))
        else:
            z1 = z2 = None

        # Variables
        x, y, z = symbols('x y z')
        expr = sympify(funcion)

        pasos = []

        if z1 is None:
            # Integral doble
            pasos.append(latex(integrate(expr, (y, y1, y2), (x, x1, x2), evaluate=False)))
            int_y = integrate(expr, (y, y1, y2), evaluate=False)
            pasos.append(latex(int_y))
            int_y_eval = integrate(expr, (y, y1, y2))
            pasos.append(latex(int_y_eval))
            resultado = int_y_eval.evalf()
        else:
            # Integral triple
            pasos.append(latex(integrate(expr, (z, z1, z2), (y, y1, y2), (x, x1, x2), evaluate=False)))
            int_z = integrate(expr, (z, z1, z2), evaluate=False)
            pasos.append(latex(int_z))
            int_zy = integrate(int_z, (y, y1, y2), evaluate=False)
            pasos.append(latex(int_zy))
            int_zyx = integrate(int_zy, (x, x1, x2))
            pasos.append(latex(int_zyx))
            resultado = int_zyx.evalf()

        return jsonify({
            "resultado": str(resultado),
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


