from flask import Flask, request, jsonify
from sympy import symbols, integrate, latex

app = Flask(__name__)

@app.route("/integral", methods=["POST"])
def integral():
    data = request.json
    expr_str = data.get("expr")
    var_str = data.get("var")

    x = symbols(var_str)
    expr = eval(expr_str)  # 👈 OJO: luego mejor parsear seguro
    result = integrate(expr, x)

    return jsonify({
        "resultado": str(result),
        "latex": latex(result)
    })

if __name__ == "__main__":
    app.run()
