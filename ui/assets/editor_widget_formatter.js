
(function(){{
    var ed = document.getElementById('editor');
    var sel = window.getSelection();
    function getHeading(node){{
        while(node && node !== ed){{
            if(node.nodeName.match(/^H[1-6]$/)) return node;
            node = node.parentNode;
        }}
        return null;
    }}
    function inList(node){{
        while(node && node !== ed){{
            if(node.nodeName.match(/^(LI|UL|OL)$/)) return true;
            node = node.parentNode;
        }}
        return false;
    }}
    var currentHeading = getHeading(sel.anchorNode);
    var appliedCommand = "{command}";
    var appliedValue = {f'"{value}"' if value is not None else 'null'};
    
    // Prevent heading if selection is within a list
    if(appliedCommand === 'formatBlock' && appliedValue && appliedValue.match(/<H[1-6]>/i)){{
        if(inList(sel.anchorNode)){{
            console.log("Cannot add heading inside a list");
            return;
        }}
        var tag = appliedValue.replace(/[<>]/g, '').toUpperCase();
        if(currentHeading && currentHeading.nodeName === tag){{
            document.execCommand('formatBlock', false, '<P>');
            return;
        }}
    }}
    else if(currentHeading && appliedCommand !== 'formatBlock'){{
        document.execCommand('formatBlock', false, '<P>');
    }}
    ed.focus();
    if(appliedValue)
        document.execCommand(appliedCommand, false, appliedValue);
    else
        document.execCommand(appliedCommand, false, null);
}})();