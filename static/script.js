document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".nav-link");
  const abas = document.querySelectorAll(".aba-conteudo");

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const alvo = link.dataset.aba;

      links.forEach((l) => l.classList.remove("ativo"));
      abas.forEach((a) => a.classList.remove("ativo"));

      link.classList.add("ativo");
      const abaAlvo = document.getElementById(`aba-${alvo}`);
      if (abaAlvo) {
        abaAlvo.classList.add("ativo");
      }
    });
  });

  const selectIso = document.getElementById("select-iso");
  const inpEsp = document.getElementById("inp-esp");
  const visualTubo = document.getElementById("visual-tubo");
  const labelTuboIso = document.getElementById("label-tubo-iso");
  const infoMaterial = document.getElementById("info-material");

  const classesIsolantes = [
    "iso-elastomerica",
    "iso-fibra-vidro",
    "iso-sem"
  ];

  function atualizarVisualIsolante() {
    if (!selectIso || !inpEsp || !visualTubo) return;

    const opt = selectIso.options[selectIso.selectedIndex];
    const nome = opt.value;
    const classe = opt.dataset.classe;
    const k = opt.dataset.k;
    const desc = opt.dataset.desc;
    const esp = Math.max(0, parseFloat(inpEsp.value) || 0);

    if (infoMaterial) {
      infoMaterial.innerHTML = `<span class="badge-k">k = ${k} W/m·K</span><p>${desc}</p>`;
    }

    if (labelTuboIso) {
      labelTuboIso.textContent = esp > 0 ? `${nome} (${esp} mm)` : "Sem isolamento (0 mm)";
    }

    visualTubo.classList.remove(...classesIsolantes);
    if (esp === 0) {
      visualTubo.classList.add("iso-sem");
    } else if (classe) {
      visualTubo.classList.add(classe);
    }

    const padVertical = esp === 0 ? 4 : Math.min(24, Math.max(8, Math.round(esp * 0.4)));
    const alturaTotal = 56 + padVertical * 2;
    visualTubo.style.paddingTop = `${padVertical}px`;
    visualTubo.style.paddingBottom = `${padVertical}px`;
    visualTubo.style.height = `${alturaTotal}px`;
  }

  if (selectIso) selectIso.addEventListener("change", atualizarVisualIsolante);
  if (inpEsp) inpEsp.addEventListener("input", atualizarVisualIsolante);
  atualizarVisualIsolante();

  const pontos = document.querySelectorAll(".ponto-interativo");
  const tooltip = document.getElementById("tooltip-grafico");
  const graficoBox = document.querySelector(".grafico-box");

  if (tooltip && graficoBox) {
    pontos.forEach((ponto) => {
      ponto.addEventListener("mouseenter", () => {
        const { tipo, x, t } = ponto.dataset;
        tooltip.innerHTML = `<strong>${tipo}</strong><br>Posição: ${x} m | Temp: <b>${t} °C</b>`;
        tooltip.style.display = "block";
      });

      ponto.addEventListener("mousemove", (e) => {
        const rect = graficoBox.getBoundingClientRect();
        tooltip.style.left = `${e.clientX - rect.left + 12}px`;
        tooltip.style.top = `${e.clientY - rect.top - 45}px`;
      });

      ponto.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
      });
    });
  }
});