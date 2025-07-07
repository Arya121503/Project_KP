/**
 * Dropdown Fix for User Dashboard
 * Ensures navbar dropdown is always visible and functional
 */

(function() {
  'use strict';
  
  // Force dropdown visibility function
  function forceDropdownVisibility() {
    const navbarDropdown = document.getElementById('navbarDropdown');
    if (navbarDropdown) {
      // Force visibility styles
      navbarDropdown.style.setProperty('display', 'flex', 'important');
      navbarDropdown.style.setProperty('visibility', 'visible', 'important');
      navbarDropdown.style.setProperty('opacity', '1', 'important');
      navbarDropdown.style.setProperty('position', 'relative', 'important');
      navbarDropdown.style.setProperty('color', '#363949', 'important'); // var(--color-dark)
      
      // Ensure user name is visible
      const userName = navbarDropdown.querySelector('.user-name');
      if (userName) {
        userName.style.setProperty('color', '#363949', 'important'); // var(--color-dark)
        userName.style.setProperty('visibility', 'visible', 'important');
        userName.style.setProperty('opacity', '1', 'important');
        userName.style.setProperty('display', 'inline', 'important');
      }
      
      // Ensure icon is visible
      const icon = navbarDropdown.querySelector('.material-icons-sharp');
      if (icon) {
        icon.style.setProperty('color', '#363949', 'important'); // var(--color-dark)
        icon.style.setProperty('visibility', 'visible', 'important');
        icon.style.setProperty('opacity', '1', 'important');
      }
      
      // Ensure parent elements are also visible
      const parentDropdown = navbarDropdown.closest('.nav-item.dropdown');
      if (parentDropdown) {
        parentDropdown.style.setProperty('display', 'block', 'important');
        parentDropdown.style.setProperty('visibility', 'visible', 'important');
        parentDropdown.style.setProperty('opacity', '1', 'important');
      }
    }
  }
  
  // Initialize dropdown functionality
  function initializeDropdownFunctionality() {
    const navbarDropdown = document.getElementById('navbarDropdown');
    const dropdownMenu = document.querySelector('.dropdown-menu[aria-labelledby="navbarDropdown"]');
    
    if (!navbarDropdown || !dropdownMenu) {
      return;
    }
    
    // Ensure dropdown menu is properly styled
    dropdownMenu.style.setProperty('position', 'absolute', 'important');
    dropdownMenu.style.setProperty('top', '100%', 'important');
    dropdownMenu.style.setProperty('right', '0', 'important');
    dropdownMenu.style.setProperty('left', 'auto', 'important');
    dropdownMenu.style.setProperty('z-index', '1050', 'important');
    
    // Click handler
    navbarDropdown.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      // Close other dropdowns
      document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        if (menu !== dropdownMenu) {
          menu.classList.remove('show');
        }
      });
      
      // Toggle current dropdown
      dropdownMenu.classList.toggle('show');
    });
    
    // Close on outside click
    document.addEventListener('click', function(e) {
      if (!navbarDropdown.contains(e.target) && !dropdownMenu.contains(e.target)) {
        dropdownMenu.classList.remove('show');
      }
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        dropdownMenu.classList.remove('show');
      }
    });
    
    // Prevent dropdown menu from closing when clicking inside (except on links)
    dropdownMenu.addEventListener('click', function(e) {
      if (!e.target.closest('a')) {
        e.stopPropagation();
      }
    });
  }
  
  // Initialize Bootstrap dropdown if available
  function initializeBootstrapDropdown() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
      const dropdownElementList = document.querySelectorAll('.dropdown-toggle');
      dropdownElementList.forEach(function (dropdownToggleEl) {
        new bootstrap.Dropdown(dropdownToggleEl, {
          autoClose: true,
          boundary: 'viewport',
          display: 'dynamic'
        });
      });
    }
  }
  
  // Main initialization function
  function initializeDropdown() {
    forceDropdownVisibility();
    initializeDropdownFunctionality();
    initializeBootstrapDropdown();
  }
  
  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDropdown);
  } else {
    initializeDropdown();
  }
  
  // Re-run periodically to ensure dropdown stays visible
  setInterval(forceDropdownVisibility, 1000);
  
  // Watch for dynamic changes that might hide the dropdown
  if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
          const target = mutation.target;
          if (target.id === 'navbarDropdown' || target.closest('#navbarDropdown')) {
            forceDropdownVisibility();
          }
        }
      });
    });
    
    observer.observe(document.body, {
      attributes: true,
      subtree: true,
      attributeFilter: ['style', 'class']
    });
  }
  
})();
