// BloomWell – Main JavaScript

// Toggle user dropdown menu
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

// Toggle mobile nav menu
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    if (menu) {
        menu.classList.toggle('open');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function (e) {
    const menu = document.querySelector('.nav-user-menu');
    const dropdown = document.getElementById('userDropdown');
    if (dropdown && menu && !menu.contains(e.target)) {
        dropdown.classList.remove('active');
    }
});

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(30px)';
            flash.style.transition = 'all 0.4s ease';
            setTimeout(function () { flash.remove(); }, 400);
        }, 5000);
    });

    // Animate page elements on load
    const animateOnLoad = document.querySelectorAll('.animate-up');
    animateOnLoad.forEach(function (el, i) {
        el.style.animationDelay = (i * 0.1) + 's';
        el.classList.add('animated');
    });
});

// Image preview for file inputs
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Confirm before delete/cancel actions
function confirmAction(message) {
    return confirm(message || 'Are you sure?');
}

// Free class toggle - disable price input when free is checked
document.addEventListener('DOMContentLoaded', function () {
    const freeCheckbox = document.getElementById('is_free');
    const priceInput = document.getElementById('price');
    if (freeCheckbox && priceInput) {
        freeCheckbox.addEventListener('change', function () {
            priceInput.disabled = this.checked;
            priceInput.closest('.form-group').style.opacity = this.checked ? '0.5' : '1';
        });
    }
});

// Star rating interactivity on review forms
document.addEventListener('DOMContentLoaded', function () {
    const ratingSelect = document.querySelector('select[name="rating"]');
    if (ratingSelect) {
        const starDisplay = document.createElement('div');
        starDisplay.className = 'star-rating-display';
        starDisplay.style.cssText = 'font-size: 1.5rem; margin-top: 0.5rem; color: #f4c430;';
        ratingSelect.parentNode.appendChild(starDisplay);

        function updateStars(val) {
            starDisplay.textContent = '★'.repeat(val) + '☆'.repeat(5 - val);
        }

        ratingSelect.addEventListener('change', function () { updateStars(this.value); });
        if (ratingSelect.value) updateStars(ratingSelect.value);
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
