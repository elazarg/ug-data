import networkx as nx

import src.read as read

data = read.get_reverse_kdam_from_course_list()
d = nx.DiGraph([(k,v) for k,v in read.multidict_to_pairs(read.read_json_to_dict(read.REVERSE_KDAM_FILENAME))
                if k.startswith('23') or v.startswith('23')])
nx.draw(d)