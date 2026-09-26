//###################################################
// JavaScript replacement for the atc50c.jar navigation
// tree applet (com.carpathia.vftis.atc50c.AnimatedTreeControl).
//###################################################

(function () {

	function parseImageList(treeEl) {
		var map = {};
		var nodes = treeEl.getElementsByTagName("image");
		for (var i = 0; i < nodes.length; i++) {
			var img = nodes[i];
			map[img.getAttribute("name")] = img.getAttribute("file");
		}
		return map;
	}

	function el(tag, className) {
		var e = document.createElement(tag);
		if (className) e.className = className;
		return e;
	}

	function icon(src) {
		var img = el("img", "navtree-icon");
		img.src = src;
		img.alt = "";
		return img;
	}

	function buildRow(config, toggleChar, iconSrc, label) {
		var row = el("div", "navtree-row");
		var toggle = el("span", "navtree-toggle");
		toggle.textContent = toggleChar || "";
		row.appendChild(toggle);
		row.appendChild(icon(iconSrc));
		var text = el("span", "navtree-label");
		text.textContent = label;
		row.appendChild(text);
		return row;
	}

	function buildFolder(config, folderEl, ancestors) {
		var li = el("li", "navtree-folder");
		var name = folderEl.getAttribute("name");
		var row = buildRow(config, "+", config.closeFolderIcon, name);
		li.appendChild(row);

		var childList = el("ul");
		childList.style.display = "none";
		li.appendChild(childList);

		var expanded = false;
		function setExpanded(value) {
			expanded = value;
			childList.style.display = expanded ? "" : "none";
			row.querySelector(".navtree-toggle").textContent = expanded ? "−" : "+";
			row.querySelector(".navtree-icon").src = expanded ? config.openFolderIcon : config.closeFolderIcon;
		}
		row.addEventListener("click", function () { setExpanded(!expanded); });
		// exposed so search can force-open ancestor folders of a match
		li.navtreeSetExpanded = setExpanded;

		config.searchIndex.push({ name: name, row: row, ancestors: ancestors });
		appendChildren(config, folderEl, childList, ancestors.concat([li]));

		return li;
	}

	function buildLeaf(config, leafEl, ancestors) {
		var li = el("li", "navtree-leaf");
		var name = leafEl.getAttribute("name");
		var link = leafEl.getAttribute("link");
		var imageId = leafEl.getAttribute("image");
		var iconSrc = config.imageList[imageId] || config.leafIcon;
		var row = buildRow(config, "", iconSrc, name);
		li.appendChild(row);

		row.addEventListener("click", function () {
			if (config.activeRow) config.activeRow.parentNode.classList.remove("active");
			li.classList.add("active");
			config.activeRow = row;
			window.open(link, config.target);
		});

		config.searchIndex.push({ name: name, row: row, ancestors: ancestors });

		return li;
	}

	function appendChildren(config, parentEl, ul, ancestors) {
		for (var i = 0; i < parentEl.children.length; i++) {
			var child = parentEl.children[i];
			if (child.tagName === "folder") {
				ul.appendChild(buildFolder(config, child, ancestors));
			} else if (child.tagName === "leaf") {
				ul.appendChild(buildLeaf(config, child, ancestors));
			}
		}
	}

	// ---- search / expand (mirrors the applet's document.stree API used by
	// scripts/basic.js's search box and scripts/tree.js's locateTree) ----

	function findMatches(config, keyword) {
		var kw = keyword.toLowerCase();
		return config.searchIndex.filter(function (node) {
			return node.name.toLowerCase().indexOf(kw) !== -1;
		});
	}

	function revealMatch(config, node) {
		node.ancestors.forEach(function (folderLi) { folderLi.navtreeSetExpanded(true); });
		if (config.searchHitRow) config.searchHitRow.classList.remove("search-hit");
		node.row.classList.add("search-hit");
		config.searchHitRow = node.row;
		node.row.scrollIntoView({ block: "center" });
	}

	function installStreeApi(config) {
		document.stree = {
			// used by scripts/tree.js locateTree() - jump to the first match
			expand: function (str) {
				var matches = findMatches(config, str || "");
				if (!matches.length) return false;
				revealMatch(config, matches[0]);
				return true;
			},
			// used by scripts/basic.js searchFirst() - start a new full-text search
			searchFirst: function (keyword) {
				var matches = findMatches(config, keyword || "");
				config.searchState = { keyword: keyword, matches: matches, index: matches.length ? 0 : -1 };
				if (!matches.length) return 0;
				revealMatch(config, matches[0]);
				return matches.length;
			},
			// used by scripts/basic.js searchFirst() on repeat clicks - advance to the next match
			searchNext: function (keyword) {
				var state = config.searchState;
				if (!state || state.keyword !== keyword) {
					return document.stree.searchFirst(keyword);
				}
				if (state.index + 1 >= state.matches.length) return 0;
				state.index++;
				revealMatch(config, state.matches[state.index]);
				return state.matches.length - state.index;
			}
		};
	}

	function init(config) {
		config.searchIndex = [];
		installStreeApi(config);

		var container = document.getElementById(config.containerId || "navtree");
		container.className = "navtree";
		if (config.loadingMessage) container.textContent = config.loadingMessage;

		fetch(config.dataUrl)
			.then(function (res) { return res.text(); })
			.then(function (text) {
				var xml = new DOMParser().parseFromString(text, "application/xml");
				var treeEl = xml.getElementsByTagName("tree")[0];
				var rootEl = treeEl.getElementsByTagName("root")[0];

				config.imageList = parseImageList(treeEl);
				config.openFolderIcon = config.openFolderIcon || "images/openfolder.gif";
				config.closeFolderIcon = config.closeFolderIcon || "images/closedfolder.gif";
				config.leafIcon = config.leafIcon || "images/document.gif";
				config.target = config.target || "main";

				container.textContent = "";
				var ul = el("ul");
				appendChildren(config, rootEl, ul, []);
				container.appendChild(ul);
			})
			.catch(function (err) {
				container.textContent = "Failed to load navigation tree.";
				if (window.console) console.error("navtree:", err);
			});
	}

	window.NavTree = { init: init };

})();
