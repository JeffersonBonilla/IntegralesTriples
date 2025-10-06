from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, sqrt, pi
import sympy as sp

app = Flask(__name__)

# Para mostrar variables bonitas en LaTeX
def simbolo(varname):
    return {"theta": "\\theta", "phi": "\\varphi"}.get(varname, varname)

def generar_paso_integral(f, var, lower, upper, paso_num):
    """Paso de integración mostrando constantes explícitas frente a la integral."""
    try:
        # Separar factores constantes respecto a var
        f_const, f_var = f.as_independent(var, as_Add=False)

        # Integral definida de la parte variable
        F_var_def = integrate(f_var, (var, lower, upper))
        resultado = sp.simplify(f_const * F_var_def)

        html = f"""
        <div style="margin-bottom: 20px; padding: 15px; background: #1A1A1A; border-left: 3px solid #4CAF50; border-radius: 5px;">
            <p><strong>Subpaso {paso_num}a:</strong> La integral definida es $$\\int_{{{latex(lower)}}}^{{{latex(upper)}}} {latex(f)} \\, d{simbolo(var.name)}$$</p>
            <p><strong>Subpaso {paso_num}b:</strong> Factorizamos las constantes respecto a {simbolo(var.name)}: $$ {latex(f)} = {latex(f_const)} \\cdot {latex(f_var)} $$</p>
            <p><strong>Subpaso {paso_num}c:</strong> Integral de la parte variable: $$\\int_{{{latex(lower)}}}^{{{latex(upper)}}} {latex(f_var)} \\, d{simbolo(var.name)} = {latex(F_var_def)}$$</p>
            <p><strong>Subpaso {paso_num}d:</strong> Multiplicamos por la constante: $$ {latex(f_const)} \\cdot {latex(F_var_def)} = {latex(resultado)} $$</p>
        </div>
        """
        return html, resultado
    except Exception as e:
        return f"<p>Error en integración: {str(e)}</p>", f

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '').replace('\\pi', 'pi').replace('\\theta', 'theta').replace('\\phi', 'phi').replace('\\sqrt', 'sqrt')
        order = data.get('order', 'dydx').lower().strip()
        is_triple = data.get('is_triple', False)

        # Símbolos
        x, y, z, r, theta, phi = symbols('x y z r theta phi')
        locals_dict = {'x': x, 'y': y, 'z': z, 'r': r, 'theta': theta, 'phi': phi, 'pi': pi, 'sqrt': sqrt}

        # Parsear función
        f = sympify(function_str, locals=locals_dict)

        # Extraer variables del orden ingresado
        if not order.startswith('d'):
            order = 'd' + order
        orden_vars = [s for s in order.split('d')[1:] if s]

        expected_vars = 3 if is_triple else 2
        if len(orden_vars) != expected_vars:
            raise ValueError(f"Orden inválido: espera {expected_vars} variables para {'triple' if is_triple else 'doble'} integral. Encontradas: {orden_vars}")

        # Límites recibidos
        limites_input = {
            'x': (data.get('x1','0'), data.get('x2','1')),
            'y': (data.get('y1','0'), data.get('y2','1')),
            'z': (data.get('z1','0'), data.get('z2','1')),
            'r': (data.get('y1','0'), data.get('y2','1')),
            'theta': (data.get('x1','0'), data.get('x2','1')),
            'phi': (data.get('z1','0'), data.get('z2','1'))
        }

        # Parsear límites
        limites_parsed = {}
        for varname in orden_vars:
            low_str, up_str = limites_input[varname]
            lower = sympify(low_str, locals=locals_dict)
            upper = sympify(up_str, locals=locals_dict)
            limites_parsed[varname] = (lower, upper)

        # Integral original en LaTeX según orden del usuario
        integrals = []
        for varname in orden_vars:
            lower, upper = limites_parsed[varname]
            integrals.append(f"\\int_{{{latex(lower)}}}^{{{latex(upper)}}}")
        integral_latex = " ".join(integrals) + f" {latex(f)} \\, " + " \\, ".join([f"d{simbolo(varname)}" for varname in orden_vars])
        tipo_integral = "\\iiint" if is_triple else "\\iint"
        integral_original = f"{tipo_integral} {integral_latex}"

        # Ejercicio propuesto
        tipo = "triple" if is_triple else "doble"
        ejercicio_html = f"""
        <div style="text-align: center; background: #2A2A2A; padding: 20px; margin-bottom: 30px; border-radius: 10px; border: 2px solid #4CAF50;">
            <h3 style="color: #4CAF50; margin-bottom: 10px;">Ejercicio Propuesto</h3>
            <p style="margin-bottom: 15px; font-size: 16px;">Resuelve la siguiente integral {tipo}:</p>
            <div class="math">$$ {integral_original} $$</div>
        </div>
        """

        # Pasos detallados
        steps = [ejercicio_html]
        result = f
        paso = 1
        for varname in orden_vars:
            var = locals_dict[varname]
            lower, upper = limites_parsed[varname]
            html, result = generar_paso_integral(result, var, lower, upper, paso)
            steps.append(f"<p><strong>Paso {paso} (integración respecto a {simbolo(varname)}):</strong></p>" + html)
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


