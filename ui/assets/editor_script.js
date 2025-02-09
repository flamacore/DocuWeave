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

// ...existing JS code...
