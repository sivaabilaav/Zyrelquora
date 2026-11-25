
// Zyrelquora - Show / Hide Password

document.addEventListener('click', function (event) {

    const button = event.target.closest('.auth-password-toggle');

    if (!button) {
        return;
    }

    const inputId = button.getAttribute('data-password-toggle');
    const passwordInput = document.getElementById(inputId);

    if (!passwordInput) {
        return;
    }

    if (passwordInput.type === 'password') {

        passwordInput.type = 'text';
        button.setAttribute('aria-label', 'Hide password');
        button.setAttribute('aria-pressed', 'true');

        button.innerHTML = `
            <svg viewBox="0 0 24 24"
                 fill="none"
                 stroke="currentColor"
                 stroke-width="1.8"
                 stroke-linecap="round"
                 stroke-linejoin="round"
                 aria-hidden="true">
                <path d="M3 3l18 18"/>
                <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/>
                <path d="M9.9 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a14.5 14.5 0 0 1-3.1 3.9"/>
                <path d="M6.2 6.2C3.5 8.1 2 12 2 12s3.6 7 10 7a10 10 0 0 0 3-.5"/>
            </svg>
        `;

    } else {

        passwordInput.type = 'password';
        button.setAttribute('aria-label', 'Show password');
        button.setAttribute('aria-pressed', 'false');

        button.innerHTML = `
            <svg viewBox="0 0 24 24"
                 fill="none"
                 stroke="currentColor"
                 stroke-width="1.8"
                 stroke-linecap="round"
                 stroke-linejoin="round"
                 aria-hidden="true">
                <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
        `;
    }

});
// Zyrelquora - Cart Action Confirmation

document.addEventListener('submit', function (event) {

    const form = event.target;

    if (form.dataset.confirm) {

        const confirmed = confirm(form.dataset.confirm);

        if (!confirmed) {
            event.preventDefault();
        }
    }

});

// Zyrelquora - AJAX Cart Quantity Update
document.addEventListener('submit', async function (event) {

    const form = event.target;

    if (!form.matches('.cart-quantity-form')) {
        return;
    }

    event.preventDefault();

    const button = form.querySelector('button[type="submit"]');

    if (button) {
        button.disabled = true;
    }

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error('Cart update failed');
        }

        const html = await response.text();

        const parser = new DOMParser();
        const newDocument = parser.parseFromString(html, 'text/html');

        const updatedCart = newDocument.querySelector('.cart-section');
        const currentCart = document.querySelector('.cart-section');

        if (!updatedCart || !currentCart) {
            throw new Error('Cart section not found');
        }

        currentCart.replaceWith(updatedCart);

        const updatedMessages = newDocument.querySelector('#django-messages');
        const currentMessages = document.querySelector('#django-messages');

        if (updatedMessages && currentMessages) {
            currentMessages.innerHTML = updatedMessages.innerHTML;
        }

    } catch (error) {
        console.error('Cart AJAX error:', error);
        window.location.reload();
    }
});
// BACK TO TOP BUTTON

const backToTop = document.getElementById("backToTop");

if (backToTop) {

    window.addEventListener("scroll", function () {
        if (window.scrollY > 300) {
            backToTop.style.display = "flex";
        } else {
            backToTop.style.display = "none";
        }
    });

    backToTop.addEventListener("click", function () {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });

}