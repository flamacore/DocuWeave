(function() {
    function updateLinkBehavior() {
        document.querySelectorAll('a').forEach(link => {
            // Only handle visual styling
            link.addEventListener('mouseenter', function() {
                this.style.backgroundColor = "rgba(173,216,230,0.3)";
                this.style.borderRadius = "3px";
                this.style.padding = "0 3px";
                this.style.cursor = "pointer";
            });
            
            link.addEventListener('mouseleave', function() {
                this.style.backgroundColor = "";
                this.style.padding = "";
            });
        });
    }
    
    updateLinkBehavior();
    
    const observer = new MutationObserver(updateLinkBehavior);
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
})();
