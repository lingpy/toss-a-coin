import random
from lingpy import *
import tqdm
from sys import argv
from lingpy.compare.sanity import synonymy

def clone(wordlist, blacklist=None):
    blacklist = blacklist or []
    D = {idx: [h for h in wordlist[idx]] for idx in wordlist if idx not in blacklist}
    D[0] = [c for c in wordlist.columns]
    return Wordlist(D)

name = argv[1][:-4]
if '/' in name: name = name.split('/')[-1]

wl = Wordlist(argv[1])
syns = synonymy(wl)
for t in wl.cols:
    synum = len([x for x in syns if x[0] == t and syns[x] > 1])
    print('{0:25}  {1}'.format(t, synum))
print('{0:2}'.format(sum(syns.values()) / len(syns)))

wl.calculate('tree', tree_calc='neighbor', distances=True)
tree = Tree(str(wl.tree))
trees, distances = [], []
etd = wl.get_etymdict(ref='concept')
samples = set()
t = tqdm.trange(1000)
all_dists = []
for i in t:
    t.update()
    # iterate to erase the superfluous words
    blacklist = set()
    for key, vals in etd.items():
        for v in vals:
            if v and len(v) > 1:
                keep = random.choice(v)
                for element in v:
                    if element != keep:
                        blacklist.add(element)
    nwl = clone(wl, blacklist)
    # check whether the sampled list has already occurred
    sample = tuple([idx for idx in nwl])
    if sample in samples:
        pass
    else:
        samples.add(sample)
        nwl.calculate('tree', tree_calc='neighbor', distances=True)
        trees += [str(nwl.tree)]
    
        new_tree = Tree(str(nwl.tree))
        dist = tree.get_distance(new_tree)
        distances += [dist]
    
        if not i % 10:
            for j in range(10):
                all_dists += [Tree(random.choice(trees)).get_distance(new_tree)]

            ad = sum(all_dists) / len(all_dists)
            t.set_postfix({'GRF': '{1:.2f})'.format(i, 100 * ad)})


 
print('Sampled average distances: {0:.2f}'.format(sum(all_dists) / len(all_dists)))
print('Distances compared to dataset with synonyms: {0:.2f}'.format(sum(distances) / len(distances)))

with open('results/'+name+'-trees.nwk', 'w') as f:
    f.write('\n'.join(trees))
