from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, SympifyError, pi, sqrt, degree
import sympy as sp

app = Flask(__name__)

def generar_explicacion(f, var, var_latex):
    """Explicación textual simple para la integral, con símbolos LaTeX."""
    if f.is_constant(var):
        return "Esta es una constante respecto a {}. La integral es {} \\cdot {} + C.".format(var_latex, latex(f), var_latex)
    elif degree(f, var) > 0:
        return "Usa la regla de potencia para cada término: \\\\int {}^n d{} = \\\\frac{{ {}^{{n+1}} }}{{n+1}} + C.".format(var_latex, var_latex, var_latex)
    elif f.has(sp.sin) or f.has(sp.cos):
        return "Usa reglas de integración trigonométrica (ej. \\\\int \\\\sin u du = -\\\\cos u + C)."
    else:
        return "Antiderivada simbólica de {} respecto a {}.".format(latex(f), var_latex)

def generar_paso_integral(f, var, lower, upper, paso_num, var_latex):
    """Genera HTML detallado para un paso de integración, con símbolos LaTeX."""
    try:
        F = integrate(f, var)
        explicacion = generar_explicacion(f, var, var_latex)
        
        F_upper = F.subs(var, upper)
        F_lower = F.subs(var, lower)
        resultado = sp.simplify(F_upper - F_lower)
        
        # Construir LaTeX en partes para evitar desbalanceo en .format()
        int_definida = r"\\int_{" + latex(lower) + r"}^{" + latex(upper) + r"} " + latex(f) + r" \, d" + var_latex
        antiderivada = r"\\int " + latex(f) + r" \, d" + var_latex + r" = " + latex(F) + r" + C"
        evaluacion = r"[" + latex(F) + r"]_{" + latex(lower) + r"}^{" + latex(upper) + r"} = " + latex(F_upper) + r" - " + latex(F_lower) + r" = " + latex(resultado)
        simplificado = latex(resultado)
        
        html = """
        <div style="margin-bottom: 20px; padding: 15px; background: #1A1A1A; border-left: 3px solid #4CAF50; border-radius: 5px;">
            <p><strong>Subpaso {0}a:</strong> La integral definida es $$ {1} $$</p>
            <p><strong>Subpaso {0}b:</strong> {2} La antiderivada indefinida es $$ {3} $$.</p>
            <p><strong>Subpaso {0}c:</strong> Evaluación en límites: $$ {4} $$</p>
            <p><strong>Subpaso {0}d:</strong> Resultado simplificado: $$ {5} $$</p>
        </div>
        """.format(
            paso_num, int_definida, explicacion, antiderivada, evaluacion, simplificado
        )
        return html, resultado
    except Exception as e:
        return "<p>Error en integración: {}</p>".format(str(e)), f

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '').replace('\\pi', 'pi').replace('\\theta', 'theta').replace('\\phi', 'phi').replace('\\sqrt', 'sqrt')
        order = data.get('order', 'dydx').lower().strip()
        is_triple = data.get('is_triple', False)

        # Obtener límites como strings
        x1_str = data.get('x1', '0')
        x2_str = data.get('x2', '1')
        y1_str = data.get('y1', '0')
        y2_str = data.get('y2', '1')
        z1_str = data.get('z1', '0')
        z2_str = data.get('z2', '1')

        # Símbolos
        x, y, z, r, theta, phi = symbols('x y z r theta phi')
        locals_dict = {'x': x, 'y': y, 'z': z, 'r': r, 'theta': theta, 'phi': phi, 'pi': pi, 'sqrt': sqrt}

        # Mapeo para LaTeX de variables
        var_latex_map = {'x': 'x', 'y': 'y', 'z': 'z', 'r': 'r', 'theta': r'\theta', 'phi': r'\phi'}

        # Parsear función
        f = sp.sympify(function_str, locals=locals_dict)

        # Extraer variables del orden (ej. "dzdrdtheta" → ['z', 'r', 'theta'])
        if not order.startswith('d'):
            order = 'd' + order
        orden_vars = [s for s in order.split('d')[1:] if s]

        # Validar número de vars
        expected_vars = 3 if is_triple else 2
        if len(orden_vars) != expected_vars:
            raise ValueError("Orden inválido: espera {} variables para {} (ej. 'dzdydx' o 'dydx'). Encontradas: {}".format(expected_vars, 'triple' if is_triple else 'doble', orden_vars))

        # Mapeo de var a límites (X= x/θ, Y= y/r, Z= z/φ)
        var_to_limites = {
            'x': (x1_str, x2_str), 'theta': (x1_str, x2_str),
            'y': (y1_str, y2_str), 'r': (y1_str, y2_str),
            'z': (z1_str, z2_str), 'phi': (z1_str, z2_str)
        }

        # Parsear límites
        limites_parsed = {}
        for varname in orden_vars:
            if varname not in var_to_limites:
                raise ValueError("Variable no soportada: {}. Usa x,y,z,r,theta,phi.".format(varname))
            low_str, up_str = var_to_limites[varname]
            lower = sp.sympify(low_str, locals=locals_dict)
            upper = sp.sympify(up_str, locals=locals_dict)
            limites_parsed[varname] = (lower, upper)

        # Generar LaTeX del ejercicio (externa a interna, limpia)
        orden_display = orden_vars[::-1]  # Externa primero
        integrals_parts = []
        for varname in orden_display:
            var_latex = var_latex_map[varname]
            lower, upper = limites_parsed[varname]
            # Construir en partes para evitar desbalanceo
            int_part = r"\\int_{" + var_latex + r" = " + latex(lower) + r"}^{" + latex(upper) + r"}"
            integrals_parts.append(int_part)
        diff_parts = [r"d" + var_latex_map[v] for v in orden_vars]
        integral_latex = " ".join(integrals_parts) + " " + latex(f) + r" \, " + " \, ".join(diff_parts)

        # Sección Ejercicio Propuesto
        tipo = "triple" if is_triple else "doble"
        ejercicio_html = """
        <div style="text-align: center; background: #2A2A2A; padding: 20px; margin-bottom: 30px; border-radius: 10px; border: 2px solid #4CAF50;">
            <h3 style="color: #4CAF50; margin-bottom: 10px;">Ejercicio Propuesto</h3>
            <p style="margin-bottom: 15px; font-size: 16px;">Resuelve la siguiente integral {}:</p>
            <div class="math">$$ {} $$</div>
        </div>
        """.format(tipo, integral_latex)

        steps = [ejercicio_html]
        result = f
        paso = 1

        # Pasos de integración
        for varname in orden_vars:
            var = locals_dict[varname]
            lower, upper = limites_parsed[varname]
            var_latex = var_latex_map[varname]
            html, result = generar_paso_integral(result, var, lower, upper, paso, var_latex)
            step_header = "<p><strong>Paso {} (integración respecto a {}):</strong></p>".format(paso, var_latex)
            steps.append(step_header + html)
            paso += 1

        steps_html = "<h2>Desglose Detallado Paso a Paso</h2>" + "".join(steps)
        final_result = "$$ " + latex(sp.simplify(result)) + " $$"

        return jsonify({
            "result": final_result,
            "steps": steps_html
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


