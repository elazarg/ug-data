import re
from collections import defaultdict, OrderedDict
import json
from .crawler import read_course, COURSE_IDS, read_lines
from .read import COURSE_LIST_FILENAME

hebrew = ['שם מקצוע', 'מספר מקצוע', 'אתר הקורס', 'נקודות',
          'הרצאה', 'תרגיל', 'מעבדה', 'סמינר/פרויקט', 'סילבוס', 'מקצועות זהים', 'מקצועות קדם', 'מקצועות צמודים', 'מקצועות ללא זיכוי נוסף', 'מקצועות ללא זיכוי נוסף (מכילים)' , 'מקצועות ללא זיכוי נוסף (מוכלים)',
          'עבור לסמסטר', 'אחראים', 'הערות', 'מועד הבחינה', 'מועד א', 'מועד ב', 'מיקום']
irrelevant = 'move_to_semester in_charge comments exam_date exam_A exam_B location'.split()
english = 'name id site points lecture tutorial lab project syllabus identical kdam adjacent no_more no_more_contains no_more_included'.split() + irrelevant
trans = dict(zip(hebrew, english))


FAILED = frozenset(read_lines('data/failed.txt'))


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
    j = {d['id']:d}
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
                              sum([d.get(x, []) for x in 'identical no_more no_more_contains no_more_included'.split()], [])) 
                numbers.update(courses - seen)


def run_exactly(numbers):
    for num in numbers:
        yield num, fetch_course(num)
        
def main():
    with open(COURSE_LIST_FILENAME, 'w', encoding='utf8') as out, open('data/failed.txt', 'a') as FAILED:
        numbers = COURSE_IDS
        out.write('{\n')
        for num, d in run_exactly(numbers):
            # print(num, end=': ')
            if d:
                # print(format_json(d))
                format_json(d, out)
                out.write(',\n')
            else:
                print(num, file=FAILED)
                # print('non existent')
        format_json({"id":"000000"}, out)
        out.write('\n}')

if __name__ == '__main__':
    main()
