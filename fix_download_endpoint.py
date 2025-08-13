import re

# Leggi il file main_dev.py
with open('main_dev.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Sostituisci la riga problematica nell'endpoint download_recall
pattern = r'if not user or user\.get\(\'role\'\) != \'company\' or user\.get\(\'company_id\'\) != company_id:'
replacement = 'if not user or user.get(\'role\') != \'company\':'

content = re.sub(pattern, replacement, content)

# Scrivi il file corretto
with open('main_dev.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Endpoint download_recall corretto!")
