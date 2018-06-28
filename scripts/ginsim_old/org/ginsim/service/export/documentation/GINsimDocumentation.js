//<![CDATA[

function nodeClicked() {

    if (shape != undefined) {
        if (oldstyle) {
            shape.attr("style", oldstyle)
        } else {
            shape.attr("style", "")
        }
    }

    shape = $("#"+this.id+"_shape", $(this))
    oldstyle = shape.attr("style")
    shape.attr("style", "fill:#1f1;stroke:#000")
    info = nodes[this.id]


    infodiv = $("#infodiv")
    infodiv.text("")

    showFunctions(info, infodiv)

    curEdges = relEdges[this.id]
    if (curEdges[0].length > 0) {
        edgediv = $("<p>")
        edgediv.append("<b>Targets:</b>")

        for (idx in curEdges[0]) {
            e = curEdges[0][idx]
            edgediv.append(" <a href='#' onclick='edgeInfo(\""+e+"\"); return false'>"+edges[e].to+"</a>")
        }
        infodiv.append(edgediv)
    }
    if (curEdges[1].length > 0) {
        edgediv = $("<p>")
        edgediv.append("<b>Regulators:</b>")

        for (idx in curEdges[1]) {
            e = curEdges[1][idx]
            edgediv.append(" <a href='#' onclick='edgeInfo(\""+e+"\"); return false'>"+edges[e].from+"</a>")

        }
        infodiv.append(edgediv)
    }

    infodiv.append("<div id='edgeinfo'></div>")

    showComments(info, infodiv)

    timestamp = new Date().getTime()
}

function showFunctions(info, infodiv) {
    if ("input" in info && info["input"]) {
        infodiv.append("<p><b>Input node</b>")
    } else {
        infodiv.append("<p><b>TODO: functions</b>")
    }
}

function showComments(info, infodiv) {

    if ("links" in info) {
        links = info["links"]
        hlinks = $("<ul>")
        for (idx in links) {
            lnk = links[idx]
            hlinks.append("<li><a href='"+lnk[1]+"'>"+lnk[0]+"</a></li>")
        }
        infodiv.append(hlinks)
    }

    if ("comment" in info) {
        infodiv.append(info["comment"])
    }

}


function showGraph() {
    tdiv = $("#tableView")
    tdiv.hide();

    bgClicked()
    cdiv = $("#graphView")
    cdiv.show();
}


function showTable() {
    cdiv = $("#graphView")
    cdiv.hide();
    tdiv = $("#tableView")
    tdiv.text("").show()

    table = $("<table></table>")
    table.append("<tr><th>Node</th><th>Function</th><th>Comment</th></tr>")


    for (k in nodes) {
        info = nodes[k]
        line = $("<tr><th>"+k+"</th></tr>")
        cell = $("<td></td>")
        showFunctions(info, cell)
        line.append(cell)
        cell = $("<td></td>")
        commentDiv = $("<div class='comment'></div>")
        showComments(info, commentDiv)
        cell.append(commentDiv)

        curEdges = relEdges[k]
        if (curEdges[1].length > 0) {
            regTable = $("<table>")
            for (idx in curEdges[1]) {
                e = curEdges[1][idx]
                regLine = $("<tr><th>"+edges[e].from+"</th></tr>")
                regCell = $("<td></td>")
                showComments(edges[e], regCell)
                regLine.append(regCell)
                regTable.append(regLine)
            }
            regDiv = $("<div class='regulators'><b>Regulators:</b></div>")
            regDiv.append(regTable)
            cell.append(regDiv)
        }
        line.append(cell)
        table.append(line)
    }

    tdiv.append(table)
}


function edgeInfo(id) {
    infodiv = $("#edgeinfo")
    infodiv.text("")
    ediv = $("<div></div>")
//  showComments(edges[id], ediv)
//  ediv.append("TODO: edge info for "+id)
    infodiv.append(ediv)
}

function bgClicked() {
    newstamp = new Date().getTime()
    if (newstamp - timestamp < 100) {
        return
    }

    if (shape != undefined) {
        if (oldstyle) {
            shape.attr("style", oldstyle)
        } else {
            shape.attr("style", "")
        }
    }

    infodiv = $("#infodiv")
    infodiv.text("")
    info = model
    infodiv.append("<b>Name:</b> "+info["name"])
    infodiv.append("<br/>"+nbnodes+" Components")
    infodiv.append("<br/>"+nbedges+" Interactions")
    if ("links" in info) {
        links = info["links"]
        hlinks = $("<ul>")
        for (idx in links) {
            hlinks.append("<li>"+links[idx]+"</li>")
        }
        infodiv.append(hlinks)
    }

    if ("comment" in info) {
        infodiv.append(info["comment"])
    }
}



function onload() {

    var container = document.getElementById("container");
    var subdoc = container.getSVGDocument()

    svgroot = $(subdoc)
    $("svg", svgroot).click(bgClicked)
    nbnodes = 0
    for (k in nodes) {
        $("#"+k, svgroot).click(nodeClicked)
        relEdges[k] = [ [], [] ]
        nbnodes++
    }


    nbedges = 0
    for (e in edges) {
        edge = edges[e]
        relEdges[edge.from][0].push(e)
        relEdges[edge.to][1].push(e)
        nbedges++
    }

    showGraph()
}


shape = undefined
relEdges = {}
timestamp = new Date().getTime() - 200;
$(window).load(onload);


//]]>