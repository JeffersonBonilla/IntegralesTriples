from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex, sympify, N, sin
import os

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr","")
    orden = data.get("orden",[])
    limites = data.get("limites",{})
    tipo = data.get("tipo","Cartesiana")  # nuevo

    try:
        x,y,z,r,theta,phi,rho = symbols("x y z r theta phi rho")
        expr = sympify(expr_str)
        pasos=[]
        current=expr

        is_cil = tipo=="Cilíndrica"
        is_esp = tipo=="Esférica"

        for var in orden:
            if var in limites:
                v = symbols(var)
                a,b = limites[var]

                expr_aux = current
                if is_cil and var=="r": expr_aux *= r
                if is_esp and var=="rho": expr_aux *= rho**2 * sin(phi)

                paso = integrate(expr_aux, (v, sympify(a), sympify(b)))
                pasos.append(f"\\textbf{{Integrando respecto a {var}:}} \\\\ $\\int_{{{a}}}^{{{b}}} {latex(expr_aux)} \\, d{var} = {latex(paso)}$")
                current = paso

        try: resultado_decimal = float(N(current))
        except: resultado_decimal = str(N(current))

        return jsonify({
            "resultado": str(current),
            "resultado_decimal": resultado_decimal,
            "latex": latex(current),
            "pasos": pasos
        })
    except Exception as e:
        return jsonify({"error":str(e)}),400

if __name__=="__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)

