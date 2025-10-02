from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin, pi
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Integrales Triples Universal funcionando!"

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr", "")
    orden = data.get("orden", [])       # ej: ["z","r","theta"]
    limites = data.get("limites", {})   # ej: { "x":["0","2"], "y":["0","1"], "z":["0","r"] }

    try:
        # Definir variables simbólicas
        x, y, z, r, theta, phi, rho = symbols("x y z r theta phi rho")
        expr = sympify(expr_str)

        pasos = []
        current_expr = expr

        # Detectar coordenadas
        is_cilindrica = {"r", "theta", "z"} <= set(orden)
        is_esferica = {"rho", "theta", "phi"} <= set(orden)

        for var in orden:
            if var in limites:
                v = symbols(var)
                a, b = limites[var]

                expr_a_integrar = current_expr

                # Aplicar factor jacobiano solo al integrar la variable externa correspondiente
                if is_cilindrica and var in ["r", "theta", "z"]:
                    if var == "r":
                        expr_a_integrar = expr_a_integrar * r
                elif is_esferica and var in ["rho", "theta", "phi"]:
                    if var == "rho":
                        expr_a_integrar = expr_a_integrar * rho**2 * sin(phi)

                # Integrar con límites
                paso_simb = integrate(expr_a_integrar, (v, sympify(a), sympify(b)))

                pasos.append(
                    f"\\textbf{{Integrando respecto a {var}:}} \\\\ "
                    f"$\\int_{{{a}}}^{{{b}}} {latex(expr_a_integrar)} \\, d{var} = {latex(paso_simb)}$"
                )

                current_expr = paso_simb

        # Evaluar decimal si es posible
        try:
            resultado_decimal = float(N(current_expr))
        except:
            resultado_decimal = str(N(current_expr))  # si quedan símbolos, lo dejamos como string

        return jsonify({
            "resultado": str(current_expr),
            "resultado_decimal": resultado_decimal,
            "latex": latex(current_expr),
            "pasos": pasos
        })

    except Exception as e:
        print("ERROR en API:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

