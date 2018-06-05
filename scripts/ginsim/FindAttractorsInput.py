from org.ginsim.common.callable import BasicProgressListener
import jarray
import ast

g = gs.open(gs.args[0])
sinit = gs.associated(g, "initialState", True)
perturbations = gs.associated(g, "mutant", False)
simparam = gs.associated(g, "reg2dyn_parameters", True)
model = g.getModel()
ssim = gs.service("simulation")
plist = BasicProgressListener()
sreduction = gs.service("reduction")
sscc = gs.service("SCC")

print(g.getNodeOrder())
print(sinit.getInputNodes())
#sim_idx = 0
## perform a reduction if available
#reductions = gs.associated(g, "modelSimplifier", True)
#if reductions is not None and len(reductions) > 0:
#    model = reductions[0].apply(model);
#    g = sreduction.getReconstructionTask(model, g).call()
#    sim_idx += 1 # work around the extra parameter added by the reduction step

for sp in simparam:
    #for ins in sp.getInitialState().keySet():
        #print(ins.getName())
    for ins in sp.getInputState().keySet():
        l=[]
        #print(ins.getName())
        input_1 = str(ins.getMaxValueTable())
        input_2 = input_1.strip('{}').split(', ')
        for elem in input_2:
            compound = elem.split('=')[0]
            valeur = elem.split('=')[1].strip('[]')
            #print(compound)
            if valeur == '1':
                l.append(compound)
        print(l)
        print('WT')
    stg = ssim.get(model, plist, sp).do_simulation()
#    for state in stg.getNodes():
#        outedges = stg.getOutgoingEdges(state)
#        if outedges is None or len(outedges) == 0:
#            print(state)

    # get the graph of the SCC and find attractors
    sccgraph = sscc.getSCCGraph(stg)
    for component in sccgraph.getNodes():
        out = sccgraph.getOutgoingEdges(component)
        if out is None or len(out) == 0:
            for node in component.getContent():
                print(node)
            #print
    #print("done")
