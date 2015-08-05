import re
from collections import defaultdict, OrderedDict
import json
from crowler import read_course, COURSE_IDS, read_lines

hebrew = ['שם מקצוע', 'מספר מקצוע', 'אתר הקורס', 'נקודות', 
          'הרצאה', 'תרגיל', 'מעבדה', 'סמינר/פרויקט', 'סילבוס',  'מקצועות זהים','מקצועות קדם','מקצועות צמודים', 'מקצועות ללא זיכוי נוסף', 'מקצועות ללא זיכוי נוסף (מכילים)' ,'מקצועות ללא זיכוי נוסף (מוכלים)',
          'עבור לסמסטר', 'אחראים', 'הערות','מועד הבחינה', 'מועד א', 'מועד ב', 'מיקום']
irrelevant = 'move_to_semester in_charge comments exam_date exam_A exam_B location'.split()
english = 'name id site points lecture tutorial lab project syllabus identical kdam adjacent no_more no_more_contains no_more_included'.split() + irrelevant
trans = dict(zip(hebrew, english))


failed = frozenset(read_lines('failed.txt'))


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
    return OrderedDict((trans[k], fix(trans[k], v)) 
                       for k,v in raw_dict.items() 
                       if trans[k] not in irrelevant)


def fetch_course(number):
    return cleanup(extract_info(read_course(number)))


def format_json(d, fp=None):
    if fp is None:
        return json.dumps(d, ensure_ascii=False)
    json.dump(d, fp, ensure_ascii=False)


def format_tsv(d):
    d = defaultdict(str, d)
    header = '{id}\t{points}\t{kdam}\t{adjacent}\t{name}'
    print(header.replace('{','').replace('}',''))
    print(header.format(**d))


def run(numbers):
    numbers = set(numbers) - failed
    seen = set()
    while numbers:
        num = numbers.pop()
        seen.add(num)
        try:
            d = fetch_course(num)
            yield num, d
            if d:
                courses = set(sum(d.get('kdam',[]), []) + sum(d.get('adjacent', []), []) + 
                              sum([d.get(x, []) for x in 'identical no_more no_more_contains no_more_included'.split()], [])) 
                numbers.update(courses - seen)
        except:
            print('Error for id', num)


def main():
    with open('course_list.txt', 'w', encoding='utf8') as out, open('failed.txt', 'a') as failed:
        numbers = COURSE_IDS
        for num, d in run(numbers):
            #print(num, end=': ')
            if d:
                #print(format_json(d))
                format_json(d, out)
                out.write('\n')
            else:
                print(num, file=failed)
                #print('non existent')

if __name__ == '__main__':
    main()
