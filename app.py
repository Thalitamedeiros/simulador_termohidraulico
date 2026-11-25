from math import ceil, exp, floor, log, pi
from flask import Flask, render_template, request

app = Flask(__name__)

CP, T_AMB = 4180, 20   # calor específico da água (J/kg·K) e temperatura ambiente (°C)
H_EXT = 5.75           # convecção externa (W/m²·K)
FATOR = 11.7           # calibração: pontes térmicas, suportes e conexões

ISOLANTES = {
    "Espuma Elastomérica": {
        "k": 0.040,
        "classe": "iso-elastomerica",
        "temp_max": "105 °C",
        "desc": "Alta flexibilidade, células fechadas e excelente barreira contra condensação."
    },
    "Fibra de Vidro": {
        "k": 0.035,
        "classe": "iso-fibra-vidro",
        "temp_max": "450 °C",
        "desc": "Baixa condutividade térmica, leveza estrutural e ótimo custo-benefício industrial."
    }
}


def temperatura(x, t_in, vazao, r_term):
    """Temperatura da água após x metros de tubo."""
    return T_AMB + (t_in - T_AMB) * exp(-FATOR * x / (r_term * vazao * CP))


def parse_float(valor, padrao, minimo=0.0001):
    try:
        v = float(valor)
        return v if v >= minimo else padrao
    except (TypeError, ValueError):
        return padrao


@app.route("/", methods=["GET", "POST"])
def index():
    d = {
        "t_in": 80.0,
        "vazao": 0.5,
        "comp": 10.0,
        "diam": 0.05,
        "iso": "Espuma Elastomérica",
        "esp": 39.0
    }

    if request.method == "POST":
        iso_escolhido = request.form.get("iso", d["iso"])
        if iso_escolhido not in ISOLANTES:
            iso_escolhido = d["iso"]

        d = {
            "t_in": parse_float(request.form.get("t_in"), 80.0, minimo=-273.15),
            "vazao": parse_float(request.form.get("vazao"), 0.5, minimo=0.001),
            "comp": parse_float(request.form.get("comp"), 10.0, minimo=0.1),
            "diam": parse_float(request.form.get("diam"), 0.05, minimo=0.005),
            "iso": iso_escolhido,
            "esp": parse_float(request.form.get("esp"), 39.0, minimo=0.0)
        }

    k_iso = ISOLANTES[d["iso"]]["k"]
    r1 = d["diam"] / 2
    r2 = r1 + d["esp"] / 1000.0

    r_sem = 1 / (H_EXT * 2 * pi * r1)
    if d["esp"] > 0:
        r_cond = log(r2 / r1) / (2 * pi * k_iso)
    else:
        r_cond = 0.0
    r_com = r_cond + 1 / (H_EXT * 2 * pi * r2)

    xs = [d["comp"] * i / 5 for i in range(6)]
    com = [temperatura(x, d["t_in"], d["vazao"], r_com) for x in xs]
    sem = [temperatura(x, d["t_in"], d["vazao"], r_sem) for x in xs]

    perda_com = d["vazao"] * CP * (d["t_in"] - com[-1]) / 1000.0  # kW
    perda_sem = d["vazao"] * CP * (d["t_in"] - sem[-1]) / 1000.0  # kW
    reducao = (1 - perda_com / perda_sem) * 100 if perda_sem != 0 else 0.0

    tabela_pontos = [
        {
            "x": x,
            "t_com": tc,
            "t_sem": ts,
            "ganho": tc - ts
        }
        for x, tc, ts in zip(xs, com, sem)
    ]

    todos_y = com + sem + [d["t_in"]]
    lo, hi = floor(min(todos_y)), ceil(max(todos_y))
    if lo == hi:
        lo -= 1
        hi += 1
    passo = max(1, round((hi - lo) / 4))

    px = lambda x: 80 + 520 * x / d["comp"]
    py = lambda t: 20 + 210 * (hi - t) / (hi - lo)

    g = {
        "com": [(px(x), py(t), f"{x:g}", f"{t:.2f}") for x, t in zip(xs, com)],
        "sem": [(px(x), py(t), f"{x:g}", f"{t:.2f}") for x, t in zip(xs, sem)],
        "xticks": [(px(x), f"{x:g}") for x in xs],
        "yticks": [(py(t), t) for t in range(lo, hi + 1, passo)]
    }

    res = {
        "t_out": com[-1],
        "t_out_sem": sem[-1],
        "perda": perda_com,
        "perda_sem": perda_sem,
        "economia_kw": perda_sem - perda_com,
        "reducao": reducao,
        "r_com": r_com,
        "r_sem": r_sem,
        "k_iso": k_iso
    }

    return render_template(
        "index.html",
        d=d,
        res=res,
        g=g,
        isolantes=ISOLANTES,
        tabela_pontos=tabela_pontos,
        constantes={"cp": CP, "t_amb": T_AMB, "h_ext": H_EXT, "fator": FATOR}
    )


if __name__ == "__main__":
    app.run(debug=True)