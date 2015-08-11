import json
import itertools as it
from collections import defaultdict
import textwrap
from itertools import chain

COURSE_LIST_FILENAME = 'course_list.json'
REVERSE_KDAM_FILENAME = 'reverse_kdam.json'
REVERSE_ADJACENT_FILENAME = 'reverse_adjacent.json'

def read_json_to_dict(filename=COURSE_LIST_FILENAME):
    with open(filename, encoding='utf8') as f:
        return json.load(f)


def flatten(v, field):
    return sum(v.get(field, []), [])


def to_jsonable(d):
    return {k:list(sorted(set(v))) for k, v in d.items()}


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
    return it.chain.from_iterable(it.product([k], v) for k, v in d.items())

def get_reverse_kdam_from_course_list(field='kdam', filename=COURSE_LIST_FILENAME):
    d = read_json_to_dict(filename)
    return multidict(it.product(flatten(v, field), [k])
                        for k, v in d.items())


def read_kdam_and_adjacent():
    kdams = read_json_to_dict(REVERSE_KDAM_FILENAME)
    adjacents = read_json_to_dict(REVERSE_ADJACENT_FILENAME)
    return merge_mutildicts(kdams, adjacents)


def dump_json_kdam(d):
    s = ',\n'.join('{}: {}'.format(repr(k), repr(v)) for k, v in sorted(d.items()))
    return ('{\n%s\n}' % s.replace("'", '"'))


def print_to_file(filename, field):
    with open(filename, 'w') as f:
        f.write(dump_json_kdam(get_reverse_kdam_from_course_list(field)))

def is_cs(cid):
    return 234000 <= int(cid) <= 236999

def nodes_to_visDataSet(fp):
    from functools import partial
    
    pr = partial(print, file=fp)
    pr('var nodes = new vis.DataSet([')
    edges = defaultdict(set)
    d = read_json_to_dict(filename=COURSE_LIST_FILENAME)
    for cid, details in sorted(d.items()):
        cid = int(cid)
        if not is_cs(cid):
            continue
        for k in details.get('kdam', []):
            if len(k) > 1:
                dummy = 1000000 + sum(map(int, k))
                if dummy not in edges:
                    pr('{', 'id:"{}", group: 9, hidden: true'.format(dummy), '},')
                edges[dummy].add(cid)
                for p in k:
                    edges[p].add(dummy)
            else:
                edges[k[0]].add(cid)
    for cid in {int(x) for x in (set(chain.from_iterable(edges.values())) | set(edges))}:
        cid = int(cid)
        if cid < 1000000:
            details = d.get(str(cid).zfill(6))
            if details is None:
                pr('{', 'id:"{0}", group: 10, label: {0}, title: "{0}", mass:1'.format(cid), '},')
            else:
                name = repr(textwrap.fill(details['name'], 25))
                pr('{', 'id:"{}", group: {g}, label: {name}, title: "{number}"'.format(
                       cid, g=str(cid)[-4], name=name, number=cid), '},')
    pr(']);')
    
    pr('var edges = new vis.DataSet([')
    for cid, v in multidict_to_pairs(edges):
        pr('{', 'from: {}, to: {}'.format(cid, v), '},')
    pr(']);')

if __name__ == '__main__':
    with open(r'..\ug-data-vis\data.js', 'w', encoding='utf8') as fp:
        nodes_to_visDataSet(fp)
