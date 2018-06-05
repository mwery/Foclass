function getElementsByContent(content, tagName) {
	var elements = new Array();
	var nodes = document.getElementsByTagName(tagName);
	for (var i = 0, node; node = nodes[i]; i++) {
			if (node.innerHTML.indexOf(content) != -1) elements.push(node);
	}
	return elements;
}

function nextSiblingOfType(node, nodeName, validAttributes) {
	if (validAttributes == null) validAttributes = function (node) {return true;};
	node = node.nextSibling;
	while ((node.nodeName != nodeName || (node.nodeName == nodeName && !validAttributes(node))) && node.nextSibling != null)
		node = node.nextSibling;
	return node;
}

function makeStableStatesClickable() {
	var tables = getElementsByContent('Stable states', 'td');
	var i;
	for (i = 0 ; i - tables.length != 0 ; i++) {
		var td_stableState = tables[i];//the td containing Stable states
		var tr = tables[i].parentNode;
		p = document.createElement('p');
		p.innerHTML = tables[i].innerHTML + ' (';
		a = document.createElement('a');
		a.setAttribute('href', 'javascript:toggle(this, "stableState'+i+'")');
		a.innerHTML = 'View';
		p.appendChild(a);
		p.innerHTML += ')';
		tables[i].replaceChild(p, tables[i].firstChild) ;

		tr = nextSiblingOfType(tr, tr.nodeName, function (node) {
			node = nextSiblingOfType(node.firstChild, tables[i].nodeName, null);
			if (node.getAttribute("colspan") != null && node.getAttribute("colspan") > 3) return true;
			return false;
		})
		var td_new = nextSiblingOfType(tr.firstChild, tables[i].nodeName, null);
		td = document.createElement('td');
		td.setAttribute('colspan', '5');
		p = document.createElement('p');
		p.innerHTML = td_new.innerHTML;
		p.setAttribute('id', 'stableState'+i);
		p.style.display = 'none';
		td.appendChild(p);
		tr.replaceChild(td, td_new);
	}
}

function toggle(a, id) {
	elm = document.getElementById(id);
	if (elm.style.display == 'none') {
		elm.style.display = 'inline';
		a.innerHTML = 'Hide';
	} else {
		elm.style.display = 'none'
		a.innerHTML = 'View';
	}
}

window.onload = makeStableStatesClickable;