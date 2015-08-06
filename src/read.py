import json
import itertools as it
from collections import defaultdict

COURSE_LIST_FILENAME = 'course_list.json'
REVERSE_KDAM_FILENAME = 'reverse_kdam.json'


def read_json_to_dict(filename=COURSE_LIST_FILENAME):
    with open(filename, encoding='utf8') as f:
        return json.load(f)


def get_reverse_kdam_from_course_list():
    d = read_json_to_dict()
    rev_kdam_pairs = (it.product(sum(v.get('kdam', []), []), [k])
                      for k,v in d.items())
    res = defaultdict(set)
    for k, v in it.chain.from_iterable(rev_kdam_pairs):
        res[k].add(v)
    return {k:list(v) for k,v in res.items()}

if __name__ == '__main__':
    print(read_json_to_dict(REVERSE_KDAM_FILENAME))