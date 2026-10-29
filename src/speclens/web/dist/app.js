const $ = (s) => document.querySelector(s);
let mode = "inspect",
  lastResult = null,
  documents = [];
const names = {
  "uno-r4-minima": "UNO R4 Minima",
  "uno-r4-wifi": "UNO R4 WiFi",
  "nano-esp32": "Nano ESP32",
  "nano-33-ble-rev2": "Nano 33 BLE Rev2",
  "nano-33-ble-sense-rev2": "Nano 33 BLE Sense Rev2",
  "nano-rp2040-connect": "Nano RP2040 Connect",
  "mkr-wifi-1010": "MKR WiFi 1010",
  "mega-2560": "Mega 2560 Rev3",
  "portenta-c33": "Portenta C33",
  opta: "Opta",
};
function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}
function selected() {
  return [...document.querySelectorAll("#sources input:checked")].map(
    (n) => n.value,
  );
}
function selectDocs(ids) {
  document
    .querySelectorAll("#sources input")
    .forEach((n) => (n.checked = ids.includes(n.value)));
  updateSelectionCount();
}
function updateSelectionCount() {
  const count = selected().length;
  $("#selection-count").textContent =
    `${count} document${count === 1 ? "" : "s"} selected`;
}
function setMode(value) {
  mode = value;
  document
    .querySelectorAll("[data-mode]")
    .forEach((n) => n.classList.toggle("active", n.dataset.mode === mode));
  $("#target-row").hidden = mode !== "compare";
  $("#question").readOnly = mode === "compare";
  if (mode === "compare")
    $("#question").value =
      "Compare the recommended VIN input voltage ranges for the selected documents.";
}
document
  .querySelectorAll("[data-mode]")
  .forEach((n) => (n.onclick = () => setMode(n.dataset.mode)));
const presets = {
  vin: {
    docs: ["uno-r4-minima", "nano-esp32"],
    mode: "compare",
    question:
      "Compare the recommended VIN input voltage ranges for the selected documents.",
  },
  opta: {
    docs: ["opta"],
    mode: "inspect",
    question: "Hangi Opta SKU kodu Wi-Fi bağlantısı sunuyor?",
  },
  temperature: {
    docs: ["nano-esp32"],
    mode: "inspect",
    question:
      "Önerilen ortam sıcaklığı tablosu ile EUT uygunluk ifadesindeki iki üst sıcaklık sınırını ayrı kapsamlarıyla bildir.",
  },
  missing: {
    docs: ["opta"],
    mode: "inspect",
    question:
      "Bu datasheet içinde Türk lirası cinsinden perakende satış fiyatı belirtiliyor mu?",
  },
};
document.querySelectorAll("[data-preset]").forEach(
  (n) =>
    (n.onclick = () => {
      const p = presets[n.dataset.preset];
      setMode(p.mode);
      selectDocs(p.docs);
      $("#question").value = p.question;
    }),
);
async function preview(c) {
  const head = $("#viewer-head"),
    body = $("#viewer-body");
  head.replaceChildren(
    el("span", "", `${names[c.document_id] || c.document_id} · p. ${c.page}`),
  );
  const link = el("a", "", "Open PDF");
  link.href = `/documents/${encodeURIComponent(c.document_id)}/pdf#page=${c.page}`;
  link.target = "_blank";
  link.rel = "noopener";
  head.append(link);
  body.className = "";
  const img = el("img");
  img.alt = `${names[c.document_id] || c.document_id}, physical PDF page ${c.page}`;
  img.src = `/documents/${encodeURIComponent(c.document_id)}/pages/${c.page}.png`;
  img.onerror = () => {
    body.className = "viewer-empty";
    body.textContent = "PDF page unavailable. Check the source file.";
  };
  body.replaceChildren(img);
}
function render(result) {
  lastResult = result;
  $("#empty").hidden = true;
  $("#results").hidden = false;
  $("#json").textContent = JSON.stringify(result, null, 2);
  const box = $("#findings");
  box.replaceChildren();
  $("#results-title").textContent =
    `${result.findings.length} findings · ${Number(result.metrics.total_seconds).toFixed(1)} s`;
  for (const f of result.findings) {
    const card = el("article", "card"),
      top = el("div", "card-top");
    const comp = (result.comparison || []).find(
      (c) =>
        c.document_id === f.document_id &&
        (c.status !== "computed" ||
          f.citations.some(
            (citation) =>
              citation.chunk_id === c.citation.chunk_id &&
              citation.quote === c.citation.quote,
          )),
    );
    const displayValue =
      comp?.status === "computed"
        ? `${comp.lower}–${comp.upper} ${comp.range_unit}`
        : f.value;
    top.append(
      el("span", "doc-label", names[f.document_id] || f.document_id),
      el(
        "span",
        "tag" + (f.status === "stated" ? "" : " review"),
        f.status === "stated"
          ? "Source linked"
          : f.status === "conflicting"
            ? "Needs review"
            : "Not found",
      ),
    );
    card.append(
      top,
      el(
        "div",
        "field",
        {
          vin_voltage: "VIN input range",
          gpio_voltage: "Pin voltage",
          sram_capacity: "SRAM",
          flash_capacity: "Flash memory",
          humidity_sensor: "Humidity sensor",
          clock_frequency: "Processor clock",
          digital_io_count: "Digital I/O pins",
          nominal_supply: "Nominal supply",
          wifi_sku: "Wi-Fi variant",
          operating_temperature: "Operating temperature",
          ambient_temperature: "Ambient temperature",
          eut_temperature: "EUT temperature limit",
          retail_price: "Retail price",
        }[f.field] || f.field.replaceAll("_", " "),
      ),
      el(
        "div",
        "value" + (!displayValue || displayValue.length > 38 ? " long" : ""),
        displayValue || "Not stated in the retrieved evidence.",
      ),
    );
    if (comp) {
      card.append(
        el(
          "div",
          "comparison" + (!comp.within_documented_range ? " no" : ""),
          comp.status === "computed"
            ? `${comp.target} ${comp.target_unit} ${comp.within_documented_range ? "is within" : "is outside"} the documented VIN range.`
            : "Range comparison needs review.",
        ),
      );
    }
    let excerpts;
    if (f.citations.length) {
      const source = el(
        "button",
        "source-page",
        `View page ${f.citations[0].page}`,
      );
      source.type = "button";
      source.onclick = () => preview(f.citations[0]);
      excerpts = el("details", "source-excerpts");
      excerpts.append(
        el(
          "summary",
          "",
          `${f.citations.length} source excerpt${f.citations.length === 1 ? "" : "s"}`,
        ),
      );
      card.append(source, excerpts);
    }
    for (const c of f.citations) {
      const cite = el("div", "citation"),
        btn = el("button", "", `Page ${c.page}`);
      btn.type = "button";
      btn.onclick = () => preview(c);
      cite.append(btn, el("p", "quote", c.quote));
      excerpts.append(cite);
    }
    box.append(card);
  }
  if (!result.findings.length)
    box.append(
      el("article", "card", "No usable answer. Try a more specific question."),
    );
  if (result.rejected_findings?.length)
    box.append(
      el(
        "article",
        "card",
        `${result.rejected_findings.length} finding(s) omitted: source validation failed.`,
      ),
    );
  const first = result.findings.flatMap((f) => f.citations)[0];
  if (first) preview(first);
  else {
    $("#viewer-head").replaceChildren(el("span", "", "Source preview"));
    $("#viewer-body").className = "viewer-empty";
    $("#viewer-body").textContent = "No source page returned.";
  }
}
$("#ask").onsubmit = async (e) => {
  e.preventDefault();
  const docs = selected();
  if (docs.length < 1 || docs.length > 3) {
    $("#message").className = "error";
    $("#message").textContent = "Select between 1 and 3 documents.";
    return;
  }
  const btn = $("#submit");
  btn.disabled = true;
  $("#message").className = "";
  $("#message").replaceChildren(
    el("span", "loading"),
    document.createTextNode("Analyzing..."),
  );
  try {
    const payload =
      mode === "compare"
        ? {
            documents: docs,
            target: $("#target").value,
            unit: $("#unit").value,
            method: $("#method").value,
          }
        : {
            question: $("#question").value,
            documents: docs,
            method: $("#method").value,
          };
    const response = await fetch(
      mode === "compare" ? "/compare-vin" : "/answer",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    );
    const result = await response.json();
    if (!response.ok)
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : JSON.stringify(result.detail),
      );
    render(result);
    $("#message").textContent =
      result.status === "provenance_checked" ? "" : "Some results need review.";
  } catch (error) {
    $("#message").className = "error";
    $("#message").textContent = error.message;
  } finally {
    btn.disabled = false;
  }
};
$("#export").onclick = () => {
  if (!lastResult) return;
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(lastResult, null, 2)], {
      type: "application/json",
    }),
  );
  const a = el("a");
  a.href = url;
  a.download = "speclens-result.json";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
fetch("/documents")
  .then((r) => {
    if (!r.ok)
      throw Error("Source library unavailable. Run the corpus setup first.");
    return r.json();
  })
  .then((rows) => {
    documents = rows;
    $("#source-count").textContent = rows.length;
    for (const d of rows) {
      const label = el("label", "source"),
        input = el("input");
      input.type = "checkbox";
      input.value = d.id;
      input.checked = ["uno-r4-minima", "nano-esp32"].includes(d.id);
      input.onchange = updateSelectionCount;
      const content = el("span");
      content.append(
        el("strong", "", names[d.id] || d.id),
        el("small", "", `${d.sku} · ${d.pages} pages`),
      );
      label.append(input, content);
      $("#sources").append(label);
    }
    updateSelectionCount();
  })
  .catch((e) => {
    $("#message").className = "error";
    $("#message").textContent = e.message;
  });
