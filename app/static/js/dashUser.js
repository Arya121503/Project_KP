console.log("Dashboard User JS Loaded!");

// Dashboard User JavaScript Functions
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sideMenu = document.querySelector("aside");
    const menuBtn = document.getElementById("menu-btn");
    const closeBtn = document.getElementById("close-btn");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const container = document.querySelector(".container");

    // Mobile sidebar toggle
    if (menuBtn && sideMenu) {
        menuBtn.addEventListener("click", () => {
            sideMenu.classList.add("show");
        });
    }

    if (closeBtn && sideMenu) {
        closeBtn.addEventListener("click", () => {
            sideMenu.classList.remove("show");
        });
    }

    // Desktop sidebar hide/show toggle
    if (sidebarToggle && container && sideMenu) {
        sidebarToggle.addEventListener("click", () => {
            container.classList.toggle("sidebar-hidden");
            sideMenu.classList.toggle("hidden");
            
            // Update icon based on state
            const icon = sidebarToggle.querySelector("span");
            if (sideMenu.classList.contains("hidden")) {
                icon.textContent = "menu";
            } else {
                icon.textContent = "menu_open";
            }
        });
    }

    // Dark mode toggle
    const darkMode = document.querySelector(".dark-mode");
    if (darkMode) {
        // Load dark mode preference on page load
        const savedDarkMode = localStorage.getItem("darkMode");
        if (savedDarkMode === "true") {
            document.body.classList.add("dark-mode-variables");
            darkMode.querySelector("span:nth-child(1)").classList.remove("active");
            darkMode.querySelector("span:nth-child(2)").classList.add("active");
        } else {
            document.body.classList.remove("dark-mode-variables");
            darkMode.querySelector("span:nth-child(1)").classList.add("active");
            darkMode.querySelector("span:nth-child(2)").classList.remove("active");
        }
        
        // Add click event listener
        darkMode.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode-variables");
            darkMode.querySelector("span:nth-child(1)").classList.toggle("active");
            darkMode.querySelector("span:nth-child(2)").classList.toggle("active");
            
            // Save dark mode preference
            const isDarkMode = document.body.classList.contains("dark-mode-variables");
            localStorage.setItem("darkMode", isDarkMode);
            
            // Debug log
            console.log("Dark mode toggled:", isDarkMode);
        });
    }

    // Close sidebar when clicking outside (for mobile)
    document.addEventListener("click", (e) => {
        if (sideMenu && sideMenu.classList.contains("show")) {
            if (!sideMenu.contains(e.target) && !menuBtn.contains(e.target)) {
                sideMenu.classList.remove("show");
            }
        }
    });

    // Initialize Bootstrap dropdown
    initializeDropdown();
});

function initializeDropdown() {
    // Wait for Bootstrap to be fully loaded
    if (typeof bootstrap !== 'undefined') {
        // Initialize Bootstrap dropdown
        const dropdownElementList = document.querySelectorAll('.dropdown-toggle');
        const dropdownList = [...dropdownElementList].map(dropdownToggleEl => {
            return new bootstrap.Dropdown(dropdownToggleEl, {
                autoClose: true,
                boundary: 'viewport',
                display: 'dynamic'
            });
        });
        
        // Additional manual dropdown handling for extra reliability
        const navbarDropdown = document.getElementById('navbarDropdown');
        const dropdownMenu = document.querySelector('.dropdown-menu');
        
        if (navbarDropdown && dropdownMenu) {
            // Ensure dropdown toggle is always visible
            navbarDropdown.style.display = 'flex';
            navbarDropdown.style.visibility = 'visible';
            navbarDropdown.style.opacity = '1';
            
            // Force show dropdown menu when clicked
            navbarDropdown.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Toggle dropdown visibility
                const isOpen = dropdownMenu.classList.contains('show');
                
                if (isOpen) {
                    dropdownMenu.classList.remove('show');
                } else {
                    dropdownMenu.classList.add('show');
                    dropdownMenu.style.position = 'absolute';
                    dropdownMenu.style.inset = '0px 0px auto auto';
                    dropdownMenu.style.margin = '0px';
                    dropdownMenu.style.transform = 'translate3d(-100%, 100%, 0px)';
                }
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbarDropdown.contains(e.target) && !dropdownMenu.contains(e.target)) {
                    dropdownMenu.classList.remove('show');
                }
            });
        }
    } else {
        // Fallback if Bootstrap is not loaded yet
        setTimeout(initializeDropdown, 100);
    }
}

// Asset filtering and management functions for user dashboard
function filterAssets() {
    const assetType = document.getElementById('assetTypeFilter')?.value || '';
    const location = document.getElementById('locationFilter')?.value || '';
    const priceRange = document.getElementById('priceFilter')?.value || '';
    const status = document.getElementById('statusFilter')?.value || '';
    
    console.log('Filtering assets:', { assetType, location, priceRange, status });
    
    // Show loading state
    const grid = document.getElementById('assetGrid');
    if (grid) {
        grid.innerHTML = `
            <div class="col-12 text-center">
                <div class="card">
                    <div class="card-body py-5">
                        <div class="spinner-border text-danger mb-3" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <h4>Mencari aset...</h4>
                        <p class="text-muted">Mohon tunggu sebentar</p>
                    </div>
                </div>
            </div>
        `;
    }
}

// SPA navigation for user dashboard
const menuLinks = document.querySelectorAll(".menu-link");
const contentSections = document.querySelectorAll(".content-section");

menuLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
        e.preventDefault();

        // Update active menu item
        menuLinks.forEach((l) => l.classList.remove("active"));
        link.classList.add("active");

        // Show target section
        const target = link.getAttribute("data-target");
        if (target) {
            contentSections.forEach((section) => {
                section.classList.remove("active");
            });

            const targetSection = document.getElementById(target);
            if (targetSection) {
                targetSection.classList.add("active");
            }
        }
    });
});

// Profile Edit and Password Change Functions
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + '_icon');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function checkPasswordStrength(password) {
    let strength = 0;
    let text = '';
    let className = '';
    
    // Length check
    if (password.length >= 8) strength += 25;
    
    // Lowercase check
    if (/[a-z]/.test(password)) strength += 25;
    
    // Uppercase check
    if (/[A-Z]/.test(password)) strength += 25;
    
    // Number or special character check
    if (/[0-9]/.test(password) || /[^A-Za-z0-9]/.test(password)) strength += 25;
    
    // Set text and class based on strength
    if (strength === 0) {
        text = 'Masukkan password untuk melihat kekuatan';
        className = '';
    } else if (strength <= 25) {
        text = 'Lemah';
        className = 'bg-danger';
    } else if (strength <= 50) {
        text = 'Sedang';
        className = 'bg-warning';
    } else if (strength <= 75) {
        text = 'Kuat';
        className = 'bg-info';
    } else {
        text = 'Sangat Kuat';
        className = 'bg-success';
    }
    
    return { strength, text, className };
}

function updatePasswordStrength() {
    const passwordField = document.getElementById('new_password');
    const strengthBar = document.getElementById('password_strength');
    const strengthText = document.getElementById('password_strength_text');
    
    if (passwordField && strengthBar && strengthText) {
        const password = passwordField.value;
        const result = checkPasswordStrength(password);
        
        strengthBar.style.width = result.strength + '%';
        strengthBar.className = 'progress-bar ' + result.className;
        strengthText.textContent = result.text;
        strengthText.className = 'form-text ' + (result.className ? result.className.replace('bg-', 'text-') : 'text-muted');
    }
}

function checkPasswordMatch() {
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    const matchMessage = document.getElementById('password_match_message');
    const submitBtn = document.getElementById('submitBtn');
    
    if (newPassword && confirmPassword && matchMessage && submitBtn) {
        const isMatch = newPassword.value === confirmPassword.value;
        const hasMinLength = newPassword.value.length >= 8;
        const confirmHasValue = confirmPassword.value.length > 0;
        
        if (confirmHasValue) {
            if (isMatch) {
                matchMessage.textContent = 'Password cocok ✓';
                matchMessage.className = 'form-text text-success';
                confirmPassword.classList.remove('is-invalid');
                confirmPassword.classList.add('is-valid');
            } else {
                matchMessage.textContent = 'Password tidak cocok ✗';
                matchMessage.className = 'form-text text-danger';
                confirmPassword.classList.remove('is-valid');
                confirmPassword.classList.add('is-invalid');
            }
        } else {
            matchMessage.textContent = '';
            confirmPassword.classList.remove('is-valid', 'is-invalid');
        }
        
        // Enable submit button only if passwords match and meet requirements
        submitBtn.disabled = !(isMatch && hasMinLength && confirmHasValue);
    }
}

// Password visibility toggle function
window.togglePassword = function(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + '_icon');
    
    if (passwordField && icon) {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
};

// Password strength validation and matching
const newPasswordField = document.getElementById('new_password');
const confirmPasswordField = document.getElementById('confirm_password');
const strengthBar = document.getElementById('password_strength');
const strengthText = document.getElementById('password_strength_text');
const matchMessage = document.getElementById('password_match_message');
const submitBtn = document.getElementById('submitBtn');

function checkPasswordStrength(password) {
    let strength = 0;
    let strengthLabel = '';
    
    if (password.length >= 8) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    switch (strength) {
        case 0:
        case 1:
            strengthLabel = 'Sangat Lemah';
            break;
        case 2:
            strengthLabel = 'Lemah';
            break;
        case 3:
            strengthLabel = 'Sedang';
            break;
        case 4:
            strengthLabel = 'Kuat';
            break;
        case 5:
            strengthLabel = 'Sangat Kuat';
            break;
    }
    
    return { strength, strengthLabel };
}

function updatePasswordStrength() {
    if (!newPasswordField || !strengthBar || !strengthText) return;
    
    const password = newPasswordField.value;
    const { strength, strengthLabel } = checkPasswordStrength(password);
    
    if (password.length === 0) {
        strengthBar.style.width = '0%';
        strengthBar.className = 'progress-bar';
        strengthText.textContent = 'Masukkan password untuk melihat kekuatan';
        strengthText.className = 'text-muted';
        return;
    }
    
    const percentage = (strength / 5) * 100;
    strengthBar.style.width = percentage + '%';
    strengthText.textContent = strengthLabel;
    
    // Color coding
    if (strength <= 1) {
        strengthBar.className = 'progress-bar bg-danger';
        strengthText.className = 'text-danger';
    } else if (strength <= 2) {
        strengthBar.className = 'progress-bar bg-warning';
        strengthText.className = 'text-warning';
    } else if (strength <= 3) {
        strengthBar.className = 'progress-bar bg-info';
        strengthText.className = 'text-info';
    } else {
        strengthBar.className = 'progress-bar bg-success';
        strengthText.className = 'text-success';
    }
}

function checkPasswordMatch() {
    if (!newPasswordField || !confirmPasswordField || !matchMessage || !submitBtn) return;
    
    const newPassword = newPasswordField.value;
    const confirmPassword = confirmPasswordField.value;
    
    if (confirmPassword.length === 0) {
        matchMessage.textContent = '';
        matchMessage.className = 'form-text';
        submitBtn.disabled = true;
        return;
    }
    
    if (newPassword === confirmPassword) {
        matchMessage.textContent = '✓ Password cocok';
        matchMessage.className = 'form-text text-success';
        
        // Enable submit button if password is strong enough
        const { strength } = checkPasswordStrength(newPassword);
        submitBtn.disabled = strength < 3; // Minimal "Sedang"
    } else {
        matchMessage.textContent = '✗ Password tidak cocok';
        matchMessage.className = 'form-text text-danger';
        submitBtn.disabled = true;
    }
}

// Attach event listeners for password validation
if (newPasswordField) {
    newPasswordField.addEventListener('input', function() {
        updatePasswordStrength();
        checkPasswordMatch();
    });
}

if (confirmPasswordField) {
    confirmPasswordField.addEventListener('input', checkPasswordMatch);
}

// Initialize password validation on page load
updatePasswordStrength();
checkPasswordMatch();
