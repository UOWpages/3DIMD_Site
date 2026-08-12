from pathlib import Path
import zipfile
import re
import sys

path = Path('docx/Tut 07 UI Overview.docx')
if not path.exists():
    print('FILE_NOT_FOUND')
    sys.exit(1)

with zipfile.ZipFile(path) as z:
    data = z.read('word/document.xml').decode('utf-8')

text = re.sub(r'<w:t[^>]*>(.*?)</w:t>', lambda m: m.group(1), data, flags=re.S)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:40000])
