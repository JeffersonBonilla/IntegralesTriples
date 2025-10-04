from flask import Flask, request, jsonify
from sympy import symbols, sympify, integrate, latex
from sympy.parsing.sympy_parser import parse_expr
import re

app = Flask(__name__)

# Variables posibles
variables_map = {
    'x': symbols('x'),
    'y': symbols('y'),
    'z': symbols('z'),
    'r': symbols('r'),
    'theta': symbols('theta'),
    'phi': symbols('phi'),
}

def parse_limits(limits_dict):
    # Convierte límites a expresiones sympy
    limits = {}
    for var, (low, high) in limits_dict.items():
        try:
            low_expr = sympify(low)
            high_expr = sympify(high)
            limits[var] = (low_expr, high_expr)
        except Exception as e:
            raise ValueError(f"Límite inválido para {var}: {e}")
    return limits

def parse_order(order_str):
    # Extrae variables en orden de integración, ej: dzdrdtheta -> ['z','r','theta']
    vars_order = re.findall(r'd([a-zA-Z]+)', order_str)
    return vars_order

@app.route('/integral', methods=['POST'])
def integral():
    data = request.json
    try:
        func_str = data['funcion']
        order_str = data['orden']  # ej: dzdrdtheta
        limites = data['limites']  # dict con claves variables y valores [lim_inf, lim_sup]

        # Parsear función
        func = parse_expr(func_str, local_dict=variables_map)

        # Parsear orden
        vars_order = parse_order(order_str)
        if not vars_order:
            return jsonify({'error': 'Orden de integración inválido'}), 400

        # Parsear límites
        limits = parse_limits(limites)

        # Verificar que todas las variables del orden tengan límites
        for v in vars_order:
            if v not in limits:
                return jsonify({'error': f'Faltan límites para variable {v}'}), 400

        # Integrar paso a paso
        steps = []
        integral_expr = func
        for v in vars_order:
            low, high = limits[v]
            integral_expr = integrate(integral_expr, (variables_map[v], low, high))
            step_latex = f"\\int_{{{latex(low)}}}^{{{latex(high)}}} {latex(integral_expr)} \\, d{v}"
            steps.append(step_latex)

        resultado = integral_expr.evalf()

        return jsonify({
            'resultado': float(resultado),
            'pasos': steps,
            'latex_funcion': latex(func),
            'orden': vars_order,
            'limites': {v: [latex(limits[v][0]), latex(limits[v][1])] for v in limits}
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
app.run(host="0.0.0.0", port=5000, debug=True)




