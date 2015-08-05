import urllib.request as request
import urllib.parse as parse
import re
import itertools

def read_lines(filename):
    with open(filename) as f: return tuple(line.strip() for line in f)

FACULTIES = read_lines('faculties.txt')
COURSE_IDS = read_lines('course_ids.txt') 

def get_form(**kwargs):
    d = {
        'CNM': '',  # Course Name
        'CNO': '',  # Course ID
        'PNT': '',  # Points
        'FAC': '',  # Faculty
        'LLN': '',  # Lecturer Last Name
        'LFN': '',  # Lecturer First Name
        'SEM': '201501',  # Semester. 201?(01|02|03)
        'RECALL':'Y',  # Something with the days
        'D1': 'on', 'D2': 'on', 'D3': 'on', 'D4': 'on', 'D5': 'on', 'D6': 'on',  # Day
        'FTM':'', 'TTM':'',  # From/To Hour HH:MM (24H format)
        'SIL':'',  # Catalogue
        'OPTCAT': 'on',  # הצג נתונים קבועים מקטלוג
        'OPTSEM': 'on',  # Semesterial Info
        'OPTSTUD': 'off',  # Only active in this semester
        'doSearch': 'Y',  #
    }
    d.update(kwargs)
    return d


def fetch(url):
    with request.urlopen(url) as w:
        return w.read().decode('utf8')
    
    
def get_courses_by(**kwargs):
    d = get_form(**kwargs)
    URL = 'https://ug3.technion.ac.il/rishum/search'
    data = bytes(parse.urlencode(d), encoding='utf8')
    with request.urlopen(URL, data=data) as w:
        html = w.read().decode('utf8')
        # print(html)
    if 'class="error-msg"' in html:
        raise RuntimeError('Bad results for ' + str(kwargs))
    return re.findall(r'>(\d{6})</a>', html)


def enumerate_faculties():
    for i in range(100):
        try:
            get_courses_by(FAC=i)
        except:
            pass
        else:
            print(str(i).zfill(2))


def enumerate_courses():
    cs = set(itertools.chain.from_iterable(get_courses_by(FAC=fac) for fac in FACULTIES)) 
    with open('course_ids.txt', 'w') as out:
        for c in sorted(cs):
            print(c, file=out)
