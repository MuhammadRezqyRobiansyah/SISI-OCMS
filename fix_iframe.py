import re

with open(r'c:\flow process overhaul component\sis\resources\views\overhauls\show.blade.php', 'r', encoding='utf-8') as f:
    content = f.read()

# I messed up the replacement. Let's fix the block from "DISASSEMBLY CHECK S" to the end of the script tag.
pattern = re.compile(r'<div class="section-title fade-up">DISASSEMBLY CHECK S.*?</script>', re.DOTALL)
replacement = """<div class="glass-card fade-up" style="padding: 0; overflow: hidden; height: 900px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
            <iframe 
                src="https://docs.google.com/spreadsheets/d/1kIjBP4R4MWPkpFzXIU7Smcwnyy2DoR2Pzj2oggmn3tY/edit?usp=sharing&rm=minimal"
                style="width: 100%; height: 100%; border: none;"
                allowfullscreen>
            </iframe>
        </div>"""

new_content = pattern.sub(replacement, content)

with open(r'c:\flow process overhaul component\sis\resources\views\overhauls\show.blade.php', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed")
