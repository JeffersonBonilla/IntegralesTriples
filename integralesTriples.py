from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, SympifyError, pi, sqrt, degree, trigsimp
import sympy as sp

app = Flask(__name__)

def generar_explicacion(f, var, is_indefinida=True):
    """Genera explicación textual simple para la integral de f respecto a var."""
    f_str = latex(f)
    if f.is_polynomial(var):
        deg = degree(f, var)
        if deg == 0:
            return "Esta es una constante respecto a {var}. La integral indefinida es {f} \\cdot {var} + C.".format(var=var.name, f=f_str)
        elif deg == 1:
            return "Usa la regla de potencia: \\int {var}^n d{var} = \\frac{{{var}}^{{n+1}}}{{n+1}} + C. Aplicado término por término.".format(var=var.name)
        else:
            return "Integra cada término polinomial usando la regla de potencia: \\int a {var}^n d{var} = a \\frac{{{var}}^{{n+1}}}{{n+1}} + C."
    elif f.has(sp.sin) or f.has(sp.cos):
        return "Usa identidades trigonométricas básicas o regla de potencia para funciones trig."
    else:
        return "SymPy calcula la antiderivada simbólica de {f} respecto a {var}.".format(f=f_str, var=var.name)
    return "Integral indefinida calculada simbólicamente."

def generar_paso_integral(f, var, lower, upper, paso_num, es_interna=False):
    """Genera HTML detallado para un paso de integración."""
    # Antiderivada indefinida
    F = integrate(f, var)
    explicacion = generar_explicacion(f, var)
    
    # Evaluación
    F_upper = F.subs(var, upper)
    F_lower = F.subs(var, lower)
    resultado = F_upper - F_lower
    
    # Simplificar
    resultado = sp.simplify(resultado)
    
    html = f"""
    <div>
        <p><strong>Subpaso {paso_num}a:</strong> La integral a resolver es $$\\int_{{{latex(lower)}}}^{{{latex(upper)}}} {latex(f)} \\, d{var}$$</p>
        <p><strong>Subpaso {paso_num}b:</strong> {explicacion} La antiderivada indefinida es $$\\int {latex(f)} \\, d{var} = {latex(F)} + C$$.</p>
        <p><strong>Subpaso {paso_num}c:</strong> Evalúa en los límites: $$[{latex(F)}]_{{{latex(lower)}}}^{{{latex(upper)}}} = {latex(F_upper)} - {latex(F_lower)} = {latex(resultado)}$$</p>
        <p><strong>Subpaso {paso_num}d:</strong> Simplificación: {latex(resultado)}</p>
    </div>
    """
    return html, resultado

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '').replace('\\pi', 'pi').replace('\\theta', 'theta').replace('\\sqrt', 'sqrt')  # Limpiar LaTeX
        x1_str = data.get('x1', '0')
        x2_str = data.get('x2', '1')
        y1_str = data.get('y1', '0')
        y2_str = data.get('y2', '1')
        z1_str = data.get('z1', '0')
        z2_str = data.get('z2', '1')
        order = data.get('order', 'dydx').lower()
        is_triple = data.get('is_triple', False)

        # Symbols
        if any(s in function_str.lower() for s in ['r', 'theta', 'phi']):
            x, y, z = symbols('r theta phi')
        else:
            x, y, z = symbols('x y z')

        locals_dict = {'x': x, 'y': y, 'z': z, 'pi': pi, 'sqrt': sqrt, 'theta': symbols('theta'), 'phi': symbols('phi'), 'r': symbols('r')}
        f = sp.sympify(function_str, locals=locals_dict)

        def parse_limit(limit_str, var):
            try:
                return sp.sympify(limit_str, locals={**locals_dict, var.name: var})
            except SympifyError:
                return sp.sympify('0')

        x1 = parse_limit(x1_str, x)
        x2 = parse_limit(x2_str, x)
        y1 = parse_limit(y1_str, y)
        y2 = parse_limit(y2_str, y)
        z1 = parse_limit(z1_str, z)
        z2 = parse_limit(z2_str, z)

        steps = []
        result = None
        paso_contador = 1

        if is_triple:
            if 'dzdydx' in order:
                steps.append(f"<p><strong>Integral Triple Original (Paso {paso_contador}):</strong> $$\\iiint_{{x={latex(x1)}}^{{{latex(x2)}}}}_{{y={latex(y1)}}^{{{latex(y2)}}}}_{{z={latex(z1)}}^{{{latex(z2)}}}} {latex(f)} \\, dz \\, dy \\, dx$$</p>")
                paso_contador += 1

                # Inner: ∫ dz
                inner_html, inner = generar_paso_integral(f, z, z1, z2, paso_contador, es_interna=True)
                steps.append(inner_html)
                paso_contador += 1

                # Mid: ∫ dy de inner
                mid_html, mid = generar_paso_integral(inner, y, y1, y2, paso_contador)
                steps.append(mid_html)
                paso_contador += 1

                # Outer: ∫ dx de mid
                outer_html, result = generar_paso_integral(mid, x, x1, x2, paso_contador)
                steps.append(outer_html)
            else:
                raise ValueError("Orden no soportada para triple: usa 'dzdydx'")
        else:
            # Double
            if 'dydx' in order:
                steps.append(f"<p><strong>Integral Doble Original (Paso {paso_contador}):</strong> $$\\iint_{{x={latex(x1)}}^{{{latex(x2)}}}}_{{y={latex(y1)}}^{{{latex(y2)}}}} {latex(f)} \\, dy \\, dx$$</p>")
                paso_contador += 1

                # Inner: ∫ dy
                inner_html, inner = generar_paso_integral(f, y, y1, y2, paso_contador, es_interna=True)
                steps.append(inner_html)
                paso_contador += 1

                # Outer: ∫ dx de inner
                outer_html, result = generar_paso_integral(inner, x, x1, x2, paso_contador)
                steps.append(outer_html)
            else:
                raise ValueError("Orden no soportada para double: usa 'dydx'")

        # HTML final para steps
        steps_html = "<h2>Desglose Detallado Paso a Paso</h2>" + "".join(steps)
        final_result = "$$ " + latex(sp.simplify(result)) + " $$" if result is not None else "$$ \\text{No se pudo calcular} $$"

        return jsonify({
            "result": final_result,
            "steps": steps_html
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



