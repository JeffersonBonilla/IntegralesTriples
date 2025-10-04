from flask import Flask, request, jsonify
from sympy import symbols, sympify, integrate, latex
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)

@app.route("/integrate", methods=["POST"])
def integrate_triple():
    try:
        data = request.get_json()

        # Leer datos
        func_str = data.get("function", "")
        order = data.get("order", "")      # Ej: 'dzdydx'
        limits = data.get("limits", {})    # Ej: {"x":[0,1], "y":[0,1], "z":[0,1]}

        # Definir símbolos
        x, y, z, r, theta, phi = symbols('x y z r theta phi')
        sym_dict = {'x': x, 'y': y, 'z': z, 'r': r, 'theta': theta, 'phi': phi}

        # Convertir string a expresión sympy
        func = parse_expr(func_str, local_dict=sym_dict)

        steps = []
        result = func

        # Realizar integración según el orden indicado
        # El order debe ser como 'dzdy dx' o 'dzdydx' (sin espacios)
        vars_order = []
        for ch in order:
            if ch in ['x','y','z','r','θ','φ','theta','phi']:
                if ch == 'θ':
                    ch = 'theta'
                if ch == 'φ':
                    ch = 'phi'
                vars_order.append(sym_dict[ch])
            elif ch == 'd':
                continue  # Ignorar 'd'
        
        # Integración paso a paso
        for var in vars_order:
            if var.name in limits:
                a, b = limits[var.name]
                result = integrate(result, (var, a, b))
                steps.append(f"\\int_{{{a}}}^{{{b}}} ... d{var} = {latex(result)}")
            else:
                # Si no hay límites, hacer integral indefinida
                result = integrate(result, var)
                steps.append(f"\\int ... d{var} = {latex(result)}")

        # Preparar JSON de respuesta
        response = {
            "result": str(result),
            "steps": steps
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


