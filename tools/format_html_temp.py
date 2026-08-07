from pathlib import Path
from bs4 import BeautifulSoup

for rel in [
    'site/pages/tut-02-03-students.html',
    'site/pages/tut-04-students.html',
]:
    path = Path(rel)
    text = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(text, 'html5lib')
    path.write_text(soup.prettify(), encoding='utf-8')
    print('formatted', path)
