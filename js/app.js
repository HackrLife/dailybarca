async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}
function tweetCount(edition) {
  return edition.stories.reduce((n, s) => n + (s.tweets?.length || 0), 0);
}
function renderCard(story) {
  const tweets = (story.tweets || []).map((t) => `
    <article class="tweet">
      <div class="tweet-head">
        <span><b>${t.name}</b> ${t.handle}</span>
        <span>${t.time}</span>
      </div>
      <p>${t.text}</p>
      <div class="tweet-stats">${t.stats || ""}</div>
    </article>
  `).join("");
  const sources = (story.sources || []).map((s) =>
    `<a class="source" href="${s.url}" target="_blank" rel="noopener">${s.label}</a>`
  ).join("");
  return `
    <article class="card ${story.lead ? "lead" : ""}">
      <div class="kicker">${story.kicker}</div>
      <h2>${story.headline}</h2>
      <p class="summary">${story.summary}</p>
      ${tweets ? `<div class="tweets">${tweets}</div>` : ""}
      <div class="sources">
        <div class="sources-label">Sources</div>
        <div class="source-row">${sources}</div>
      </div>
    </article>
  `;
}
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
async function renderEdition(date) {
  const index = await loadJSON("/data/editions.json");
  const editionMeta = date
    ? index.editions.find((e) => e.date === date)
    : index.editions[0];
  if (!editionMeta) throw new Error("Edition not found");
  const edition = await loadJSON(`/data/${editionMeta.file}`);
  const count = tweetCount(edition);
  setText("editionChip", `Edition ${edition.number} · ${edition.label}`);
  setText("heroTitle", edition.title);
  setText("heroDeck", edition.deck);
  setText("heroMeta", `${edition.stories.length} stories · ${count} supporting posts`);
  document.getElementById("grid").innerHTML = edition.stories.map(renderCard).join("");
  document.title = `dailybarca · Edition ${edition.number}`;
}
async function renderArchive() {
  const index = await loadJSON("/data/editions.json");
  document.getElementById("archiveList").innerHTML = index.editions.map((e) => `
    <a class="edition-row" href="/?date=${e.date}">
      <div>
        <strong>Edition ${e.number} · ${e.label}</strong>
        <span>${e.lead}</span>
      </div>
      <span>${e.tweets} posts</span>
    </a>
  `).join("");
}
const params = new URLSearchParams(location.search);
const page = document.body.dataset.page;
if (page === "home") renderEdition(params.get("date")).catch((err) => {
  document.getElementById("grid").innerHTML = `<p class="summary">${err.message}</p>`;
});
if (page === "archive") renderArchive();
