var tableData = new Object();
window.onload = function () {
	addProperClassToSummaryTable();
	moveReportTablesInSummary();
}

function addProperClassToSummaryTable() {
	document.getElementsByTagName("table")[0].className = 'summary';
}

function moveReportTablesInSummary() {
	h4s = document.getElementsByTagName('h4');
	for (var i = 0 ; i < h4s.length ; i++) {
		h4 = h4s[i];
		table = nextSiblingOfType(h4, 'table');
		table.id = h4.innerHTML.replace(/^.*?(\w+) -.*? (\w+).*?$/, '$1__$2');
		tr = nextSiblingOfType(nextSiblingOfType(table.firstChild, 'tbody').firstChild, 'tr');
		makeThSortable(tr);
		readTable(nextSiblingOfType(tr.nextSibling, 'tr'));
	}
	as = document.getElementsByTagName('a');
	summary_table = as[0].parentNode.parentNode.parentNode;
	for (var i = 0 ; i < as.length ; i++) {
		a = as[i];
		id = a.href.substring(a.href.indexOf('#')+1);
		a.id = 'view_'+id;
		a.setAttribute('onclick', 'view(this, this.href.substring(this.href.indexOf(\'#\')+1))');

		table = document.getElementById(id);

		new_tr = document.createElement('tr');
		new_tr.style.display = "none";
		new_td = document.createElement('td');
		new_td.setAttribute("colspan", 5);
		new_td.appendChild(table);
		new_tr.appendChild(new_td);

		tr = a.parentNode.parentNode.nextSibling;
		if (tr == null) summary_table.appendChild(new_tr);
		else summary_table.insertBefore(new_tr, tr);

	}
} 

function makeThSortable(tr) {
	var i = 0;
	th = nextSiblingOfType(tr.firstChild, 'th');
	while (th != null) {
		th.name='th_'+i;
		th.setAttribute('onclick', 'sort(this, 1, '+(i++)+')');
		th = nextSiblingOfType(th.nextSibling, 'th');
	}		
}


function readTable(tr) {
	rows = tableData[table.id] = [];
	while (tr != null) {
		cols = [];
		td = nextSiblingOfType(tr.firstChild, 'td');
		while (td != null) {
			cols.push(td.innerHTML);
			td = nextSiblingOfType(td.nextSibling, 'td');
		}
		rows.push(cols);
		tr = nextSiblingOfType(tr.nextSibling, 'tr');
	}
}


function view(view_a) {
	table = document.getElementById(view_a.href.substring(view_a.href.indexOf('#')+1));
	table.parentNode.parentNode.style.display = "table-row";
	view_a.innerHTML = "hide";
	view_a.setAttribute("onclick", "hide('"+view_a.id+"', 't"+id+"')");
	return false;
}

function hide(view_aid) {
	view_a = document.getElementById(view_aid);
	view_a.innerHTML = 'view';
	view_a.setAttribute('onclick', 'view(this)');
	table = document.getElementById(view_a.href.substring(view_a.href.indexOf('#')+1));
	table.parentNode.parentNode.style.display = 'none';
	return false;
}

function sort(th_clicked, order, th_index) {
	tbody = th_clicked.parentNode.parentNode;
	if (th_clicked.className.indexOf('sorted') != -1) { //If the th is already sorted
		reverseTable(tbody);
		updateSortIcon(th_clicked, order);
		th_clicked.setAttribute('onclick', 'sort(this, '+(-order)+', '+th_index+')');
	} else {
		ths = th_clicked.parentNode.childNodes;
		for (i = 0 ; i < ths.length ; i++) {
			th = ths[i];
			if (th.lastChild != null && th.lastChild.tagName != null && th.lastChild.tagName.toLowerCase() == 'span') {
				th.removeChild(th.lastChild);
				th.className = th.className.replace(/sorted/, "");
				th.setAttribute("onclick", "sort(this, 1, "+parseInt(th.name.substring(3))+")");
			}
		}
		sortTable(th_clicked, order, tbody);
		updateSortIcon(th_clicked, order);
		th_clicked.className += 'sorted';
		th_clicked.setAttribute('onclick', 'sort(this, '+(-order)+', '+th_index+')');
	}
}

function updateSortIcon(th, order) {
	if (th.lastChild.tagName != null && th.lastChild.tagName.toLowerCase() == 'span') {
		th.removeChild(th.lastChild);
	}
	span = document.createElement('span');
	span.innerHTML = order < 0 ? ' &#8896;':' &#8897;';
	th.appendChild(span);
}

function reverseTable(tbody) {
	i = 0;
	length = tbody.childNodes.length-1;
	first_tr = nextSiblingOfType(tbody.firstChild.nextSibling, 'tr');
	last_tr = previousSiblingOfType(tbody.lastChild, 'tr');
	while (last_tr != first_tr && i++ < length) {
		tbody.removeChild(last_tr);
		tbody.insertBefore(last_tr, first_tr);
		last_tr = previousSiblingOfType(tbody.lastChild, 'tr');
	}
	tableData[tbody.parentNode.id].reverse();
} 

var sort_key;
function sortTable(th, order, tbody) {
	sort_key = parseInt(th.name.substring(3));
	var data = tableData[tbody.parentNode.id];
	var zip = [];

	var tr = nextSiblingOfType(tbody.firstChild.nextSibling, 'tr');
	var i = 0;
	while (tr != null) {
		zip.push([data[i++], tr]);
		var ntr = nextSiblingOfType(tr.nextSibling, 'tr');
		tbody.removeChild(tr);
		tr = ntr;
	}
	if (zip[0][0][sort_key].match(/^\d+$/)) zip.sort(sort_num);
	else zip.sort(sort_alpha);
	var t = [];
	for (var i = 0 ; i < zip.length ; i++) {
		tbody.appendChild(zip[i][1]);
		zip[i][0]
		t.push(zip[i][0]);
	}
	tableData[tbody.parentNode.id] = t;
}
function sort_num(a,b) {
	a = parseFloat(a[0][sort_key]);
	b = parseFloat(b[0][sort_key]);
	if (a == b) return 0;
	if (a < b) return -1;
	return 1;
}
function sort_alpha(a,b) {
	if (a[0][sort_key] == b[0][sort_key]) return 0;
	if (a[0][sort_key] < b[0][sort_key]) return -1;
	return 1;
}

function nextSiblingOfType(element, tagName) {
	while (element != null && ((element.tagName != null && element.tagName.toLowerCase() != tagName) || element.tagName == null)) {
		element = element.nextSibling;
	}
	return element;
}

function previousSiblingOfType(element, tagName) {
	while (element != null && ((element.tagName != null && element.tagName.toLowerCase() != tagName) || element.tagName == null)) {
		element = element.previousSibling;
	}
	return element;
}
