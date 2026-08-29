const LANGS = ["en", "es", "de", "fr", "it"];
const UI = {
  en: { today: "Today", archive: "Archive", sources: "Sources", stories: "stories", posts: "supporting posts", footer: "Updated once a day. Sources and posts stay in the original language.", past: "Past editions", pastDeck: "Open a date to read that day's cards." },
  es: { today: "Hoy", archive: "Archivo", sources: "Fuentes", stories: "historias", posts: "tuits de apoyo", footer: "Se actualiza una vez al día. Fuentes y tuits quedan en el idioma original.", past: "Ediciones anteriores", pastDeck: "Abre una fecha para leer las tarjetas de ese día." },
  de: { today: "Heute", archive: "Archiv", sources: "Quellen", stories: "Stories", posts: "begleitende Posts", footer: "Einmal täglich. Quellen und Posts bleiben in der Originalsprache.", past: "Ältere Ausgaben", pastDeck: "Ein Datum öffnen, um die Karten des Tages zu lesen." },
  fr: { today: "Aujourd'hui", archive: "Archives", sources: "Sources", stories: "histoires", posts: "posts d'appui", footer: "Mis à jour une fois par jour. Sources et posts restent dans la langue d'origine.", past: "Anciennes éditions", pastDeck: "Ouvrez une date pour lire les cartes du jour." },
  it: { today: "Oggi", archive: "Archivio", sources: "Fonti", stories: "storie", posts: "post di supporto", footer: "Aggiornato una volta al giorno. Fonti e post restano in lingua originale.", past: "Edizioni precedenti", pastDeck: "Apri una data per leggere le card di quel giorno." }
};

function currentLang() {
  const stored = localStorage.getItem("dailybarca-lang");
  if (LANGS.includes(stored)) return stored;
  const nav = (navigator.language || "en").slice(0, 2);
  return LANGS.includes(nav) ? nav : "en";
}

function pick(value, lang) {
  if (!value) return "";
  if (typeof value === "string") return value;
  return value[lang] || value.en || Object.values(value)[0] || "";
}

function mergeSources(story, edition) {
  const extra = story.sources || [];
  const base = edition.defaultSources || [];
  const seen = new Set();
  const out = [];
  for (const s of extra.concat(base)) {
    if (!s || !s.label || seen.has(s.label)) continue;
    seen.add(s.label);
    out.push(s);
  }
  return out;
}

async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}

function tweetCount(edition) {
  return edition.stories.reduce((n, s) => n + (s.tweets?.length || 0), 0);
}

function renderCard(story, lang, edition) {
  const ui = UI[lang];
  const tweets = (story.tweets || []).map((t) => `
    <article class="tweet">
      <div class="tweet-head"><span><b>${t.name}</b> ${t.handle}</span><span>${t.time}</span></div>
      <p>${t.text}</p>
      <div class="tweet-stats">${t.stats || ""}</div>
    </article>`).join("");
  const sources = mergeSources(story, edition).map((s) =>
    `<a class="source" href="${s.url}" target="_blank" rel="noopener">${s.label}</a>`
  ).join("");
  return `
    <article class="card ${story.lead ? "lead" : ""} theme-${story.theme || "club"}">
      <div class="kicker">${pick(story.kicker, lang)}</div>
      <h2>${pick(story.headline, lang)}</h2>
      <p class="summary">${pick(story.summary, lang)}</p>
      ${tweets ? `<div class="tweets">${tweets}</div>` : ""}
      <div class="sources">
        <div class="sources-label">${ui.sources}</div>
        <div class="source-row">${sources}</div>
      </div>
    </article>`;
}

function paintLangs(active) {
  const box = document.getElementById("langs");
  if (!box) return;
  box.innerHTML = LANGS.map((code) =>
    `<button class="lang ${code === active ? "on" : ""}" data-lang="${code}">${code.toUpperCase()}</button>`
  ).join("");
  box.querySelectorAll("button").forEach((btn) => {
    btn.onclick = () => {
      localStorage.setItem("dailybarca-lang", btn.dataset.lang);
      boot();
    };
  });
}

function applyChrome(lang) {
  const ui = UI[lang];
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (ui[key]) el.textContent = ui[key];
  });
  const foot = document.getElementById("footerCopy");
  if (foot) foot.textContent = ui.footer;
}

async function renderEdition(date, lang) {
  const index = await loadJSON("/data/editions.json");
  const editionMeta = date ? index.editions.find((e) => e.date === date) : index.editions[0];
  if (!editionMeta) throw new Error("Edition not found");
  const edition = await loadJSON(`/data/${editionMeta.file}`);
  const count = tweetCount(edition);
  const ui = UI[lang];
  document.getElementById("editionChip").textContent = `Edition ${edition.number} · ${edition.label}`;
  document.getElementById("heroTitle").textContent = pick(edition.title, lang);
  document.getElementById("heroDeck").textContent = pick(edition.deck, lang);
  document.getElementById("heroMeta").textContent = `${edition.stories.length} ${ui.stories} · ${count} ${ui.posts}`;
  document.getElementById("grid").innerHTML = edition.stories.map((s) => renderCard(s, lang, edition)).join("");
  document.title = `dailybarca · Edition ${edition.number}`;
}

async function renderArchive(lang) {
  const index = await loadJSON("/data/editions.json");
  const ui = UI[lang];
  const title = document.getElementById("heroTitle");
  const deck = document.getElementById("heroDeck");
  if (title) title.textContent = ui.past;
  if (deck) deck.textContent = ui.pastDeck;
  document.getElementById("archiveList").innerHTML = index.editions.map((e) => `
    <a class="edition-row" href="/?date=${e.date}">
      <div><strong>Edition ${e.number} · ${e.label}</strong><span>${e.lead}</span></div>
      <span>${e.tweets} posts</span>
    </a>`).join("");
}

async function boot() {
  const lang = currentLang();
  paintLangs(lang);
  applyChrome(lang);
  const params = new URLSearchParams(location.search);
  const page = document.body.dataset.page;
  if (page === "home") {
    try { await renderEdition(params.get("date"), lang); }
    catch (err) { document.getElementById("grid").innerHTML = `<p class="summary">${err.message}</p>`; }
  }
  if (page === "archive") await renderArchive(lang);
}

boot();
