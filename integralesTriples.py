from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, SympifyError
import sympy as sp

app = Flask(__name__)

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '')
        x1_str = data.get('x1', '0')
        x2_str = data.get('x2', '1')
        y1_str = data.get('y1', '0')
        y2_str = data.get('y2', '1')
        z1_str = data.get('z1', '0')
        z2_str = data.get('z2', '1')
        order = data.get('order', 'dydx').lower()
        is_triple = data.get('is_triple', False)

        # Define symbols based on order (e.g., x, y, z or r, theta, phi)
        if 'r' in function_str or 'θ' in function_str:
            x, y, z = symbols('r theta phi')  # Polar/spherical example
        else:
            x, y, z = symbols('x y z')

        # Parse function
        f = sp.sympify(function_str, locals={'x': x, 'y': y, 'z': z, 'pi': sp.pi, 'sqrt': sp.sqrt})

        # Parse limits
        def parse_limit(limit_str, var):
            try:
                return sp.sympify(limit_str, locals={var.name: var, 'pi': sp.pi, 'sqrt': sp.sqrt})
            except SympifyError:
                return 0  # Default on error

        x1 = parse_limit(x1_str, x)
        x2 = parse_limit(x2_str, x)
        y1 = parse_limit(y1_str, y)
        y2 = parse_limit(y2_str, y)
        z1 = parse_limit(z1_str, z)
        z2 = parse_limit(z2_str, z)

        steps = []
        result = None

        if is_triple:
            if 'dzdydx' in order:
                # ∫∫∫ f dz dy dx
                inner = integrate(f, (z, z1, z2))
                steps.append(latex(sp.Integral(f, (z, z1, z2))))
                mid = integrate(inner, (y, y1, y2))
                steps.append(latex(sp.Integral(inner, (y, y1, y2))))
                result = integrate(mid, (x, x1, x2))
                steps.append(latex(sp.Integral(mid, (x, x1, x2))))
            # Add other orders (dzdxdy, etc.) similarly if needed
        else:
            # Double integral
            if 'dydx' in order:
                inner = integrate(f, (y, y1, y2))
                steps.append(latex(sp.Integral(f, (y, y1, y2))))
                result = integrate(inner, (x, x1, x2))
                steps.append(latex(sp.Integral(inner, (x, x1, x2))))
            # Add dxdy if needed

        # Format steps as HTML with LaTeX
        steps_latex = "\\[ " + " \\\\ ".join(steps) + " \\] \\\\ Resultado: \\[ " + latex(result) + " \\]"
        final_result = f"$$ {latex(result)} $$" if result else "No se pudo calcular"

        return jsonify({
            "result": final_result,
            "steps": steps_latex
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



