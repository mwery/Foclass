from org.ginsim.common.callable import BasicProgressListener
import jarray
import ast, sys

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

def findstablestate(model, coreNodes, maxvalues, unfoldNodes, coreOrder, nodes, envt, inputs):
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

        state = list(state)

        """ Ne recupere que les SS dont les valeurs des inputs sont de 1 """
        #print(nodes)
        #print(envt)
        #print(list(inputs))

        inp = False  # valeur de l'input

        for input in list(inputs) :
            input = str(input)
            index = nodes.index(input)
            # print(input)
            # print(state[index])
            if input in envt and state[index] == '1' :
                inp = True
            elif input in envt and state[index] == '0' :
                inp = False
                break
            if input not in envt and state[index] == '0' :
                inp = True
            elif input not in envt and state[index] == '1' :
                inp = False
                break

        # print("inp")
        # print(inp)
        #print("inp_out")
        #print(inp_out)

        if inp :
            print(''.join(state))

        # input_index = ['0']*len_input
        # print(input_index)
        # sys.exit()
        #
        # for i in index:
        #     input_index[i] = '1'
        #
        # input_list = state[:len_input]
        #
        # if input_index == input_list:
        #     print(''.join(state))


""" Ne recupere que les SS dont les environnements input ont ete specifies """

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

node = str(nodeOrder).strip('[]').split(', ')



for input_name, envt in dico_input.items():

    print(envt)

#    findstablestate(model, coreNodes, maxvalues, unfoldNodes, coreOrder, index_input, len(node_input))
#print(proteines)
    #print(index_input)

    print("WT")
    findstablestate(model, coreNodes, maxvalues, unfoldNodes, coreOrder, node, envt, node_input)
    #print

    # if perturbations:
    #     for perturb in perturbations:
    #         print(perturb)
    #         pert_model = perturb.apply(model)
    #         findstablestate(pert_model, coreNodes, maxvalues, unfoldNodes, coreOrder, node, envt, node_input)
