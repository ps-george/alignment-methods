"use strict";

const $ = (id) => document.getElementById(id);

function show(el, html) { el.innerHTML = html; el.hidden = false; }
function hide(el) { el.hidden = true; el.innerHTML = ""; }

$("shorten-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const url = $("url-input").value.trim();
  hide($("shorten-result")); hide($("shorten-error"));
  try {
    const resp = await fetch("/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      show($("shorten-error"), `Error: ${data.error || resp.statusText}`);
      return;
    }
    show(
      $("shorten-result"),
      `<dl class="kv">
         <dt>Short URL:</dt><dd><a href="${data.short_url}" target="_blank" rel="noopener">${data.short_url}</a></dd>
         <dt>Code:</dt><dd><code>${data.code}</code></dd>
         <dt>Original:</dt><dd>${data.url}</dd>
       </dl>`
    );
  } catch (err) {
    show($("shorten-error"), `Network error: ${err.message}`);
  }
});

$("stats-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const code = $("code-input").value.trim();
  hide($("stats-result")); hide($("stats-error"));
  try {
    const resp = await fetch(`/api/stats/${encodeURIComponent(code)}`);
    const data = await resp.json();
    if (!resp.ok) {
      show($("stats-error"), `Error: ${data.error || resp.statusText}`);
      return;
    }
    show(
      $("stats-result"),
      `<dl class="kv">
         <dt>Code:</dt><dd><code>${data.code}</code></dd>
         <dt>Clicks:</dt><dd>${data.clicks}</dd>
         <dt>Original:</dt><dd>${data.url}</dd>
       </dl>`
    );
  } catch (err) {
    show($("stats-error"), `Network error: ${err.message}`);
  }
});
