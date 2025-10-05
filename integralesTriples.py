from flask import Flask, request, jsonify
import sympy as sp
from sympy import integrate, symbols, latex

app = Flask(__name__)

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data['function']  # e.g., "x*y"
        x1, x2 = data['x1'], data['x2']  # strings, e.g., "0", "1"
        y1, y2 = data['y1'], data['y2']
        z1, z2 = data['z1'], data['z2']  # Ignored if not triple
        order = data['order'].lower()    # e.g., "dydx" or "dzdydx"
        is_triple = data['is_triple']

        # Define symbols
        x, y, z = symbols('x y z')

        # Parse function
        f = sp.sympify(function_str)

        steps = []
        result = None

        if not is_triple:
            # Double integral
            if order == "dydx":
                inner = integrate(f, (y, sp.sympify(y1), sp.sympify(y2)))
                steps.append(latex(sp.Integral(f, (y, y1, y2))) + " (inner)")
                final = integrate(inner, (x, sp.sympify(x1), sp.sympify(x2)))
                steps.append(latex(inner) + " (after dy)")
                result = latex(final)
            elif order == "dxdy":
                inner = integrate(f, (x, sp.sympify(x1), sp.sympify(x2)))
                steps.append(latex(sp.Integral(f, (x, x1, x2))) + " (inner)")
                final = integrate(inner, (y, sp.sympify(y1), sp.sympify(y2)))
                steps.append(latex(inner) + " (after dx)")
                result = latex(final)
            else:
                return jsonify({"error": "Orden no soportada para doble (usa dydx o dxdy)"}), 400
        else:
            # Triple integral (extend for more orders)
            if order == "dzdydx":
                inner_z = integrate(f, (z, sp.sympify(z1), sp.sympify(z2)))
                steps.append(latex(sp.Integral(f, (z, z1, z2))) + " (inner dz)")
                inner_y = integrate(inner_z, (y, sp.sympify(y1), sp.sympify(y2)))
                steps.append(latex(inner_z) + " (after dz), then " + latex(sp.Integral(inner_z, (y, y1, y2))))
                final = integrate(inner_y, (x, sp.sympify(x1), sp.sympify(x2)))
                steps.append(latex(inner_y) + " (after dy)")
                result = latex(final)
            # Add more orders like "dxdydz" as needed
            else:
                return jsonify({"error": "Orden no soportada para triple (usa dzdydx)"}), 400

        steps.append("Resultado: " + result)  # Last step is result

        return jsonify({
            "steps": steps,
            "result": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
