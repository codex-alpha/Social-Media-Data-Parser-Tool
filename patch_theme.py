import re
import os

with open("frontend/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

# Replace :root variables completely
root_pattern = re.compile(r':root\s*\{[^}]+\}', re.MULTILINE)

new_root = """:root {
  /* Color Palette - Earthy Palette */
  --bg-primary: #F0D8A1;
  --bg-secondary: rgba(255, 255, 255, 0.4);
  --bg-tertiary: #DD9E59;
  --bg-card: rgba(255, 255, 255, 0.6);
  --bg-glass: rgba(255, 255, 255, 0.4);
  --bg-hover: rgba(221, 158, 89, 0.2);

  --border-primary: rgba(164, 114, 81, 0.4);
  --border-glow: rgba(221, 158, 89, 0.5);
  --border-subtle: rgba(164, 114, 81, 0.15);

  --text-primary: #4a301f;
  --text-secondary: #A47251;
  --text-muted: #8c5b3c;
  --text-accent: #DD9E59;

  --accent-blue: #DD9E59;
  --accent-cyan: #DCF0C3;
  --accent-purple: #A47251;
  --accent-pink: #DD9E59;
  --accent-green: #DCF0C3;
  --accent-amber: #DD9E59;
  --accent-red: #A47251;
  --accent-orange: #DD9E59;

  --gradient-blue: linear-gradient(135deg, #DD9E59, #A47251);
  --gradient-purple: linear-gradient(135deg, #A47251, #DD9E59);
  --gradient-green: linear-gradient(135deg, #DCF0C3, #DD9E59);
  --gradient-red: linear-gradient(135deg, #A47251, #DD9E59);
  --gradient-amber: linear-gradient(135deg, #DD9E59, #A47251);

  --shadow-sm: 0 1px 3px rgba(164, 114, 81, 0.15);
  --shadow-md: 0 4px 12px rgba(164, 114, 81, 0.2);
  --shadow-lg: 0 8px 32px rgba(164, 114, 81, 0.25);
  --shadow-glow-blue: 0 0 20px rgba(221, 158, 89, 0.2);
  --shadow-glow-purple: 0 0 20px rgba(164, 114, 81, 0.2);

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
}"""

css = root_pattern.sub(new_root, css)

# Map hex to hex
hex_replacements = {
    "#3b82f6": "#DD9E59",
    "#06b6d4": "#DCF0C3",
    "#8b5cf6": "#A47251",
    "#ec4899": "#DD9E59",
    "#10b981": "#DCF0C3",
    "#f59e0b": "#DD9E59",
    "#ef4444": "#A47251",
    "#f97316": "#DD9E59",
    "#1DA1F2": "#DD9E59",
    "#E1306C": "#A47251",
    "#1877F2": "#DD9E59",
    "#FF4500": "#A47251",
    "#ff6b6b": "#A47251"
}

# Map rgb to rgb
rgb_replacements = {
    # Blue
    r"59,\s*130,\s*246": "221, 158, 89",
    # Cyan
    r"6,\s*182,\s*212": "220, 240, 195",
    # Purple
    r"139,\s*92,\s*246": "164, 114, 81",
    # Green
    r"16,\s*185,\s*129": "220, 240, 195",
    # Amber
    r"245,\s*158,\s*11": "221, 158, 89",
    # Red
    r"239,\s*68,\s*68": "164, 114, 81",
    # Orange
    r"249,\s*115,\s*22": "221, 158, 89",
    # White used for light text bindings or subtle lines -> Brown lines
    r"255,\s*255,\s*255,\s*0\.06": "164, 114, 81, 0.15",
    # platform colors
    r"29,\s*161,\s*242": "221, 158, 89",
    r"225,\s*48,\s*108": "164, 114, 81",
    r"24,\s*119,\s*242": "221, 158, 89",
    r"255,\s*69,\s*0": "164, 114, 81"
}


for old_hex, new_hex in hex_replacements.items():
    css = re.sub(old_hex, new_hex, css, flags=re.IGNORECASE)

for old_rgb, new_rgb in rgb_replacements.items():
    css = re.sub(old_rgb, new_rgb, css)

# Fix background body pulse and elements that relied on dark theme
css = re.sub(r'color:\s*white;', 'color: var(--text-primary);', css)
css = re.sub(r'color:\s*#fff;', 'color: var(--text-primary);', css)

with open("frontend/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Updated index.css")

# process App.jsx and components just in case
def process_js(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    modified = file_content
    for old_hex, new_hex in hex_replacements.items():
        modified = re.sub(old_hex, new_hex, modified, flags=re.IGNORECASE)
    
    if modified != file_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified)
        print(f"Updated {filepath}")

for root, _, files in os.walk("frontend"):
    if "node_modules" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith(".jsx") or file.endswith(".js") or file.endswith(".ts") or file.endswith(".tsx"):
            process_js(os.path.join(root, file))

