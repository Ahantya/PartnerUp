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


document.addEventListener("DOMContentLoaded", function() {
    const deleteAllLink = document.getElementById("deleteAllLink");
    deleteAllLink.addEventListener("click", function(event) {
        event.preventDefault();
        if (confirm("Are you sure you want to delete all partners?")) {
            const form = document.createElement("form");
            form.method = "POST";
            form.action = "/delete_all";
            document.body.appendChild(form);
            form.submit();
        }
    });
});


function showMessage(message, isSuccess) {
    if (isSuccess) {
        alert("Success: " + message);
    } else {
        alert("Error: " + message);
    }
}

setTimeout(function() {
    var successAlert = document.getElementById('successAlert');
    if (successAlert) {
        successAlert.style.display = 'none';
    }
}, 3000); 


setTimeout(function() {
        var errorAlert = document.getElementById('error-alert');
        if (errorAlert) {
            errorAlert.style.display = 'none';
        }
    }, 3000);


    var faq = document.getElementsByClassName("faq-page");
    var i;
    
    for (i = 0; i < faq.length; i++) {
        faq[i].addEventListener("click", function () {
            /* Toggle between adding and removing the "active" class,
            to highlight the button that controls the panel */
            this.classList.toggle("active");
    
            /* Toggle between hiding and showing the active panel */
            var body = this.nextElementSibling;
            if (body.style.display === "block") {
                body.style.display = "none";
            } else {
                body.style.display = "block";
            }
        });
    }
