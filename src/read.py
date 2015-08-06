import json
import itertools as it
from collections import defaultdict

COURSE_LIST_FILENAME = 'course_list.json'
REVERSE_KDAM_FILENAME = 'reverse_kdam.json'


def read_json_to_dict(filename=COURSE_LIST_FILENAME):
    with open(filename, encoding='utf8') as f:
        return json.load(f)


def flatten(v, field):
    val = v.get(field, [])
    return sum(val, [])


def reverse_dict(pairs):
    res = defaultdict(set)
    for k, v in it.chain.from_iterable(pairs):
        res[v].add(k)
    return {k:list(v) for k,v in res.items()}


def get_reverse_kdam_from_course_list(field='kdam', filename=COURSE_LIST_FILENAME):
    d = read_json_to_dict(filename)
    return reverse_dict(it.product([k], flatten(v, field))
                        for k, v in d.items())


if __name__ == '__main__':
    print(get_reverse_kdam_from_course_list('adjacent'))
