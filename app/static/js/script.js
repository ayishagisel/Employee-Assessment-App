// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to any forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Prevent double submission
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
            }
        });
    });

    // Add event listeners to any flash message close buttons
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        const closeButton = message.querySelector('.close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                message.style.display = 'none';
            });
        }
    });
}); 