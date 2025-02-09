(function() {
    console.log("Enabling table editing...");
    var ed = document.getElementById('editor');
    if (!ed) {
        console.error("Editor element not found!");
        return;
    }
    var removalTimer = null;
    function removeHandles() {
        document.querySelectorAll('.table-handle-btn-container').forEach(container => container.remove());
    }
    function scheduleRemoval() {
        removalTimer = setTimeout(removeHandles, 300);
    }
    function cancelRemoval() {
        if (removalTimer) {
            clearTimeout(removalTimer);
            removalTimer = null;
        }
    }
    function createButtonWithBuffer(btn) {
        var bgColor = '#666';
        if (btn.text.indexOf("row") > -1 && btn.text.indexOf("+") > -1) { bgColor = '#28a745'; }
        else if (btn.text.indexOf("col") > -1 && btn.text.indexOf("+") > -1) { bgColor = '#28a745'; }
        else if (btn.text.indexOf("row") > -1 || btn.text.indexOf("col") > -1) { bgColor = '#dc3545'; }
        let container = document.createElement('div');
        container.className = 'table-handle-btn-container';
        container.style.cssText = `
                    position: fixed;
                    top: ${btn.top - 10}px;
                    left: ${btn.left - 10}px;
                    padding: 10px;
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                `;
        let symbol = btn.text.slice(0,1);
        let buttonEl = document.createElement('div');
        buttonEl.className = 'table-handle-btn';
        buttonEl.textContent = symbol;
        buttonEl.style.cssText = `
                    background: ${bgColor};
                    color: white;
                    width: 16px;
                    height: 16px;
                    text-align: center;
                    line-height: 16px;
                    font-size: 10px;
                    cursor: pointer;
                    border-radius: 50%;
                    flex-shrink: 0;
                `;
        let labelEl = document.createElement('span');
        labelEl.textContent = btn.text;
        labelEl.style.cssText = `
                    display: none;
                    margin-left: 5px;
                    font-size: 10px;
                    color: white;
                `;
        container.addEventListener('mouseenter', () => {
            labelEl.style.display = 'inline';
            cancelRemoval();
        });
        container.addEventListener('mouseleave', () => {
            labelEl.style.display = 'none';
            scheduleRemoval();
        });
        buttonEl.onclick = btn.action;
        container.appendChild(buttonEl);
        container.appendChild(labelEl);
        document.body.appendChild(container);
        return container;
    }
    function handleCellMouseEnter(e) { cancelRemoval(); }
    function handleCellMouseLeave(e) { scheduleRemoval(); }
    // --- Resizing code start ---
    var isResizing = false;
    var resizeMode = null; // "col" or "row"
    var targetCell = null;
    var startX, startY, startWidth, startHeight;
    var threshold = 3; // pixels from border for resize mode
    function setCursor(cursor) { ed.style.cursor = cursor; }
    function handleMouseMoveForResize(e) {
        if (isResizing) return;
        let cell = e.target.closest("td, th");
        if (!cell) {
            setCursor("default");
            return;
        }
        let rect = cell.getBoundingClientRect();
        let x = e.clientX, y = e.clientY;
        let nearRight = (rect.right - x) < threshold;
        let nearBottom = (rect.bottom - y) < threshold;
        if (nearRight && !nearBottom) {
            setCursor("col-resize");
            resizeMode = "col";
        } else if (nearBottom && !nearRight) {
            setCursor("row-resize");
            resizeMode = "row";
        } else if (nearRight && nearBottom) {
            setCursor("col-resize");
            resizeMode = "col";
        } else {
            setCursor("default");
            resizeMode = null;
        }
    }
    function handleMouseDownForResize(e) {
        let cell = e.target.closest("td, th");
        if (!cell || !resizeMode) return;
        isResizing = true;
        targetCell = cell;
        let rect = cell.getBoundingClientRect();
        startX = e.clientX;
        startY = e.clientY;
        startWidth = rect.width;
        startHeight = rect.height;
        e.preventDefault();
    }
    function handleMouseDrag(e) {
        if (!isResizing || !targetCell) return;
        if (resizeMode === "col") {
            let deltaX = e.clientX - startX;
            targetCell.style.width = (startWidth + deltaX) + "px";
            let cellIndex = targetCell.cellIndex;
            let table = targetCell.closest("table");
            if (table) {
                table.querySelectorAll("tr").forEach(function(row) {
                    let cell = row.cells[cellIndex];
                    if (cell) cell.style.width = (startWidth + deltaX) + "px";
                });
            }
        } else if (resizeMode === "row") {
            let deltaY = e.clientY - startY;
            targetCell.parentElement.style.height = (startHeight + deltaY) + "px";
        }
    }
    function handleMouseUpForResize(e) {
        if (isResizing) {
            isResizing = false;
            resizeMode = null;
            targetCell = null;
            setCursor("default");
        }
    }
    document.addEventListener("mousemove", handleMouseMoveForResize);
    ed.addEventListener("mousedown", handleMouseDownForResize);
    document.addEventListener("mousemove", handleMouseDrag);
    document.addEventListener("mouseup", handleMouseUpForResize);
    // --- Resizing code end ---
    function handleMouseOver(e) {
        if (e.target.matches('td, th')) {
            let cell = e.target;
            let rect = cell.getBoundingClientRect();
            let x = e.clientX;
            let y = e.clientY;
            if (x - rect.left > 4 && rect.right - x > 4 &&
                y - rect.top > 4 && rect.bottom - y > 4) {
                removeHandles();
                return;
            }
            cancelRemoval();
            cell.removeEventListener('mouseenter', handleCellMouseEnter);
            cell.addEventListener('mouseenter', handleCellMouseEnter);
            cell.removeEventListener('mouseleave', handleCellMouseLeave);
            cell.addEventListener('mouseleave', handleCellMouseLeave);
            
            removeHandles();
            let isFirstRow = cell.parentElement.rowIndex === 0;
            let isFirstColumn = cell.cellIndex === 0;
            // Only show buttons if cell is at top row or left column.
            if (!isFirstRow && !isFirstColumn) {
                return;
            }
            let btns = [];
            if (isFirstColumn) {
                btns.push({
                    text: '-row',
                    top: rect.top,
                    left: rect.left - 20,
                    action: () => cell.parentElement.remove()
                });
                btns.push({
                    text: '+row',
                    top: rect.bottom,
                    left: rect.left - 20,
                    action: () => {
                        let newRow = cell.closest('table').insertRow(cell.parentElement.rowIndex + 1);
                        for (let i = 0; i < cell.parentElement.cells.length; i++) {
                            let newCell = newRow.insertCell();
                            newCell.style.border = '1px solid #ccc';
                            newCell.style.padding = '8px';
                        }
                    }
                });
            }
            if (isFirstRow) {
                btns.push({
                    text: '-col',
                    top: rect.top - 20,
                    left: rect.left,
                    action: () => {
                        let idx = Array.from(cell.parentElement.children).indexOf(cell);
                        cell.closest('table').querySelectorAll('tr').forEach(row => {
                            if (row.cells[idx]) row.deleteCell(idx);
                        });
                    }
                });
                btns.push({
                    text: '+col',
                    top: rect.top - 20,
                    left: rect.right,
                    action: () => {
                        let idx = Array.from(cell.parentElement.children).indexOf(cell) + 1;
                        cell.closest('table').querySelectorAll('tr').forEach(row => {
                            let newCell = row.insertCell(idx);
                            newCell.style.border = '1px solid #ccc';
                            newCell.style.padding = '8px';
                        });
                    }
                });
            }
            btns.forEach(btn => createButtonWithBuffer(btn));
        }
    }
    ed.addEventListener('mouseover', handleMouseOver);
    console.log("Table editing enabled!");
})();
