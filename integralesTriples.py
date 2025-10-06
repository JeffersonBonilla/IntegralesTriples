from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, SympifyError, pi, sqrt, degree
import sympy as sp

app = Flask(__name__)

def generar_explicacion(f, var, var_latex):
    """Explicación textual simple para la integral, con símbolos LaTeX."""
    var_name = var.name
    if f.is_constant(var):  # Constante respecto a var
        return f"Esta es una constante respecto a {var_latex}. La integral es {latex(f)} \\cdot {var_latex} + C."
    elif degree(f, var) > 0:  # Polinomio
        # Escapar llaves correctamente para LaTeX en f-string
        return f"Usa la regla de potencia para cada término: \\\\int {var_latex}^n d{var_latex} = \\\\frac{{ {var_latex}^{{n+1}} }}{{n+1}} + C."
    elif f.has(sp.sin) or f.has(sp.cos):
        return f"Usa reglas de integración trigonométrica (ej. \\\\int \\\\sin u du = -\\\\cos u + C)."
    else:
        return f"Antiderivada simbólica de {latex(f)} respecto a {var_latex}."

def generar_paso_integral(f, var, lower, upper, paso_num, var_latex):
    """Genera HTML detallado para un paso de integración, con símbolos LaTeX."""
    try:
        F = integrate(f, var)  # Antiderivada indefinida
        explicacion = generar_explicacion(f, var, var_latex)
        
        F_upper = F.subs(var, upper)
        F_lower = F.subs(var, lower)
        resultado = sp.simplify(F_upper - F_lower)
        
        html = f"""
        <div style="margin-bottom: 20px; padding: 15px; background: #1A1A1A; border-left: 3px solid #4CAF50; border-radius: 5px;">
            <p><strong>Subpaso {paso_num}a:</strong> La integral definida es $$\\int_{{{latex(lower)}}}^{{{latex(upper)}}} {latex(f)} \\, d{var_latex}$$</p>
            <p><strong>Subpaso {paso_num}b:</strong> {explicacion} La antiderivada indefinida es $$\\int {latex(f)} \\, d{var_latex} = {latex(F)} + C$$.</p>
            <p><strong>Subpaso {paso_num}c:</strong> Evaluación en límites: $$[{latex(F)}]_{{{latex(lower)}}}^{{{latex(upper)}}} = {latex(F_upper)} - {latex(F_lower)} = {latex(resultado)}$$</p>
            <p><strong>Subpaso {paso_num}d:</strong> Resultado simplificado: $$ {latex(resultado)} $$</p>
        </div>
        """
        return html, resultado
    except Exception as e:
        return f"<p>Error en integración: {str(e)}</p>", f  # Fallback

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '').replace('\\pi', 'pi').replace('\\theta', 'theta').replace('\\phi', 'phi').replace('\\sqrt', 'sqrt')
        order = data.get('order', 'dydx').lower().strip()
        is_triple = data.get('is_triple', False)

        # Obtener límites como strings (del body)
        x1_str = data.get('x1', '0')
        x2_str = data.get('x2', '1')
        y1_str = data.get('y1', '0')
        y2_str = data.get('y2', '1')
        z1_str = data.get('z1', '0')
        z2_str = data.get('z2', '1')

        # Símbolos para coordenadas cartesianas/polares/esféricas
        x, y, z, r, theta, phi = symbols('x y z r theta phi')
        locals_dict = {'x': x, 'y': y, 'z': z, 'r': r, 'theta': theta, 'phi': phi, 'pi': pi, 'sqrt': sqrt}

        # Mapeo para LaTeX de variables (para renderizar símbolos)
        var_latex_map = {
            'x': 'x',
            'y': 'y',
            'z': 'z',
            'r': 'r',
            'theta': '\\theta',
            'phi': '\\phi'
        }

        # Parsear función
        f = sp.sympify(function_str, locals=locals_dict)

        # Extraer variables del orden (ej. "dydx" → ['y', 'x']; "dzdrdtheta" → ['z', 'r', 'theta'])
        if not order.startswith('d'):
            order = 'd' + order  # Asegurar que empiece con 'd'
        orden_vars = [s for s in order.split('d')[1:] if s]  # Split y filtrar vacíos

        # Validar número de vars basado en is_triple
        expected_vars = 3 if is_triple else 2
        if len(orden_vars) != expected_vars:
            raise ValueError(f"Orden inválido: espera {expected_vars} variables para {'triple' if is_triple else 'doble'} (ej. 'dzdydx' o 'dydx'). Encontradas: {orden_vars}")

        # Mapeo de var a límites (basado en hints XML: X= x/θ, Y= y/r, Z= z/φ)
        var_to_limites = {
            'x': (x1_str, x2_str),
            'theta': (x1_str, x2_str),  # θ usa límites X
            'y': (y1_str, y2_str),
            'r': (y1_str, y2_str),     # r usa límites Y
            'z': (z1_str, z2_str),
            'phi': (z1_str, z2_str)    # φ usa límites Z
        }

        # Parsear límites para cada var en orden (interna primero)
        limites_parsed = {}
        for varname in orden_vars:
            if varname not in var_to_limites:
                raise ValueError(f"Variable no soportada en orden: {varname}. Usa x,y,z,r,theta,phi.")
            low_str, up_str = var_to_limites[varname]
            try:
                lower = sp.sympify(low_str, locals=locals_dict)
                upper = sp.sympify(up_str, locals=locals_dict)
                limites_parsed[varname] = (lower, upper)
            except SympifyError:
                raise ValueError(f"Límite inválido para {varname}: '{low_str}' o '{up_str}'. Usa expresiones como 'pi/2' o 'theta'.")

        # Generar LaTeX de la integral original (limpia: externa a interna, sin vacíos)
        # orden_display: externa a interna para límites
        orden_display = orden_vars[::-1]  # Reverso para display (externa primero)
        integrals_parts = []
        for i, varname in enumerate(orden_display):
            var_latex = var_latex_map[varname]
            lower, upper = limites_parsed[varname]
            integrals_parts.append(f"\\int_{{{var_latex} = {latex(lower)}}}^{{{latex(upper)}}}}")
        # Función y diferenciales (diferenciales: interna a externa, que es orden_vars)
        diff_parts = [f"d{var_latex_map[v]}" for v in orden_vars]
        integral_latex = " ".join(integrals_parts) + f" {latex(f)} \\, " + " \\, ".join(diff_parts)

        # Sección "Ejercicio Propuesto" como HTML destacado (sin \iiint extra)
        tipo = "triple" if is_triple else "doble"
        ejercicio_html = f"""
        <div style="text-align: center; background: #2A2A2A; padding: 20px; margin-bottom: 30px; border-radius: 10px; border: 2px solid #4CAF50;">
            <h3 style="color: #4CAF50; margin-bottom: 10px;">Ejercicio Propuesto</h3>
            <p style="margin-bottom: 15px; font-size: 16px;">Resuelve la siguiente integral {tipo}:</p>
            <div class="math">$$ {integral_latex} $$</div>
        </div>
        """

        steps = [ejercicio_html]
        result = f
        paso = 1

        # Agregar pasos de integración (con símbolos LaTeX)
        for varname in orden_vars:
            var = locals_dict[varname]
            lower, upper = limites_parsed[varname]
            var_latex = var_latex_map[varname]
            html, result = generar_paso_integral(result, var, lower, upper, paso, var_latex)
            steps.append(f"<p><strong>Paso {paso} (integración respecto a {var_latex}):</strong></p>" + html)
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
