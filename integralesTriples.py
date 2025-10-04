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
    return expr

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = limpiar_expr(data.get("expr", ""))
    orden = data.get("orden", [])
    limites = data.get("limites", {})
    tipo = data.get("tipo", "Cartesiana")

    try:
        # símbolos
        x, y, z, r, theta, phi = symbols("x y z r theta phi")
        expr = sympify(expr_str)
        pasos = []
        current = expr

        is_cil = tipo == "Cilíndrica"
        is_esp = tipo == "Esférica"

        for var in orden:
            v = symbols(var)
            if var in limites:
                a, b = limpiar_expr(limites[var][0]), limpiar_expr(limites[var][1])
                expr_aux = current

                # Jacobiano
                if is_cil and var == "r":
                    expr_aux *= r
                if is_esp and var == "r":
                    expr_aux *= r**2 * sin(phi)

                # integral indefinida primero
                indef = integrate(expr_aux, v)
                # eval en límites
                eval_ab = indef.subs(v, sympify(b)) - indef.subs(v, sympify(a))
                paso = eval_ab

                pasos.append(
                    f"Paso {len(pasos)+1}: ∫ {latex(expr_aux)} d{var} = {latex(indef)}"
                )
                pasos.append(
                    f"Evaluando en [{a}, {b}]: {latex(indef.subs(v, sympify(b)))} - {latex(indef.subs(v, sympify(a)))} = {latex(eval_ab)}"
                )

                current = paso

        return jsonify({
            "resultado": str(current),
            "resultado_decimal": float(N(current)),
            "latex": latex(current),
            "pasos": pasos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


