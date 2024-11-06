document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('expense-form');
    const expenseTableBody = document.getElementById('expense-table');
    const totalAmountElement = document.getElementById('total-amount');
    let totalAmount = 0;

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const expenseData = {
            category_select: formData.get('category_select'),
            amount_input: parseFloat(formData.get('amount_input')),
            info: formData.get('info'),
            date_input: formData.get('date_input')
        };

        fetch('/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(expenseData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Added expense:', data);
            addExpenseToTable(data);
            totalAmount += data.category === 'Income' ? data.amount : -data.amount;
            totalAmountElement.textContent = totalAmount.toFixed(2); // Update total amount
            form.reset(); // Clear the form fields
        })
        .catch(error => console.error('Error adding expense:', error));
    });

    expenseTableBody.addEventListener('click', function (event) {
        const target = event.target;
        if (target.classList.contains('delete-btn')) {
            const expenseId = target.getAttribute('data-id');
            const deletedAmount = parseFloat(target.getAttribute('data-amount'));

            fetch(`/expenses/${expenseId}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    console.log('Expense deleted successfully');
                    target.parentElement.parentElement.remove(); // Remove the row from the table
                    totalAmount -= deletedAmount; // Adjust total amount after deletion
                    totalAmountElement.textContent = totalAmount.toFixed(2); // Update total amount
                } else {
                    console.error('Failed to delete expense');
                }
            })
            .catch(error => console.error('Error deleting expense:', error));
        }
    });

    // Fetch expenses and populate the table when the page loads
    fetch('/expenses')
    .then(response => response.json())
    .then(data => {
        console.log('Fetched expenses:', data);
        data.forEach(expense => {
            addExpenseToTable(expense);
            totalAmount += expense.category === 'Income' ? expense.amount : -expense.amount;
        });
        totalAmountElement.textContent = totalAmount.toFixed(2); // Initialize total amount
    })
    .catch(error => console.error('Error fetching expenses:', error));

    function addExpenseToTable(expense) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${expense.category}</td>
            <td>${expense.amount}</td>
            <td>${expense.info}</td>
            <td>${new Date(expense.date).toLocaleDateString()}</td>
            <td><button class="delete-btn" data-id="${expense.id}">Delete</button></td>
        `;
        expenseTableBody.appendChild(row);
    }
});