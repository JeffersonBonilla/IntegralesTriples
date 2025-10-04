from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp
import json

app = Flask(__name__)
CORS(app)

# Defino símbolos comunes
DEFAULT_SYMBOLS = "x y z r theta phi".split()

def parse_order(order_str):
    # recibe "dzdydx" -> ['z','y','x']
    order = []
    # buscar patrón d<var>
    i = 0
    s = order_str.replace(" ", "").lower()
    while i < len(s):
        if s[i] == 'd':
            i += 1
            # variable puede tener más de una letra (ej theta, phi)
            # comprobamos las longitudes más largas primero
            for var_len in (5,4,3,2,1):
                if i+var_len <= len(s):
                    candidate = s[i:i+var_len]
                    # aceptar si empieza con letra y no comienza con 'd'
                    if candidate.isalpha():
                        order.append(candidate)
                        i += var_len
                        break
            else:
                # fallback: toma una letra
                order.append(s[i])
                i += 1
        else:
            i += 1
    return order

def to_sympy_expr(expr_str, sym_dict):
    # convierne string en expr sympy, con pi, sqrt, etc.
    # Permitimos funciones comunes
    local_dict = {
        'sqrt': sp.sqrt,
        'pi': sp.pi,
        'sin': sp.sin,
        'cos': sp.cos,
        'tan': sp.tan,
        'exp': sp.exp,
        'log': sp.log,
    }
    local_dict.update(sym_dict)
    return sp.sympify(expr_str, locals=local_dict)

@app.route("/integrate", methods=["POST"])
def integrate_route():
    try:
        data = request.get_json(force=True)
        expr_str = data.get("expression", "")
        order_str = data.get("order", "")
        limits = data.get("limits", {}) or {}
        symbols_list = data.get("symbols", DEFAULT_SYMBOLS)
        mode = data.get("mode", "symbolic")

        # crear símbolos
        sympy_syms = {}
        for s in symbols_list:
            sympy_syms[s] = sp.symbols(s)
        # add common names (pi etc)
        sympy_syms['pi'] = sp.pi

        vars_order = parse_order(order_str)
        if not vars_order:
            return jsonify({"status":"error","error":"No se pudo parsear el orden de integración."}), 400

        # construyo la expresión
        expr = to_sympy_expr(expr_str, sympy_syms)

        steps = []
        current_expr = expr

        # Para mostrar la integral iterativa construyo una representación LaTeX acumulada
        # Hacemos integraciones desde la primera diferencial en el string (la interna) hacia afuera.
        # Ej: order ['z','y','x'] integrate wrt z, luego y, luego x.
        numeric_possible = True

        # Para cada variable en order, tomamos sus límites de limits dict si existen
        for var in vars_order:
            if var not in sympy_syms:
                # crear símbolo adicional si no estaba
                sympy_syms[var] = sp.symbols(var)
            sym_var = sympy_syms[var]

        # Hacemos la integración paso a paso
        for i, var in enumerate(vars_order):
            sym_var = sympy_syms[var]
            lim = limits.get(var)
            step_info = {}
            # Intención: calcular integral indefinida y luego definitiva si límites dados
            try:
                # Indefinida
                indef = sp.integrate(current_expr, sym_var)
            except Exception as e:
                return jsonify({"status":"error","error":f"Error integrando indefinidamente respecto {var}: {str(e)}"}), 400

            # Representaciones LaTeX
            indef_latex = sp.latex(indef)
            cur_latex = sp.latex(current_expr)

            if lim and len(lim) == 2:
                a_str, b_str = lim[0], lim[1]
                try:
                    a = to_sympy_expr(a_str, sympy_syms)
                    b = to_sympy_expr(b_str, sympy_syms)
                except Exception as e:
                    return jsonify({"status":"error","error":f"Error parseando límites para {var}: {str(e)}"}), 400

                # calcular definitiva aplicando límites
                try:
                    definite = sp.integrate(current_expr, (sym_var, a, b))
                    # sustituimos current_expr por el resultado para la siguiente iteración
                    current_expr = definite
                    # si los límites contienen símbolos no numéricos, numeric_possible = False
                    if (not (a.is_real and b.is_real)) and (not (a.is_Number and b.is_Number)):
                        # si no son números puros, marcamos que no podemos evaluar numéricamente el resultado final
                        numeric_possible = False
                    step_explanation = (f"Integración respecto {var} desde {sp.latex(a)} hasta {sp.latex(b)}. "
                                        f"Integral indefinida: $\\int {cur_latex}\\,d{var} = {indef_latex}$. "
                                        f"Aplicando límites: $[{sp.latex(indef)}]_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} = {sp.latex(definite)}$.")
                    step_info["latex"] = f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {cur_latex}\\, d{var} = {sp.latex(definite)}"
                    step_info["explanation"] = step_explanation
                except Exception as e:
                    return jsonify({"status":"error","error":f"Error integrando definitivamente respecto {var}: {str(e)}"}), 400
            else:
                # sin límites: dejamos la indefinida como current_expr para el siguiente paso
                current_expr = indef
                numeric_possible = False
                step_explanation = (f"Integración indefinida respecto {var}. "
                                    f"$\\int {cur_latex}\\,d{var} = {indef_latex}$.")
                step_info["latex"] = f"\\int {cur_latex}\\, d{var} = {indef_latex}"
                step_info["explanation"] = step_explanation

            steps.append(step_info)

        # Resultado final
        result_expr = sp.simplify(current_expr)
        result_latex = sp.latex(result_expr)

        result_numeric = None
        if mode == "numeric":
            try:
                if numeric_possible:
                    result_numeric = float(sp.N(result_expr))
                else:
                    # intentar evaluar numéricamente si quedan símbolos
                    result_numeric = None
            except Exception:
                result_numeric = None

        response = {
            "status": "ok",
            "result_latex": result_latex,
            "steps": steps
        }
        if result_numeric is not None:
            response["result"] = result_numeric
        else:
            # si no hay resultado numérico, incluir expresión simbólica
            response["result_expr"] = str(result_expr)

        return jsonify(response)
    except Exception as e:
        return jsonify({"status":"error","error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


