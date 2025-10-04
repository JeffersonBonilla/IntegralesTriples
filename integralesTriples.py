from flask import Flask, request, jsonify
from sympy import symbols, sympify, integrate, latex
import traceback

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def calcular_integral():
    data = request.json or {}
    debug_info = {"recibido": data, "error": None}

    try:
        # Función
        funcion = str(data.get("funcion", "")).replace("π", "pi").replace("√", "sqrt").strip()
        orden = str(data.get("orden", "")).strip()

        x, y, z = symbols('x y z')

        # Limites seguros
        def safe_sympify(value, default=0):
            if value is None or value == "":
                return default
            return sympify(str(value).replace(",", ".").strip())

        x1 = safe_sympify(data.get("x1"))
        x2 = safe_sympify(data.get("x2"))
        y1 = safe_sympify(data.get("y1"))
        y2 = safe_sympify(data.get("y2"))
        z1 = safe_sympify(data.get("z1")) if "z1" in data else None
        z2 = safe_sympify(data.get("z2")) if "z2" in data else None

        expr = sympify(funcion)

        pasos = []

        # Integral doble
        if z1 is None or z2 is None:
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

        debug_info["resultado"] = str(resultado)
        debug_info["pasos"] = pasos

        return jsonify(debug_info)

    except Exception as e:
        debug_info["error"] = traceback.format_exc()
        return jsonify(debug_info), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



