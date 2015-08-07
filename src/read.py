import json
import itertools as it
from collections import defaultdict

COURSE_LIST_FILENAME = 'course_list.json'
REVERSE_KDAM_FILENAME = 'reverse_kdam.json'
REVERSE_ADJACENT_FILENAME = 'reverse_adjacent.json'

def read_json_to_dict(filename=COURSE_LIST_FILENAME):
    with open(filename, encoding='utf8') as f:
        return json.load(f)


def flatten(v, field):
    return sum(v.get(field, []), [])


def to_jsonable(d):
    return {k:list(sorted(set(v))) for k,v in d.items()}


def multidict(pairs):
    res = defaultdict(list)
    for k, v in it.chain.from_iterable(pairs):
        res[k].append(v)
    return to_jsonable(res)


def merge_mutildicts(d1, d2):
    res = defaultdict(list, d1)
    for (k, v) in d2.items():
        res[k] += v
    return to_jsonable(res)


def multidict_to_pairs(d):
    return it.chain.from_iterable(it.product([k], v) for k,v in d.items())

def get_reverse_kdam_from_course_list(field='kdam', filename=COURSE_LIST_FILENAME):
    d = read_json_to_dict(filename)
    return multidict(it.product(flatten(v, field), [k])
                        for k, v in d.items())


def read_kdam_and_adjacent():
    kdams = read_json_to_dict(REVERSE_KDAM_FILENAME)
    adjacents = read_json_to_dict(REVERSE_ADJACENT_FILENAME)
    return merge_mutildicts(kdams, adjacents)


def dump_json_kdam(d):
    s = ',\n'.join('{}: {}'.format(repr(k), repr(v)) for k,v in sorted(d.items()))
    return ('{\n%s\n}' % s.replace("'", '"'))


def print_to_file(filename, field):
    with open(filename, 'w') as f:
        f.write(dump_json_kdam(get_reverse_kdam_from_course_list(field)))
        
if __name__ == '__main__':
    for k, v in multidict_to_pairs(read_json_to_dict(REVERSE_ADJACENT_FILENAME)):
        if k.startswith('234') or v.startswith('234'):
            k, v = int(k), int(v)
            print('{', 'from: {}, to: {}, arrows: "to",  dashes:true'.format(k, v), '},')
        
