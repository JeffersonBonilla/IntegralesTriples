from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, SympifyError, pi, sqrt
import sympy as sp

app = Flask(__name__)

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '').replace('\\pi', 'pi').replace('\\theta', 'theta')  # Limpiar LaTeX para SymPy
        x1_str = data.get('x1', '0')
        x2_str = data.get('x2', '1')
        y1_str = data.get('y1', '0')
        y2_str = data.get('y2', '1')
        z1_str = data.get('z1', '0')
        z2_str = data.get('z2', '1')
        order = data.get('order', 'dydx').lower()
        is_triple = data.get('is_triple', False)

        # Define symbols (ajusta según función, ej. polar)
        if any(s in function_str for s in ['r', 'theta', 'phi']):
            x, y, z = symbols('r theta phi')
        else:
            x, y, z = symbols('x y z')

        # Parse function con locals para pi, sqrt, etc.
        locals_dict = {'x': x, 'y': y, 'z': z, 'pi': pi, 'sqrt': sqrt, 'theta': symbols('theta'), 'phi': symbols('phi'), 'r': symbols('r')}
        f = sp.sympify(function_str, locals=locals_dict)

        # Parse limits
        def parse_limit(limit_str, var):
            try:
                return sp.sympify(limit_str, locals={**locals_dict, var.name: var})
            except SympifyError:
                return sp.sympify('0')  # Default

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
                # Triple: ∫ dx ∫ dy ∫ dz f
                steps.append("Paso 1: Integral original: $$\\iiint f(x,y,z) \\, dz \\, dy \\, dx$$ con límites z: {z1} a {z2}, y: {y1} a {y2}, x: {x1} a {x2}.".format(
                    z1=latex(z1), z2=latex(z2), y1=latex(y1), y2=latex(y2), x1=latex(x1), x2=latex(x2)))
                
                inner = integrate(f, (z, z1, z2))
                steps.append("Paso 2: Integrar respecto a z (interna): $$\\int_{{ {z1} }}^{{ {z2} }} {f} \\, dz = {inner}$$".format(
                    z1=latex(z1), z2=latex(z2), f=latex(f), inner=latex(inner)))
                
                mid = integrate(inner, (y, y1, y2))
                steps.append("Paso 3: Integrar respecto a y (intermedia): $$\\int_{{ {y1} }}^{{ {y2} }} {inner} \\, dy = {mid}$$".format(
                    y1=latex(y1), y2=latex(y2), inner=latex(inner), mid=latex(mid)))
                
                result = integrate(mid, (x, x1, x2))
                steps.append("Paso 4: Integrar respecto a x (externa): $$\\int_{{ {x1} }}^{{ {x2} }} {mid} \\, dx = {result}$$".format(
                    x1=latex(x1), x2=latex(x2), mid=latex(mid), result=latex(result)))
            else:
                raise ValueError("Orden no soportada para triple: usa 'dzdydx'")
        else:
            # Double
            if 'dydx' in order:
                steps.append("Paso 1: Integral original: $$\\iint f(x,y) \\, dy \\, dx$$ con límites y: {y1} a {y2}, x: {x1} a {x2}.".format(
                    y1=latex(y1), y2=latex(y2), x1=latex(x1), x2=latex(x2)))
                
                inner = integrate(f, (y, y1, y2))
                steps.append("Paso 2: Integrar respecto a y (interna): $$\\int_{{ {y1} }}^{{ {y2} }} {f} \\, dy = {inner}$$".format(
                    y1=latex(y1), y2=latex(y2), f=latex(f), inner=latex(inner)))
                
                result = integrate(inner, (x, x1, x2))
                steps.append("Paso 3: Integrar respecto a x (externa): $$\\int_{{ {x1} }}^{{ {x2} }} {inner} \\, dx = {result}$$".format(
                    x1=latex(x1), x2=latex(x2), inner=latex(inner), result=latex(result)))
            else:
                raise ValueError("Orden no soportada para double: usa 'dydx'")

        # Formatear steps como HTML listo para MathJax (un string con <p> y $$)
        steps_html = "<div style='margin-bottom: 20px;'>" + "</div><div style='margin-bottom: 20px;'>".join(steps) + "</div>"
        final_result = "$$ " + latex(result) + " $$" if result is not None else "$$ \\text{No se pudo calcular} $$"

        return jsonify({
            "result": final_result,
            "steps": steps_html  # Ahora es HTML con LaTeX embebido
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

