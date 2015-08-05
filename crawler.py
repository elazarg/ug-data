import urllib.request as request
import urllib.parse as parse
import re

def read_lines(filename):
    with open(filename) as f:
        return tuple(line.strip() for line in f)


def write_lines(filename, iterable):
    with open(filename, 'w', encoding='utf8') as out:
        for t in iterable:
            print(t, file=out)


FACULTIES = read_lines('faculties.txt')
SUB_FACULTIES = read_lines('sub_faculties.txt')
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
    

def read_course(number):
    return fetch("https://ug3.technion.ac.il/rishum/course/{}".format(number))


def get_courses_by(**kwargs):
    d = get_form(**kwargs)
    URL = 'https://ug3.technion.ac.il/rishum/search'
    data = bytes(parse.urlencode(d), encoding='utf8')
    with request.urlopen(URL, data=data) as w:
        html = w.read().decode('utf8')
        #print(html)
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
            yield str(i).zfill(2)

def enumerate_sub_faculties():
    for fac in FACULTIES:
        try:
            yield from set(x[:3] for x in get_courses_by(FAC=fac))
        except RuntimeError:
            pass

def enumerate_courses(): 
    for sub_f in SUB_FACULTIES:
        for i in range(1000):
            course_id = '{}{}'.format(sub_f, str(i).zfill(3))
            if 'Error Message' not in read_course(course_id):
                yield course_id

