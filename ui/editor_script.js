// ...existing JS code...

function attachImageHandlers() {
    var editor = document.getElementById('editor');
    editor.addEventListener('click', function(e) {
        // Remove 'selected' from all images
        var imageWrappers = editor.querySelectorAll('.draggable-image');
        imageWrappers.forEach(function(wrapper) {
            wrapper.classList.remove('selected');
        });
        // If an image inside a draggable wrapper was clicked, mark it
        if (e.target.tagName.toLowerCase() === 'img' && e.target.parentNode.classList.contains('draggable-image')) {
            e.target.parentNode.classList.add('selected');
        }
    });
}

// Call on DOM load
document.addEventListener("DOMContentLoaded", function(){
    attachImageHandlers();
});

document.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        let sel = window.getSelection();
        if (!sel.rangeCount) return;
        let range = sel.getRangeAt(0);
        let node = range.startContainer.nodeType === Node.TEXT_NODE
            ? range.startContainer.parentNode
            : range.startContainer;
        let li = node.closest ? node.closest("li") : null;
        if (li) {
            e.preventDefault();
            if (li.innerText.trim() === "") {
                // Empty -> exit list
                document.execCommand("outdent");
                document.execCommand("insertHTML", false, "<p><br></p>");
            } else {
                // Non-empty -> new list item
                document.execCommand("insertHTML", false, "<li><br></li>");
            }
        }
    }
});

// ...existing JS code...
