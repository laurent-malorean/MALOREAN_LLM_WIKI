#!/usr/bin/env python3
"""
Génère data/generated/mobileapp/mobile.html — version smartphone hors ligne du wiki de révision.
Toutes les notes dues sont embarquées en JSON dans le HTML.
"""
import argparse
import json
import random
import re
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
WIKI_ROOT = BASE_DIR / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())
STATE_FILE = BASE_DIR / "data" / "generated" / "website" / "review_state.json"
OUTPUT_DIR = BASE_DIR / "data" / "generated" / "mobileapp"
OUTPUT_FILE = OUTPUT_DIR / "mobile.html"

TYPE_COLORS = {
    "atomic_note": "#3b82f6",
    "glossary_term": "#10b981",
    "regulatory_text": "#f59e0b",
    "habilitation": "#8b5cf6",
    "norm_reference": "#ec4899",
    "business_process": "#06b6d4",
    "business_rule": "#ef4444",
    "indicator": "#84cc16",
    "normative_requirement": "#f97316",
    "domain_object": "#14b8a6",
}

TYPE_LABELS = {
    "atomic_note": "Note atomique",
    "glossary_term": "Glossaire",
    "regulatory_text": "Réglementaire",
    "habilitation": "Habilitation",
    "norm_reference": "Norme",
    "business_process": "Processus",
    "business_rule": "Règle métier",
    "indicator": "Indicateur",
    "normative_requirement": "Exigence",
    "domain_object": "Objet métier",
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text.strip()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    return parts[2].strip()


def read_note_body(filepath_rel: str, theme_dir: Path) -> str:
    # Essayer d'abord relatif à BASE_DIR (chemin complet), puis relatif au thème
    for base in [BASE_DIR, theme_dir]:
        try:
            full = base / filepath_rel
            if full.exists():
                return strip_frontmatter(full.read_text(encoding="utf-8"))
        except Exception:
            pass
    return ""


def is_due(entry: dict) -> bool:
    nr = entry.get("next_review", "")
    if not nr:
        return True
    try:
        return date.fromisoformat(nr) <= date.today()
    except Exception:
        return True


def build_notes(theme_dir: Path) -> list:
    artifacts_index = BASE_DIR / "data" / "generated" / "indexes" / theme_dir.name / "artifacts.index.json"
    artifacts = load_json(artifacts_index)
    if not artifacts:
        print(f"ERREUR : impossible de lire {artifacts_index}")
        return []

    state_data = load_json(STATE_FILE) or {"notes": {}}
    state_notes = state_data.get("notes", {})

    notes = []
    for e in artifacts:
        if e.get("type") in ("source_record", "moc"):
            continue
        uid = e.get("uid", "")
        if not uid:
            continue

        entry = state_notes.get(uid, {})
        if not is_due(entry):
            continue

        filepath = e.get("path", e.get("file", ""))
        body = read_note_body(filepath, theme_dir) if filepath else ""

        notes.append({
            "uid": uid,
            "id": e.get("id", ""),
            "title": e.get("title", e.get("id", "")),
            "type": e.get("type", "unknown"),
            "body": body,
            "color": TYPE_COLORS.get(e.get("type", ""), "#6b7280"),
            "label": TYPE_LABELS.get(e.get("type", ""), e.get("type", "")),
        })

    random.shuffle(notes)
    return notes


def generate_html(notes: list) -> str:
    notes_json = json.dumps(notes, ensure_ascii=False)
    count = len(notes)
    today = date.today().isoformat()

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>Wiki Maintenance — Mobile</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ height: 100%; overflow: hidden; -webkit-tap-highlight-color: transparent; }}

:root {{
  --bg: #ffffff;
  --fg: #1e293b;
  --header-bg: #1e293b;
  --header-fg: #f8fafc;
  --body-color: #334155;
  --h1-color: #0f172a;
  --h2-color: #475569;
  --code-bg: #f1f5f9;
  --card-bg: #ffffff;
  --btn-bg: #1e293b;
  --btn-fg: #ffffff;
  --done-bg: #f0fdf4;
  --done-color: #166534;
  --meta-border: #e2e8f0;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0f172a;
    --fg: #e2e8f0;
    --header-bg: #020617;
    --header-fg: #e2e8f0;
    --body-color: #cbd5e1;
    --h1-color: #f1f5f9;
    --h2-color: #94a3b8;
    --code-bg: #1e293b;
    --card-bg: #0f172a;
    --btn-bg: #3b82f6;
    --btn-fg: #ffffff;
    --done-bg: #052e16;
    --done-color: #86efac;
    --meta-border: #1e293b;
  }}
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--fg);
  display: flex;
  flex-direction: column;
  height: 100%;
}}

.header {{
  background: var(--header-bg);
  color: var(--header-fg);
  padding: 12px 16px 10px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.header-title {{
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0.7;
}}
.header-counter {{
  font-size: 1rem;
  font-weight: 600;
}}

.progress-track {{
  height: 3px;
  background: rgba(255,255,255,0.15);
  flex-shrink: 0;
}}
.progress-fill {{
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}}

.card-area {{
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 16px 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}}

.card-meta {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}}
.badge {{
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 700;
  color: white;
  white-space: nowrap;
}}
.note-id {{
  font-family: monospace;
  font-size: 0.72rem;
  color: #94a3b8;
}}

.card-title {{
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--h1-color);
}}

.card-body {{
  font-size: 0.97rem;
  line-height: 1.65;
  color: var(--body-color);
  flex: 1;
}}
.card-body h1 {{
  font-size: 0.95rem;
  font-weight: 700;
  margin: 14px 0 4px;
  color: var(--h1-color);
}}
.card-body h2 {{
  font-size: 0.8rem;
  font-weight: 700;
  margin: 12px 0 3px;
  color: var(--h2-color);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}}
.card-body p {{ margin: 0 0 7px; }}
.card-body li {{ margin: 2px 0 2px 18px; }}
.card-body code {{
  background: var(--code-bg);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.82em;
}}
.card-body pre {{
  background: var(--code-bg);
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.78em;
  margin: 6px 0;
}}
.card-body table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82em;
  margin: 8px 0;
}}
.card-body th, .card-body td {{
  border: 1px solid var(--meta-border);
  padding: 5px 8px;
  text-align: left;
}}

.btn-area {{
  flex-shrink: 0;
  padding: 12px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
}}
.btn-next {{
  width: 100%;
  height: 56px;
  background: var(--btn-bg);
  color: var(--btn-fg);
  border: none;
  border-radius: 14px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.3px;
  -webkit-tap-highlight-color: transparent;
  transition: opacity 0.12s;
}}
.btn-next:active {{ opacity: 0.8; }}

.done-screen {{
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 32px;
  text-align: center;
  gap: 12px;
}}
.done-screen.visible {{ display: flex; }}
.done-icon {{ font-size: 3rem; }}
.done-title {{ font-size: 1.4rem; font-weight: 700; color: var(--h1-color); }}
.done-sub {{ font-size: 0.9rem; color: var(--h2-color); }}

.hidden {{ display: none !important; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-title">Wiki Maintenance</div>
  <div class="header-counter" id="counter">Chargement...</div>
</div>
<div class="progress-track">
  <div class="progress-fill" id="progress" style="width:0%"></div>
</div>

<div class="card-area" id="card-area">
  <div class="card-meta" id="card-meta"></div>
  <div class="card-title" id="card-title"></div>
  <div class="card-body" id="card-body"></div>
</div>

<div class="done-screen" id="done-screen">
  <div class="done-icon">✓</div>
  <div class="done-title">Session terminée</div>
  <div class="done-sub">Toutes les notes ont été vues.</div>
</div>

<div class="btn-area" id="btn-area">
  <button class="btn-next" id="btn-next" onclick="next()">Suivant</button>
</div>

<script>
const NOTES = {notes_json};
const TOTAL = NOTES.length;
let idx = 0;

function mdToHtml(text) {{
  if (!text) return '';
  const lines = text.split('\\n');
  const result = [];
  let inPre = false;
  let inUl = false;
  let inOl = false;

  function closeLists() {{
    if (inUl) {{ result.push('</ul>'); inUl = false; }}
    if (inOl) {{ result.push('</ol>'); inOl = false; }}
  }}

  for (let i = 0; i < lines.length; i++) {{
    let line = lines[i];

    // Bloc de code
    if (line.startsWith('```')) {{
      closeLists();
      if (!inPre) {{
        result.push('<pre><code>');
        inPre = true;
      }} else {{
        result.push('</code></pre>');
        inPre = false;
      }}
      continue;
    }}
    if (inPre) {{
      result.push(esc(line));
      continue;
    }}

    // Titres
    if (line.startsWith('### ')) {{ closeLists(); result.push('<h2>' + inline(line.slice(4)) + '</h2>'); continue; }}
    if (line.startsWith('## '))  {{ closeLists(); result.push('<h2>' + inline(line.slice(3)) + '</h2>'); continue; }}
    if (line.startsWith('# '))   {{ closeLists(); result.push('<h1>' + inline(line.slice(2)) + '</h1>'); continue; }}

    // Ligne vide
    if (!line.trim()) {{
      closeLists();
      continue;
    }}

    // Tableau (ligne contenant |)
    if (line.includes('|') && line.trim().startsWith('|')) {{
      closeLists();
      if (line.replace(/[\\|\\s\\-]/g, '').length === 0) continue; // séparateur
      const cells = line.split('|').filter((_, i, a) => i > 0 && i < a.length - 1);
      result.push('<tr>' + cells.map(c => '<td>' + inline(c.trim()) + '</td>').join('') + '</tr>');
      continue;
    }}

    // Liste non ordonnée
    if (line.match(/^[-*] /)) {{
      if (inOl) {{ result.push('</ol>'); inOl = false; }}
      if (!inUl) {{ result.push('<ul>'); inUl = true; }}
      result.push('<li>' + inline(line.slice(2)) + '</li>');
      continue;
    }}

    // Liste ordonnée
    if (line.match(/^\\d+\\. /)) {{
      if (inUl) {{ result.push('</ul>'); inUl = false; }}
      if (!inOl) {{ result.push('<ol>'); inOl = true; }}
      result.push('<li>' + inline(line.replace(/^\\d+\\. /, '')) + '</li>');
      continue;
    }}

    closeLists();
    result.push('<p>' + inline(line) + '</p>');
  }}

  closeLists();
  if (inPre) result.push('</code></pre>');
  return result.join('\\n');
}}

function esc(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function inline(s) {{
  // Masquer la section "Validation atomique"
  s = s.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
  s = s.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/\\[\\[([^\\]]+?)\\]\\]/g, '<em>$1</em>');
  s = s.replace(/\\[([^\\]]+)\\]\\([^)]+\\)/g, '<em>$1</em>');
  return s;
}}

function hideValidation(container) {{
  const h2s = container.querySelectorAll('h2');
  h2s.forEach(h => {{
    if (h.textContent.trim().toLowerCase().includes('validation atomique')) {{
      let el = h;
      while (el) {{
        const next = el.nextElementSibling;
        el.style.display = 'none';
        el = next;
        if (!el || el.tagName === 'H2') break;
      }}
      h.style.display = 'none';
    }}
  }});
}}

function showNote(i) {{
  if (i >= TOTAL) {{
    document.getElementById('card-area').classList.add('hidden');
    document.getElementById('btn-area').classList.add('hidden');
    document.getElementById('done-screen').classList.add('visible');
    document.getElementById('counter').textContent = 'Session terminée';
    document.getElementById('progress').style.width = '100%';
    return;
  }}
  const n = NOTES[i];
  document.getElementById('counter').textContent = (i + 1) + ' / ' + TOTAL + ' notes';
  document.getElementById('progress').style.width = Math.round((i / TOTAL) * 100) + '%';

  const meta = document.getElementById('card-meta');
  meta.innerHTML =
    '<span class="note-id">' + n.id + '</span>' +
    '<span class="badge" style="background:' + n.color + '">' + n.label + '</span>';

  document.getElementById('card-title').textContent = n.title;

  const bodyEl = document.getElementById('card-body');
  bodyEl.innerHTML = mdToHtml(n.body);
  hideValidation(bodyEl);

  // Remonter en haut
  document.getElementById('card-area').scrollTop = 0;
}}

function next() {{
  idx++;
  showNote(idx);
}}

// Mélange aléatoire à chaque chargement (Fisher-Yates)
for (let i = NOTES.length - 1; i > 0; i--) {{
  const j = Math.floor(Math.random() * (i + 1));
  [NOTES[i], NOTES[j]] = [NOTES[j], NOTES[i]];
}}

// Init
if (TOTAL === 0) {{
  document.getElementById('card-area').classList.add('hidden');
  document.getElementById('btn-area').classList.add('hidden');
  document.getElementById('done-screen').classList.add('visible');
  document.getElementById('counter').textContent = 'Aucune note à réviser';
}} else {{
  showNote(0);
}}
</script>

</body>
</html>
<!-- Généré le {today} — {count} notes embarquées -->
"""


def main():
    parser = argparse.ArgumentParser(description="Générer l'app mobile de révision")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    theme_dir = WIKI_ROOT / "themes" / args.theme
    print(f"Lecture des notes dues ({args.theme})...")
    notes = build_notes(theme_dir)
    print(f"  {len(notes)} notes dues trouvées")

    if not notes:
        print("Aucune note due — le fichier sera généré avec un écran vide.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html = generate_html(notes)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    size_kb = OUTPUT_FILE.stat().st_size // 1024
    print(f"Fichier généré : {OUTPUT_FILE}")
    print(f"  Taille : {size_kb} Ko")
    print(f"  Notes embarquées : {len(notes)}")


if __name__ == "__main__":
    main()
