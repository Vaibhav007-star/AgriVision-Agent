"""
Build standalone static presentation deck for Netlify Drop and GitHub Pages.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_TEMPLATE = BASE_DIR / "app" / "templates" / "presentation.html"
PPTX_SOURCE = BASE_DIR / "docs" / "AgriVision_Agent_Presentation.pptx"

DIST_DIR = BASE_DIR / "dist-presentation"
DOCS_DIR = BASE_DIR / "docs"

DIST_DIR.mkdir(parents=True, exist_ok=True)

with open(SOURCE_TEMPLATE, "r", encoding="utf-8") as f:
    content = f.read()

# Make links fully standalone and relative
content = content.replace('href="/download/pptx"', 'href="./AgriVision_Agent_Presentation.pptx"')
content = content.replace(
    'href="/" class="px-2.5 py-1 rounded-md bg-lime-500/20 border border-lime-500/40 text-lime-300 hover:bg-lime-500/30 text-xs font-semibold flex items-center gap-1 transition-all">',
    'href="https://github.com/Vaibhav007-star/AgriVision-Agent" target="_blank" title="GitHub Code Repository" class="px-2.5 py-1 rounded-md bg-lime-500/20 border border-lime-500/40 text-lime-300 hover:bg-lime-500/30 text-xs font-semibold flex items-center gap-1 transition-all">'
)
content = content.replace("<span>Open App</span>", "<span>GitHub Repo</span>")
content = content.replace(
    'href="/" target="_blank" class="px-4 py-2 rounded-lg bg-lime-500 hover:bg-lime-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow-lg shadow-lime-500/20">',
    'href="https://github.com/Vaibhav007-star/AgriVision-Agent" target="_blank" class="px-4 py-2 rounded-lg bg-lime-500 hover:bg-lime-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow-lg shadow-lime-500/20">'
)
content = content.replace("<span>Launch Live App</span>", "<span>View GitHub Repo</span>")

# Write to dist-presentation/index.html
with open(DIST_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(content)

# Write to docs/index.html (for GitHub Pages compatibility)
with open(DOCS_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(content)

# Copy PPTX to dist-presentation
import shutil
shutil.copy2(PPTX_SOURCE, DIST_DIR / "AgriVision_Agent_Presentation.pptx")

# Add _redirects for Netlify
with open(DIST_DIR / "_redirects", "w", encoding="utf-8") as f:
    f.write("/*    /index.html   200\n")

print(f"[+] Successfully built standalone presentation deck in {DIST_DIR}")
print(f"[+] Files in dist-presentation: {list(DIST_DIR.glob('*'))}")
