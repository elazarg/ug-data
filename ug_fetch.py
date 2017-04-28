import urllib.parse as parse
import urllib.request as request
import sys
import json
import re
from collections import defaultdict, OrderedDict


class FILES:
    COURSE_LIST = 'output/course_list.json'
    REVERSE_KDAM = 'output/reverse_kdam.json'
    REVERSE_ADJACENT = 'output/reverse_adjacent.json'
    FACULTIES = 'metadata/faculties.txt'
    SUB_FACULTIES = 'metadata/sub_faculties.txt'
    COURSE_IDS = 'metadata/course_ids.txt'
    FAILED = 'metadata/failed.txt'


def read_lines(filename):
    with open(filename) as f:
        return tuple(line.strip() for line in f)


def write_lines(filename, iterable, callback):
    with open(filename, 'w', encoding='utf8') as out:
        for i, t in enumerate(iterable):
            print(t, file=out)
            callback(i)


FACULTIES = read_lines(FILES.FACULTIES)
SUB_FACULTIES = read_lines(FILES.SUB_FACULTIES)
COURSE_IDS = read_lines(FILES.COURSE_IDS)


def get_form(**kwargs):
    d = {
        'CNM': '',  # Course Name
        'CNO': '',  # Course ID
        'PNT': '',  # Points
        'FAC': '',  # Faculty
        'LLN': '',  # Lecturer Last Name
        'LFN': '',  # Lecturer First Name
        'SEM': '201501',  # Semester. 201?(01|02|03)
        'RECALL': 'Y',  # Something with the days
        'D1': 'on', 'D2': 'on', 'D3': 'on', 'D4': 'on', 'D5': 'on', 'D6': 'on',  # Day
        'FTM': '', 'TTM': '',  # From/To Hour HH:MM (24H format)
        'SIL': '',  # Catalogue
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
            yield str(i).zfill(2)


def enumerate_sub_faculties():
    for fac in FACULTIES:
        try:
            yield from set(x[:3] for x in get_courses_by(FAC=fac))
        except RuntimeError:
            pass


def enumerate_course_ids():
    for sub_f in SUB_FACULTIES:
        for i in range(1000):
            course_id = '{}{}'.format(sub_f, str(i).zfill(3))
            if 'Error Message' not in read_course(course_id):
                yield course_id


hebrew = ['שם מקצוע', 'מספר מקצוע', 'אתר הקורס', 'נקודות',
          'הרצאה', 'תרגיל', 'מעבדה', 'סמינר/פרויקט', 'סילבוס', 'מקצועות זהים', 'מקצועות קדם', 'מקצועות צמודים',
          'מקצועות ללא זיכוי נוסף', 'מקצועות ללא זיכוי נוסף (מכילים)', 'מקצועות ללא זיכוי נוסף (מוכלים)',
          'עבור לסמסטר', 'אחראים', 'הערות', 'מועד הבחינה', 'מועד א', 'מועד ב', 'מיקום']
irrelevant = 'move_to_semester in_charge comments exam_date exam_A exam_B location'.split()
english = 'name id site points lecture tutorial lab project syllabus identical kdam adjacent no_more no_more_contains no_more_included'.split() + irrelevant
trans = dict(zip(hebrew, english))

FAILED = frozenset(read_lines(FILES.FAILED))


def extract_info(html):
    div_fmt = r'<div class="{}">\s*(.*?)\s*</div>'
    keys = re.findall(div_fmt.format('property'), html)
    values = re.findall(div_fmt.format('property-value'), html)
    return OrderedDict(zip(keys, [re.sub('\s+', ' ', v) for v in values]))


def fix(k, v):
    data_title = r'data-original-title="(.*?)"'
    if k in ['kdam', 'adjacent']:
        return [re.findall(data_title, x) for x in v.split(' או ')]
    if k.startswith('no_more') or k in ['identical']:
        return re.findall(data_title, v)
    if k in ['site']:
        return re.search(r'href="(.*?)" ', v).group(1)
    return v


def cleanup(raw_dict):
    od = OrderedDict((trans[k], fix(trans[k], v))
                     for k, v in raw_dict.items()
                     if trans[k] not in irrelevant)
    if not od:
        return {}
    if 'points' in od:
        od.move_to_end('points', last=False)
    od.move_to_end('id', last=False)
    if 'site' in od:
        od.move_to_end('site')
    od.move_to_end('syllabus')
    return od


def fetch_course(number):
    return cleanup(extract_info(read_course(number)))


def format_json(d, fp=None):
    j = {d['id']: d}
    del d['id']
    if fp is None:
        return json.dumps(j, ensure_ascii=False)
    json.dump(j, fp, ensure_ascii=False)


def format_tsv(d):
    d = defaultdict(str, d)
    header = '{id}\t{points}\t{kdam}\t{adjacent}\t{name}'
    print(header.replace('{', '').replace('}', ''))
    print(header.format(**d))


def run_propagate(numbers):
    seen = set(FAILED)
    numbers = set(numbers) - seen
    while numbers:
        num = numbers.pop()
        seen.add(num)
        try:
            d = fetch_course(num)
            yield num, d
        except BaseException as ex:
            print('Error for id', num, type(ex))
        else:
            if d:
                courses = set(sum(d.get('kdam', []), []) + sum(d.get('adjacent', []), []) +
                              sum([d.get(x, []) for x in 'identical no_more no_more_contains no_more_included'.split()],
                                  []))
                numbers.update(courses - seen)


def run_exactly(numbers):
    for num in numbers:
        yield num, fetch_course(num)


def fetch_all_courses():
    with open(FILES.COURSE_LIST, 'w', encoding='utf8') as out, open('data/failed.txt', 'a') as failed:
        numbers = COURSE_IDS
        out.write('{\n')
        for num, d in run_exactly(numbers):
            # print(num, end=': ')
            if d:
                # print(format_json(d))
                format_json(d, out)
                out.write(',\n')
            else:
                print(num, file=failed)
                # print('non existent')
        format_json({"id": "000000"}, out)
        out.write('\n}')


if __name__ == '__main__':
    def callback(i):
        print(i, end='\r')
    if len(sys.argv) == 1:
        fetch_all_courses()
    elif sys.argv[1].isdigit():
        print(json.dumps(fetch_course(sys.argv[1]), ensure_ascii=False, indent=2))
    elif sys.argv[1] == 'metadata':
        print('Writing', FILES.FACULTIES, '...')
        write_lines(FILES.FACULTIES, enumerate_faculties(), callback)
        print('Writing', FILES.SUB_FACULTIES, '...')
        write_lines(FILES.SUB_FACULTIES, enumerate_sub_faculties(), callback)
    elif sys.argv[1] == 'course_ids':
        print('Writing', FILES.COURSE_IDS, '...')
        write_lines(FILES.COURSE_IDS, enumerate_course_ids(), callback)
