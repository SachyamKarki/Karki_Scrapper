// Delete selected rows
function deleteSelected() {
    const checkboxes = document.querySelectorAll('.select-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('Please select at least one row to delete');
        return;
    }

    if (!confirm(`Are you sure you want to delete ${checkboxes.length} selected item(s)?`)) {
        return;
    }

    const ids = Array.from(checkboxes).map(cb => cb.getAttribute('data-id'));

    fetch('/api/delete_items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: ids })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove rows from table
                checkboxes.forEach(cb => {
                    const row = cb.closest('tr');
                    if (row) row.remove();
                });
                // Update count
                const countEl = document.querySelector('.card-header .text-muted');
                if (countEl) {
                    const remaining = document.querySelectorAll('tr[data-id]').length;
                    countEl.textContent = `${remaining} places found`;
                }
            } else {
                alert('Failed to delete items');
            }
        })
        .catch(error => {
            console.error('Error deleting items:', error);
            alert('Failed to delete items');
        });
}
