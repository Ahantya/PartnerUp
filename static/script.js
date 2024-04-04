// Get all elements with the class "edit-btn"
const editBtns = document.querySelectorAll(".edit-btn");
const idbuttos = document.querySelectorAll(".whoknows");

// Loop through each button and add event listener
editBtns.forEach(function(btn) {
    btn.addEventListener("click", function() {
        console.log("Update display function called");

        // Get the data-id attribute of the clicked button
        const dataId = btn.getAttribute('data-id');
        console.log("Button clicked for data-id:", dataId);

        // Get the corresponding edit-content element by its data-id
        const editContent = document.getElementById(`edit-${dataId}`);
        const yuppersDiv = document.getElementById('yuppers');
        
        // Toggle the 'edit-content' class on the edit-content element
        if (editContent.classList.contains('edit-content')) {
            editContent.classList.remove('edit-content');
            idbuttos.forEach(function(idbttn) {
                idbttn.classList.remove('yuppers');
            });
            idbuttos.forEach(function(idbttn) {
                idbttn.classList.add('flex', 'mx-auto', 'items-center');
            });
        } else {
            editContent.classList.add('edit-content');
            idbuttos.forEach(function(idbttn) {
                idbttn.classList.add('yuppers');
            });
            idbuttos.forEach(function(idbttn) {
                idbttn.classList.remove('flex', 'mx-auto', 'items-center');
            });
        }

        // Example: Call your function here with dataId
        // updateDisplay(dataId);
    });
});

// Example function
function updateDisplay() {
    console.log("Updating display");
}
