const form = document.getElementById('signing-form');
const responseMessage = document.getElementById('response-message');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    responseMessage.textContent = "Signing app, please wait...";

    try {
        const response = await fetch('http://your-fastapi-url/sign-app/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.error) {
            responseMessage.textContent = `Error: ${data.error}`;
            responseMessage.style.color = 'red';
        } else {
            responseMessage.textContent = data.message;
        }
    } catch (error) {
        responseMessage.textContent = `Error: ${error.message}`;
        responseMessage.style.color = 'red';
    }
});
