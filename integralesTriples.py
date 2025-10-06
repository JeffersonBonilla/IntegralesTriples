from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, SympifyError, pi, sqrt
import sympy as sp

app = Flask(__name__)

def generar_paso_integral(f, var, lower, upper, paso_num):
    F = integrate(f, var)
    F_upper = F.subs(var, upper)
    F_lower = F.subs(var, lower)
    resultado = sp.simplify(F_upper - F_lower)

    html = f"""
    <div>
        <p><strong>Paso {paso_num}a:</strong> $$\\int_{{{latex(lower)}}}^{{{latex(upper)}}} {latex(f)} \\, d{var}$$</p>
        <p><strong>Paso {paso_num}b:</strong> Antiderivada: $$ {latex(F)} $$</p>
        <p><strong>Paso {paso_num}c:</strong> Evaluando: $$[{latex(F)}]_{{{latex(lower)}}}^{{{latex(upper)}}} = {latex(resultado)}$$</p>
    </div>
    """
    return html, resultado

@app.route('/integral', methods=['POST'])
def calcular_integral():
    try:
        data = request.json
        function_str = data.get('function', '').replace('\\pi','pi').replace('\\theta','theta').replace('\\phi','phi')
        order = data.get('order', 'dydx').lower()
        limites = {
            'x': (data.get('x1','0'), data.get('x2','1')),
            'y': (data.get('y1','0'), data.get('y2','1')),
            'z': (data.get('z1','0'), data.get('z2','1')),
            'r': (data.get('r1','0'), data.get('r2','1')),
            'theta': (data.get('theta1','0'), data.get('theta2','pi')),
            'phi': (data.get('phi1','0'), data.get('phi2','pi'))
        }

        # símbolos
        x,y,z,r,theta,phi = symbols('x y z r theta phi')
        locals_dict = {s.name: s for s in [x,y,z,r,theta,phi]}
        locals_dict.update({'pi': pi, 'sqrt': sqrt})

        f = sp.sympify(function_str, locals=locals_dict)

        # parsear el orden: ej. "dzdrdtheta" -> ['dz','dr','dtheta']
        orden_vars = [order[i+1:] if order[i]=='d' else None for i in range(0,len(order), order.find('d',1)-0)]
        orden_vars = [s.replace("d","") for s in order.split("d") if s]  # más simple

        steps = []
        result = f
        paso = 1

        for varname in orden_vars:
            var = locals_dict[varname]
            low_str, up_str = limites[varname]
            lower = sp.sympify(low_str, locals=locals_dict)
            upper = sp.sympify(up_str, locals=locals_dict)

            html, result = generar_paso_integral(result, var, lower, upper, paso)
            steps.append(html)
            paso += 1

        steps_html = "<h2>Desglose Detallado</h2>" + "".join(steps)
        final_result = "$$ " + latex(sp.simplify(result)) + " $$"

        return jsonify({
            "result": final_result,
            "steps": steps_html
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
