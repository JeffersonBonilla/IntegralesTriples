from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, pi, sqrt, degree
import sympy as sp

app = Flask(__name__)

def simbolo(varname):
    return {"theta": "\\theta", "phi": "\\varphi"}.get(varname, varname)

def generar_explicacion(f, var):
    if f.is_constant(var):
        return f"Es constante respecto a {simbolo(var.name)}. Entonces $$\\int {latex(f)} \\, d{simbolo(var.name)} = {latex(f)}{simbolo(var.name)} + C$$"
    elif degree(f, var) > 0:
        return f"Usa la regla de potencia: $$\\int {simbolo(var.name)}^n \\, d{simbolo(var.name)} = \\frac{{{simbolo(var.name)}^{{n+1}}}}{{n+1}} + C$$"
    elif f.has(sp.sin) or f.has(sp.cos):
        return "Usa reglas trigonométricas, por ejemplo: $$\\int \\sin u \\, du = -\\cos u + C$$"
    else:
        return f"Antiderivada simbólica de $$ {latex(f)} $$ respecto a {simbolo(var.name)}."

def generar_paso_integral(f, var, lower, upper, paso_num):
    """Genera paso mostrando antiderivada indefinida y resultado de integral definida
       Maneja constantes respecto a la variable de integración para evitar errores."""
    try:
        # Separar parte constante y parte que depende de var
        f_const, f_var = f.as_independent(var, as_Add=False)
        
        # Antiderivada indefinida segura
        F_indef = integrate(f_var, var) * f_const

        # Integral definida directa (maneja constantes automáticamente)
        resultado = integrate(f, (var, lower, upper))

        explicacion = generar_explicacion(f, var)

        html = f"""
        <div style="margin-bottom: 20px; padding: 15px; background: #1A1A1A; border-left: 3px solid #4CAF50; border-radius: 5px;">
            <p><strong>Subpaso {paso_num}a:</strong> La integral definida es $$\\int_{{{latex(lower)}}}^{{{latex(upper)}}} {latex(f)} \\, d{simbolo(var.name)}$$</p>
            <p><strong>Subpaso {paso_num}b:</strong> {explicacion}. La antiderivada indefinida es $$\\int {latex(f)} \\, d{simbolo(var.name)} = {latex(F_indef)} + C$$</p>
            <p><strong>Subpaso {paso_num}c:</strong> Evaluación directa de la integral definida: $$ {latex(resultado)} $$</p>
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

        # Límites recibidos
        x1_str = data.get('x1', '0')
        x2_str = data.get('x2', '1')
        y1_str = data.get('y1', '0')
        y2_str = data.get('y2', '1')
        z1_str = data.get('z1', '0')
        z2_str = data.get('z2', '1')

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

        # Asignar límites
        var_to_limites = {
            'x': (x1_str, x2_str),
            'theta': (x1_str, x2_str),
            'y': (y1_str, y2_str),
            'r': (y1_str, y2_str),
            'z': (z1_str, z2_str),
            'phi': (z1_str, z2_str)
        }

        limites_parsed = {}
        for varname in orden_vars:
            low_str, up_str = var_to_limites[varname]
            lower = sympify(low_str, locals=locals_dict)
            upper = sympify(up_str, locals=locals_dict)
            limites_parsed[varname] = (lower, upper)

        # Integral en LaTeX según orden del usuario
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


