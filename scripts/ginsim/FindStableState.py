from org.ginsim.common.callable import BasicProgressListener
import jarray

def unfold(values, maxvalues, stack, coreNodes):
    n = len(values)
    jokers = [ (idx, maxvalues[idx]+1) for idx in xrange(n) if values[idx] == -1 ]
    unfold_rec(values, jokers, stack, coreNodes)

    return stack


def copy_path(values, coreNodes):
    n = len(coreNodes)
    path = jarray.zeros(n, 'b')
    i = 0
    for idx in coreNodes:
        path[i] = values[idx]
        i += 1

    return path


def unfold_rec(values, jokers, stack, coreNodes):
    if len(jokers) < 1:
        path = copy_path(values, coreNodes)
        if False:
            for p in stack:
                idx = 0
                ident = True
                for v in p:
                    if v != path[idx]:
                        ident = False
                        break
                    idx += 1
                if ident:
                    return
        stack.append( path )
        return

    idx, mx = jokers[0]
    njk = jokers[1:]
    for v in xrange(mx):
        values[idx] = v
        unfold_rec(values, njk, stack, coreNodes)
    values[idx] = -1

def findstablestate(model, coreNodes, maxvalues, unfoldNodes, coreOrder):
    searcher = ssrv.getStableStateSearcher(model)
    searcher.call()
    paths = searcher.getPaths()
    values = paths.getPath()
    stack = []
    for l in paths:
        path = copy_path(values, coreNodes)
        #stack.append(l)
        unfold(path, maxvalues, stack, unfoldNodes)

    for path in stack:
        name = istates.nameState(path, coreOrder)
        if name is None:
            name = ""
        state = ""
        for v in path:
            if v < 0: state += "*"
            else: state += "%d" % v
        print(state)



g = gs.open(gs.args[0])
inits = gs.associated(g, "initialState", True)
istates = inits.getInitialStates()
ssrv = gs.service("stable")
model = g.getModel()
perturbations = gs.associated(g, 'mutant', False)
simul_parameters = gs.associated(g, 'reg2dyn_parameters', True)

dico_input = {}

for sp in simul_parameters:
    for ins in sp.getInputState().keySet():
        name_input = ins.getName()
        dico_input[str(name_input)] = []
        input_1 = str(ins.getMaxValueTable())
        input_2 = input_1.strip('{}').split(', ')
        for elem in input_2:
            proteine = elem.split('=')[0]
            valeur = elem.split('=')[1].strip('[]')
            if valeur == '1':
                dico_input[name_input].append(proteine)

#print(dico_input)


nodeOrder = g.getNodeOrder()
node_input = inits.getInputNodes()

print(nodeOrder)
print(node_input)

maxvalues = []
coreNodes = []
inputNodes = []
coreOrder = []
idx = 0
for n in nodeOrder:
    coreNodes.append(idx)
    coreOrder.append(n)
    maxvalues.append( n.getMaxValue() )
    idx += 1
unfoldNodes = xrange(len(coreNodes))

print("WT")
findstablestate(model, coreNodes, maxvalues, unfoldNodes, coreOrder)

if perturbations:
    for perturb in perturbations:
        print(perturb)
        pert_model = perturb.apply(model)
        findstablestate(pert_model, coreNodes, maxvalues, unfoldNodes, coreOrder)
