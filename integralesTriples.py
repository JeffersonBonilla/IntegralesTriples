from flask import Flask, request, jsonify
from sympy import symbols, sympify, integrate, latex

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def calcular_integral():
    try:
        data = request.json
        funcion = data.get("funcion", "")
        orden = data.get("orden", "")
        x1 = sympify(data.get("x1", "0"))
        x2 = sympify(data.get("x2", "0"))
        y1 = sympify(data.get("y1", "0"))
        y2 = sympify(data.get("y2", "0"))
        z1 = data.get("z1", None)
        z2 = data.get("z2", None)

        x, y, z = symbols('x y z')
        expr = sympify(funcion.replace("π","pi").replace("√","sqrt"))

        pasos = []

        # Integral doble
        if z1 is None:
            # Paso 1: integral original
            pasos.append(latex(integrate(expr, (y, y1, y2), (x, x1, x2), evaluate=False)))

            # Paso 2: integrar respecto a y
            int_y = integrate(expr, (y, y1, y2), evaluate=False)
            pasos.append(latex(int_y))

            # Paso 3: evaluar límites de y
            int_y_eval = integrate(expr, (y, y1, y2))
            pasos.append(latex(int_y_eval))

            # Paso 4: integrar respecto a x (resultado final)
            resultado = int_y_eval.evalf()
        else:
            # Integral triple (similar, paso a paso)
            z1 = sympify(z1)
            z2 = sympify(z2)
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




