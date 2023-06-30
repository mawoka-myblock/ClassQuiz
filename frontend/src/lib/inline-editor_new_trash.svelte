<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let text;
	let internal_text = '';
	/*
		const markSelection = (function() {
			const markerTextChar = '\ufeff';
			const markerTextCharEntity = '&#xfeff;';

			let markerEl, markerId = 'sel_' + new Date().getTime() + '_' + Math.random().toString().substr(2);

			let selectionEl;

			return function(win) {
				win = win || window;
				const doc = win.document;
				let sel, range;
				// Branch for IE <= 8
				if (doc.selection && doc.selection.createRange) {
					// Clone the TextRange and collapse
					range = doc.selection.createRange().duplicate();
					range.collapse(false);

					// Create the marker element containing a single invisible character by creating literal HTML and insert it
					range.pasteHTML('<span id="' + markerId + '" style="position: relative;">' + markerTextCharEntity + '</span>');
					markerEl = doc.getElementById(markerId);
				} else if (win.getSelection) {
					sel = win.getSelection();
					range = sel.getRangeAt(0).cloneRange();
					range.collapse(false);

					// Create the marker element containing a single invisible character using DOM methods and insert it
					markerEl = doc.createElement('span');
					markerEl.id = markerId;
					markerEl.appendChild(doc.createTextNode(markerTextChar));
					range.insertNode(markerEl);
				}

				if (markerEl) {
					// Lazily create element to be placed next to the selection
					if (!selectionEl) {
						selectionEl = doc.createElement('div');
						selectionEl.style.border = 'solid darkblue 1px';
						selectionEl.style.backgroundColor = 'lightgoldenrodyellow';
						selectionEl.innerHTML = '&lt;- selection';
						selectionEl.style.position = 'absolute';

						doc.body.appendChild(selectionEl);
					}

					// Find markerEl position http://www.quirksmode.org/js/findpos.html
					var obj = markerEl;
					var left = 0, top = 0;
					do {
						left += obj.offsetLeft;
						top += obj.offsetTop;
					} while (obj = obj.offsetParent);

					// Move the button into place.
					// Substitute your jQuery stuff in here
					selectionEl.style.left = left + 'px';
					selectionEl.style.top = top + 'px';

					markerEl.parentNode.removeChild(markerEl);
				}
			};
		})();*/
	// $: console.log(document.getSelection().toString())
	/*
		const markSelection = () => {
			const sel = document.getSelection();
			console.log(sel.toString());
		};
	*/
	const bold_regex = /.*\*\*(.+)\*\*.*/gm; // **bold**
	const italic_regex = /.*\|\|(.+)\|\|.*/gm; // *italic*
	const strikethrough_regex = /.*~~(.+)~~.*/gm; // ~~strikethrough~~
	const sub_regex = /.*__(.+)__.*/gm; // __sub__
	const sup_regex = /.*--(.+)--.*/gm; // --sup--
	const process_input = () => {
		let output = internal_text;
		output = output.replace(bold_regex, '<b>$1</b>');
		output = output.replace(italic_regex, '<i>$1</i>');
		output = output.replace(strikethrough_regex, '<del>$1</del>');
		output = output.replace(sub_regex, '<sub>$1</sub>');
		output = output.replace(sup_regex, '<sup>$1</sup>');
		console.log(output);
	};

	$: {
		process_input();
		internal_text;
	}
</script>

<input bind:value={internal_text} />
