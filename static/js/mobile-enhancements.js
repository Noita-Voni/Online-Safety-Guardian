// Mobile responsiveness enhancements for ThreatSense Analytics

document.addEventListener('DOMContentLoaded', function() {
  // Enhanced mobile menu toggle
  function toggleMobileMenu() {
    const navMenu = document.querySelector('.navbar-nav');
    const toggleButton = document.querySelector('.mobile-menu-toggle');
    
    if (navMenu) {
      navMenu.classList.toggle('show');
      
      // Update toggle button icon
      const icon = toggleButton.querySelector('i');
      if (navMenu.classList.contains('show')) {
        icon.className = 'fas fa-times';
      } else {
        icon.className = 'fas fa-bars';
      }
    }
  }

  // Close mobile menu when clicking outside
  document.addEventListener('click', function(event) {
    const navMenu = document.querySelector('.navbar-nav');
    const toggleButton = document.querySelector('.mobile-menu-toggle');
    const navbar = document.querySelector('.navbar');
    
    if (navMenu && navMenu.classList.contains('show')) {
      if (!navbar.contains(event.target)) {
        navMenu.classList.remove('show');
        const icon = toggleButton.querySelector('i');
        icon.className = 'fas fa-bars';
      }
    }
  });

  // Close mobile menu when link is clicked
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function() {
      const navMenu = document.querySelector('.navbar-nav');
      const toggleButton = document.querySelector('.mobile-menu-toggle');
      
      if (navMenu && navMenu.classList.contains('show')) {
        navMenu.classList.remove('show');
        const icon = toggleButton.querySelector('i');
        icon.className = 'fas fa-bars';
      }
    });
  });

  // Chart responsiveness improvements
  function makeChartsResponsive() {
    // Update Chart.js defaults for mobile
    if (typeof Chart !== 'undefined') {
      Chart.defaults.responsive = true;
      Chart.defaults.maintainAspectRatio = false;
      
      // Mobile-specific chart options
      const isMobile = window.innerWidth <= 768;
      
      if (isMobile) {
        Chart.defaults.plugins.legend.labels.boxWidth = 12;
        Chart.defaults.plugins.legend.labels.padding = 10;
        Chart.defaults.plugins.legend.labels.font = {
          size: 11
        };
      }
    }
  }

  // Call chart responsiveness on load
  makeChartsResponsive();

  // Update charts on window resize
  let resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      makeChartsResponsive();
      
      // Trigger chart resize
      if (typeof Chart !== 'undefined') {
        Chart.helpers.each(Chart.instances, function(instance) {
          instance.resize();
        });
      }
    }, 250);
  });

  // Touch improvements for threat cards
  if ('ontouchstart' in window) {
    document.querySelectorAll('.threat-profile-square').forEach(card => {
      card.addEventListener('touchstart', function() {
        this.style.transform = 'scale(0.98)';
      });
      
      card.addEventListener('touchend', function() {
        this.style.transform = 'scale(1)';
      });
    });
  }

  // Mobile modal improvements
  function isMobileDevice() {
    return window.innerWidth <= 768;
  }

  // Override modal functions for mobile
  if (typeof window.openThreatModal === 'function') {
    const originalOpenThreatModal = window.openThreatModal;
    window.openThreatModal = function(messageId) {
      originalOpenThreatModal(messageId);
      
      if (isMobileDevice()) {
        // Scroll to top of modal on mobile
        const modal = document.getElementById('threatModal');
        const modalContent = modal.querySelector('.threat-modal-content');
        if (modalContent) {
          modalContent.scrollTop = 0;
        }
      }
    };
  }

  // Mobile swipe gestures for modal closing
  let touchStartY = 0;
  let touchEndY = 0;

  document.addEventListener('touchstart', function(e) {
    touchStartY = e.changedTouches[0].screenY;
  });

  document.addEventListener('touchend', function(e) {
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
  });

  function handleSwipe() {
    const swipeDistance = touchStartY - touchEndY;
    const minSwipeDistance = 100;
    
    // If swiping down on modal, close it
    if (swipeDistance < -minSwipeDistance) {
      const modal = document.getElementById('threatModal');
      const settingsModal = document.getElementById('settingsModal');
      
      if (modal && modal.style.display === 'block') {
        if (typeof closeThreatModal === 'function') {
          closeThreatModal();
        }
      }
      if (settingsModal && settingsModal.classList.contains('active')) {
        if (typeof closeSettingsModal === 'function') {
          closeSettingsModal();
        }
      }
    }
  }

  // Mobile-specific chart configurations
  window.mobileChartOptions = {
    scales: {
      y: {
        ticks: {
          font: {
            size: 10
          }
        }
      },
      x: {
        ticks: {
          font: {
            size: 10
          },
          maxRotation: 45
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          font: {
            size: 11
          },
          padding: 10,
          boxWidth: 12
        }
      }
    }
  };

  // Apply mobile chart options if on mobile
  if (isMobileDevice()) {
    // This will be used when charts are created
    window.applyMobileChartOptions = true;
  }

  // Viewport meta tag enforcement for proper mobile scaling
  const viewport = document.querySelector('meta[name="viewport"]');
  if (!viewport) {
    const meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    document.head.appendChild(meta);
  }

  // Global mobile menu toggle function
  window.toggleMobileMenu = toggleMobileMenu;
});

// Smooth scrolling for mobile navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Mobile orientation change handling
window.addEventListener('orientationchange', function() {
  setTimeout(function() {
    // Trigger chart resize after orientation change
    if (typeof Chart !== 'undefined') {
      Chart.helpers.each(Chart.instances, function(instance) {
        instance.resize();
      });
    }
    
    // Close mobile menu on orientation change
    const navMenu = document.querySelector('.navbar-nav');
    const toggleButton = document.querySelector('.mobile-menu-toggle');
    
    if (navMenu && navMenu.classList.contains('show')) {
      navMenu.classList.remove('show');
      const icon = toggleButton.querySelector('i');
      if (icon) {
        icon.className = 'fas fa-bars';
      }
    }
  }, 500);
});

// =============================================================================
// SETTINGS PAGE MOBILE ENHANCEMENTS
// =============================================================================

// Settings page specific mobile improvements
if (window.location.pathname === '/settings' || document.querySelector('.settings-page-container')) {
  
  // Enhanced tab switching for mobile
  function enhancedShowTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.settings-tab-content').forEach(tab => {
      tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.settings-tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    // Show selected tab
    const targetTab = document.getElementById(tabName);
    const clickedButton = event.target.closest('.settings-tab-btn');
    
    if (targetTab && clickedButton) {
      targetTab.classList.add('active');
      clickedButton.classList.add('active');
      
      // Scroll to top of tab content on mobile
      if (window.innerWidth <= 768) {
        setTimeout(() => {
          targetTab.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }, 100);
      }
    }
  }

  // Override the global showTab function if it exists
  window.showTab = enhancedShowTab;

  // Touch feedback for settings controls
  if ('ontouchstart' in window) {
    // Settings buttons
    document.querySelectorAll('.settings-tab-btn').forEach(btn => {
      btn.addEventListener('touchstart', function(e) {
        this.style.transform = 'scale(0.98)';
      });
      
      btn.addEventListener('touchend', function(e) {
        this.style.transform = 'scale(1)';
      });
    });

    // Action buttons
    document.querySelectorAll('.btn-settings-save, .btn-settings-apply, .btn-settings-reset, .btn-settings-cancel').forEach(btn => {
      btn.addEventListener('touchstart', function(e) {
        this.style.transform = 'scale(0.98)';
      });
      
      btn.addEventListener('touchend', function(e) {
        this.style.transform = 'scale(1)';
      });
    });

    // Category checkboxes
    document.querySelectorAll('.category-checkbox').forEach(checkbox => {
      checkbox.addEventListener('touchstart', function(e) {
        this.style.transform = 'scale(0.99)';
      });
      
      checkbox.addEventListener('touchend', function(e) {
        this.style.transform = 'scale(1)';
      });
    });

    // Color scheme options
    document.querySelectorAll('.color-scheme-option').forEach(option => {
      option.addEventListener('touchstart', function(e) {
        this.style.transform = 'scale(0.98)';
      });
      
      option.addEventListener('touchend', function(e) {
        this.style.transform = 'scale(1)';
      });
    });
  }

  // Mobile-optimized slider handling
  function enhanceSliders() {
    document.querySelectorAll('.settings-slider').forEach(slider => {
      // Add touch event listeners for better mobile experience
      slider.addEventListener('input', function() {
        const valueDisplay = this.nextElementSibling?.querySelector('.slider-value');
        if (valueDisplay) {
          valueDisplay.textContent = this.value;
          
          // Add visual feedback on mobile
          if (window.innerWidth <= 768) {
            valueDisplay.style.transform = 'scale(1.1)';
            setTimeout(() => {
              valueDisplay.style.transform = 'scale(1)';
            }, 150);
          }
        }
      });

      // Improve touch handling for sliders
      if ('ontouchstart' in window) {
        slider.addEventListener('touchstart', function() {
          this.style.height = '12px';
        });
        
        slider.addEventListener('touchend', function() {
          this.style.height = '8px';
        });
      }
    });
  }

  // Enhanced form validation for mobile
  function enhanceMobileFormValidation() {
    const formInputs = document.querySelectorAll('.settings-input, .settings-select, .settings-textarea');
    
    formInputs.forEach(input => {
      // Visual feedback on focus for mobile
      input.addEventListener('focus', function() {
        if (window.innerWidth <= 768) {
          this.style.transform = 'scale(1.02)';
          this.style.transition = 'transform 0.2s ease';
        }
      });
      
      input.addEventListener('blur', function() {
        if (window.innerWidth <= 768) {
          this.style.transform = 'scale(1)';
        }
      });

      // Enhanced validation feedback
      input.addEventListener('invalid', function() {
        if (window.innerWidth <= 768) {
          this.style.animation = 'shake 0.5s ease-in-out';
          setTimeout(() => {
            this.style.animation = '';
          }, 500);
        }
      });
    });
  }

  // Mobile-specific settings page navigation
  function enhanceSettingsNavigation() {
    const tabButtons = document.querySelectorAll('.settings-tab-btn');
    const tabsContainer = document.querySelector('.settings-tabs-nav');
    
    if (tabsContainer && window.innerWidth <= 768) {
      // Add horizontal scroll indicators if needed
      let isScrollable = tabsContainer.scrollWidth > tabsContainer.clientWidth;
      
      if (isScrollable) {
        // Add scroll indicators
        tabsContainer.style.position = 'relative';
        
        // Left scroll indicator
        const leftIndicator = document.createElement('div');
        leftIndicator.className = 'scroll-indicator left';
        leftIndicator.innerHTML = '<i class="fas fa-chevron-left"></i>';
        leftIndicator.style.cssText = `
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 8px;
          border-radius: 50%;
          z-index: 10;
          cursor: pointer;
          display: none;
        `;
        
        // Right scroll indicator
        const rightIndicator = document.createElement('div');
        rightIndicator.className = 'scroll-indicator right';
        rightIndicator.innerHTML = '<i class="fas fa-chevron-right"></i>';
        rightIndicator.style.cssText = `
          position: absolute;
          right: 0;
          top: 50%;
          transform: translateY(-50%);
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 8px;
          border-radius: 50%;
          z-index: 10;
          cursor: pointer;
        `;
        
        // Add click handlers for scroll indicators
        leftIndicator.addEventListener('click', () => {
          tabsContainer.scrollBy({ left: -100, behavior: 'smooth' });
        });
        
        rightIndicator.addEventListener('click', () => {
          tabsContainer.scrollBy({ left: 100, behavior: 'smooth' });
        });
        
        // Show/hide indicators based on scroll position
        tabsContainer.addEventListener('scroll', () => {
          leftIndicator.style.display = tabsContainer.scrollLeft > 0 ? 'block' : 'none';
          rightIndicator.style.display = 
            tabsContainer.scrollLeft < (tabsContainer.scrollWidth - tabsContainer.clientWidth) ? 'block' : 'none';
        });
        
        tabsContainer.parentNode.insertBefore(leftIndicator, tabsContainer);
        tabsContainer.parentNode.insertBefore(rightIndicator, tabsContainer.nextSibling);
        
        // Initial indicator state
        rightIndicator.style.display = 'block';
      }
    }
  }

  // Mobile keyboard handling
  function handleMobileKeyboard() {
    if (/Mobi|Android/i.test(navigator.userAgent)) {
      // Handle virtual keyboard appearance
      window.addEventListener('resize', function() {
        const activeElement = document.activeElement;
        
        if (activeElement && (
          activeElement.tagName === 'INPUT' || 
          activeElement.tagName === 'TEXTAREA' || 
          activeElement.tagName === 'SELECT'
        )) {
          // Scroll active element into view when keyboard appears
          setTimeout(() => {
            activeElement.scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            });
          }, 300);
        }
      });
    }
  }

  // Enhanced mobile message display
  function enhanceMobileMessages() {
    const originalShowMessage = window.showMessage;
    
    if (originalShowMessage) {
      window.showMessage = function(message, type) {
        originalShowMessage(message, type);
        
        // Position messages better on mobile
        if (window.innerWidth <= 768) {
          const messages = document.querySelectorAll('#messageContainer .alert');
          messages.forEach(msg => {
            msg.style.cssText += `
              position: fixed;
              top: 10px;
              left: 10px;
              right: 10px;
              width: auto;
              z-index: 9999;
              font-size: 0.9rem;
              padding: 12px 16px;
            `;
          });
        }
      };
    }
  }

  // Mobile swipe gestures for tab switching
  let touchStartX = 0;
  let touchEndX = 0;
  let currentTabIndex = 0;
  const tabContents = document.querySelectorAll('.settings-tab-content');
  const tabButtons = document.querySelectorAll('.settings-tab-btn');
  
  if (window.innerWidth <= 768 && tabContents.length > 0) {
    document.addEventListener('touchstart', function(e) {
      if (e.target.closest('.settings-tab-content')) {
        touchStartX = e.changedTouches[0].screenX;
      }
    });

    document.addEventListener('touchend', function(e) {
      if (e.target.closest('.settings-tab-content')) {
        touchEndX = e.changedTouches[0].screenX;
        handleTabSwipe();
      }
    });

    function handleTabSwipe() {
      const swipeDistance = touchStartX - touchEndX;
      const minSwipeDistance = 100;
      
      // Find current active tab index
      tabContents.forEach((tab, index) => {
        if (tab.classList.contains('active')) {
          currentTabIndex = index;
        }
      });
      
      // Swipe left - next tab
      if (swipeDistance > minSwipeDistance && currentTabIndex < tabButtons.length - 1) {
        tabButtons[currentTabIndex + 1].click();
      }
      // Swipe right - previous tab
      else if (swipeDistance < -minSwipeDistance && currentTabIndex > 0) {
        tabButtons[currentTabIndex - 1].click();
      }
    }
  }

  // Initialize all mobile enhancements
  document.addEventListener('DOMContentLoaded', function() {
    enhanceSliders();
    enhanceMobileFormValidation();
    enhanceSettingsNavigation();
    handleMobileKeyboard();
    enhanceMobileMessages();
  });

  // Re-enhance on window resize
  window.addEventListener('resize', function() {
    setTimeout(() => {
      enhanceSettingsNavigation();
    }, 250);
  });
}

// Add CSS animations for mobile feedback
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
  
  @media (max-width: 768px) {
    .settings-tab-content {
      transition: transform 0.3s ease, opacity 0.3s ease;
    }
    
    .settings-tab-content:not(.active) {
      opacity: 0;
      transform: translateX(20px);
    }
    
    .settings-tab-content.active {
      opacity: 1;
      transform: translateX(0);
    }
  }
`;
document.head.appendChild(style);
