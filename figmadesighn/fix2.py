import os

DIRECTORY = r"C:\Users\user\Desktop\contract checker\wowVPN_repo\figmadesighn\src\app\pages"

FIXES = {
    r'DownНАГРУЗКА': 'Download',
    r'UpНАГРУЗКА': 'Upload',
    r'<Настройкаs': '<Settings'
}

for root, _, files in os.walk(DIRECTORY):
    for file in files:
        if file.endswith(".tsx"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for bad, good in FIXES.items():
                content = content.replace(bad, good)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
print("Syntax artifacts fixed again.")
