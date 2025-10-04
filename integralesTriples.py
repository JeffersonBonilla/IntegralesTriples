from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin

app = Flask(__name__)

def limpiar_expr(expr):
    if not expr:
        return "0"
    expr = expr.replace("π", "pi")
    expr = expr.replace("\\theta", "theta")
    expr = expr.replace("\\phi", "phi")
    expr = expr.replace("\n", "")
    expr = expr.replace("$", "")
    expr = expr.replace(" ", "*")  # Convierte "2 y" a "2*y"
    return expr

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = limpiar_expr(data.get("expr", ""))
    orden = data.get("orden", [])
    limites = data.get("limites", {})
    tipo = data.get("tipo", "Cartesiana")  # Cartesiana, Cilíndrica, Esférica

    try:
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        is_cil = tipo == "Cilíndrica"
        is_esp = tipo == "Esférica"

        for idx, var in enumerate(orden, start=1):
            v = symbols(var)
            if var in limites:
                a, b = limpiar_expr(limites[var][0]), limpiar_expr(limites[var][1])
                expr_aux = current
                # Aplicar jacobiano
                if is_cil and var == "r":
                    expr_aux *= r
                if is_esp and var == "r":
                    expr_aux *= r**2 * sin(phi)

                # Antiderivada
                primitiva = integrate(expr_aux, v)

                # Evaluación de límites
                evaluacion = primitiva.subs(v, sympify(b)) - primitiva.subs(v, sympify(a))
                pasos.append(f"\\textbf{{Paso {idx}: Integrando respecto a {var}}} \\\\"
                             f"$$\\int_{{{a}}}^{{{b}}} {latex(expr_aux)} \\, d{var} = {latex(primitiva)}$$ \\\\"
                             f"Evaluando los límites: $$ {latex(primitiva.subs(v, sympify(b)))} - {latex(primitiva.subs(v, sympify(a)))} = {latex(evaluacion)} $$")

                current = evaluacion

        try:
            resultado_decimal = float(N(current))
        except:
            resultado_decimal = str(N(current))

        return jsonify({
            "resultado": str(current),
            "resultado_decimal": resultado_decimal,
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





