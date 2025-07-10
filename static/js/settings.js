/**
 * ThreatSense Analytics - Settings Modal JavaScript
 * Handles configuration panel interactions and settings persistence
 */

class SettingsManager {
    constructor() {
        console.log('SettingsManager constructor called');
        this.modal = null;
        this.currentTab = 'detection';
        this.settings = this.getDefaultSettings();
        this.initializeModal();
        this.bindEvents();
        this.loadSettings();
        console.log('SettingsManager constructor completed');
    }

    getDefaultSettings() {
        return {
            detection: {
                sensitivity: 75,
                realTimeAnalysis: true,
                autoFlag: true,
                customPatterns: '',
                enableGrooming: true,
                enableIsolation: true,
                enableCoercion: true,
                enableInappropriate: true,
                enableMeeting: true
            },
            analysis: {
                sentimentAnalysis: true,
                patternMatching: true,
                riskScoring: true,
                detailedReports: true,
                batchSize: 100,
                processingDelay: 500
            },
            interface: {
                darkMode: true,
                animations: true,
                notifications: true,
                autoRefresh: false,
                compactView: false,
                showAdvanced: false
            },
            alerts: {
                emailNotifications: false,
                soundAlerts: true,
                browserNotifications: true,
                highRiskOnly: false,
                alertThreshold: 50
            }
        };
    }

    initializeModal() {
        console.log('Initializing modal...');
        this.modal = document.getElementById('settingsModal');
        console.log('Modal element found:', this.modal);
        
        if (!this.modal) {
            console.error('Settings modal not found');
            return;
        }
    }

    bindEvents() {
        console.log('SettingsManager: Binding events...');
        
        // Settings button in navbar
        const settingsBtn = document.querySelector('[data-action="settings"]');
        console.log('Settings button found:', settingsBtn);
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', (e) => {
                console.log('Settings button clicked!');
                e.preventDefault();
                this.openModal();
            });
        } else {
            console.error('Settings button not found!');
        }

        // Close modal events
        const closeBtn = this.modal?.querySelector('.close-modal');
        const cancelBtn = this.modal?.querySelector('[data-action="cancel"]');
        
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeModal());
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.closeModal());

        // Close on outside click
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Tab switching
        const tabButtons = this.modal?.querySelectorAll('.tab-btn');
        tabButtons?.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                this.switchTab(tabId);
            });
        });

        // Save and apply buttons
        const saveBtn = this.modal?.querySelector('[data-action="save"]');
        const applyBtn = this.modal?.querySelector('[data-action="apply"]');
        const resetBtn = this.modal?.querySelector('[data-action="reset"]');

        if (saveBtn) saveBtn.addEventListener('click', () => this.saveSettings());
        if (applyBtn) applyBtn.addEventListener('click', () => this.applySettings());
        if (resetBtn) resetBtn.addEventListener('click', () => this.resetSettings());

        // Real-time updates for sliders and toggles
        this.bindSettingsControls();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal?.classList.contains('active')) {
                this.closeModal();
            }
        });
    }

    bindSettingsControls() {
        if (!this.modal) return;

        // Sliders
        const sliders = this.modal.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.addEventListener('input', (e) => {
                this.updateSliderValue(e.target);
                this.updateSetting(e.target.id, parseInt(e.target.value));
            });
        });

        // Toggles (checkboxes)
        const toggles = this.modal.querySelectorAll('input[type="checkbox"]');
        toggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.updateSetting(e.target.id, e.target.checked);
            });
        });

        // Text inputs
        const textInputs = this.modal.querySelectorAll('input[type="text"], textarea');
        textInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateSetting(e.target.id, e.target.value);
            });
        });

        // Number inputs
        const numberInputs = this.modal.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateSetting(e.target.id, parseInt(e.target.value));
            });
        });
    }

    updateSliderValue(slider) {
        const valueDisplay = slider.nextElementSibling?.querySelector('.slider-value');
        if (valueDisplay) {
            valueDisplay.textContent = slider.value + (slider.dataset.unit || '');
        }
    }

    updateSetting(settingId, value) {
        // Parse setting ID to get category and setting name
        const [category, setting] = this.parseSettingId(settingId);
        
        if (category && setting && this.settings[category]) {
            this.settings[category][setting] = value;
            
            // Show unsaved changes indicator
            this.showUnsavedChanges();
        }
    }

    parseSettingId(settingId) {
        // Convert camelCase to category_setting format
        // e.g., 'detectionSensitivity' -> ['detection', 'sensitivity']
        const categories = ['detection', 'analysis', 'interface', 'alerts'];
        
        for (const category of categories) {
            if (settingId.startsWith(category)) {
                const setting = settingId.substring(category.length);
                return [category, setting.charAt(0).toLowerCase() + setting.slice(1)];
            }
        }
        
        return [null, null];
    }

    showUnsavedChanges() {
        const indicator = this.modal?.querySelector('.unsaved-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }

    hideUnsavedChanges() {
        const indicator = this.modal?.querySelector('.unsaved-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    openModal() {
        if (!this.modal) return;
        
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = this.modal.querySelector('input, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }

        // Log modal open event
        this.logEvent('settings_modal_opened');
    }

    closeModal() {
        if (!this.modal) return;
        
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Check for unsaved changes
        if (this.hasUnsavedChanges()) {
            if (confirm('You have unsaved changes. Are you sure you want to close?')) {
                this.hideUnsavedChanges();
            } else {
                this.openModal();
                return;
            }
        }

        this.logEvent('settings_modal_closed');
    }

    switchTab(tabId) {
        if (!this.modal) return;
        
        this.currentTab = tabId;
        
        // Update tab buttons
        const tabButtons = this.modal.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });
        
        // Update tab content
        const tabContents = this.modal.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabId}Tab`);
        });

        this.logEvent('settings_tab_switched', { tab: tabId });
    }

    loadSettings() {
        try {
            // Load from localStorage first
            const saved = localStorage.getItem('threatSenseSettings');
            if (saved) {
                this.settings = { ...this.settings, ...JSON.parse(saved) };
            }

            // Apply settings to UI
            this.applySettingsToUI();
            
            this.logEvent('settings_loaded');
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showNotification('Error loading settings', 'error');
        }
    }

    saveSettings() {
        try {
            // Save to localStorage
            localStorage.setItem('threatSenseSettings', JSON.stringify(this.settings));
            
            // Send to server (optional)
            this.sendSettingsToServer();
            
            this.hideUnsavedChanges();
            this.showNotification('Settings saved successfully', 'success');
            this.logEvent('settings_saved');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showNotification('Error saving settings', 'error');
        }
    }

    async sendSettingsToServer() {
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.settings)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Settings saved to server:', result);
            
        } catch (error) {
            console.warn('Could not save settings to server:', error);
            // Continue with local storage only
        }
    }

    applySettings() {
        this.saveSettings();
        
        // Apply immediate changes
        this.applyInterfaceSettings();
        this.applyDetectionSettings();
        
        this.showNotification('Settings applied successfully', 'success');
        this.logEvent('settings_applied');
    }

    applySettingsToUI() {
        if (!this.modal) return;

        // Detection settings
        this.setSliderValue('detectionSensitivity', this.settings.detection.sensitivity);
        this.setCheckbox('detectionRealTimeAnalysis', this.settings.detection.realTimeAnalysis);
        this.setCheckbox('detectionAutoFlag', this.settings.detection.autoFlag);
        this.setTextValue('detectionCustomPatterns', this.settings.detection.customPatterns);
        this.setCheckbox('detectionEnableGrooming', this.settings.detection.enableGrooming);
        this.setCheckbox('detectionEnableIsolation', this.settings.detection.enableIsolation);
        this.setCheckbox('detectionEnableCoercion', this.settings.detection.enableCoercion);
        this.setCheckbox('detectionEnableInappropriate', this.settings.detection.enableInappropriate);
        this.setCheckbox('detectionEnableMeeting', this.settings.detection.enableMeeting);

        // Analysis settings
        this.setCheckbox('analysisSentimentAnalysis', this.settings.analysis.sentimentAnalysis);
        this.setCheckbox('analysisPatternMatching', this.settings.analysis.patternMatching);
        this.setCheckbox('analysisRiskScoring', this.settings.analysis.riskScoring);
        this.setCheckbox('analysisDetailedReports', this.settings.analysis.detailedReports);
        this.setNumberValue('analysisBatchSize', this.settings.analysis.batchSize);
        this.setSliderValue('analysisProcessingDelay', this.settings.analysis.processingDelay);

        // Interface settings
        this.setCheckbox('interfaceDarkMode', this.settings.interface.darkMode);
        this.setCheckbox('interfaceAnimations', this.settings.interface.animations);
        this.setCheckbox('interfaceNotifications', this.settings.interface.notifications);
        this.setCheckbox('interfaceAutoRefresh', this.settings.interface.autoRefresh);
        this.setCheckbox('interfaceCompactView', this.settings.interface.compactView);
        this.setCheckbox('interfaceShowAdvanced', this.settings.interface.showAdvanced);

        // Alert settings
        this.setCheckbox('alertsEmailNotifications', this.settings.alerts.emailNotifications);
        this.setCheckbox('alertsSoundAlerts', this.settings.alerts.soundAlerts);
        this.setCheckbox('alertsBrowserNotifications', this.settings.alerts.browserNotifications);
        this.setCheckbox('alertsHighRiskOnly', this.settings.alerts.highRiskOnly);
        this.setSliderValue('alertsAlertThreshold', this.settings.alerts.alertThreshold);
    }

    setSliderValue(id, value) {
        const slider = this.modal?.querySelector(`#${id}`);
        if (slider) {
            slider.value = value;
            this.updateSliderValue(slider);
        }
    }

    setCheckbox(id, checked) {
        const checkbox = this.modal?.querySelector(`#${id}`);
        if (checkbox) {
            checkbox.checked = checked;
        }
    }

    setTextValue(id, value) {
        const input = this.modal?.querySelector(`#${id}`);
        if (input) {
            input.value = value || '';
        }
    }

    setNumberValue(id, value) {
        const input = this.modal?.querySelector(`#${id}`);
        if (input) {
            input.value = value;
        }
    }

    applyInterfaceSettings() {
        const { interface: ui } = this.settings;
        
        // Apply dark mode (though it's permanent in this design)
        document.body.classList.toggle('dark-mode', ui.darkMode);
        
        // Apply animations
        document.body.classList.toggle('no-animations', !ui.animations);
        
        // Apply compact view
        document.body.classList.toggle('compact-view', ui.compactView);
    }

    applyDetectionSettings() {
        // This would typically update the backend analysis engine
        // For now, we'll store settings for the next analysis
        window.threatSenseSettings = this.settings;
    }

    resetSettings() {
        if (confirm('Are you sure you want to reset all settings to defaults?')) {
            this.settings = this.getDefaultSettings();
            this.applySettingsToUI();
            this.showUnsavedChanges();
            this.showNotification('Settings reset to defaults', 'info');
            this.logEvent('settings_reset');
        }
    }

    hasUnsavedChanges() {
        const indicator = this.modal?.querySelector('.unsaved-indicator');
        return indicator && indicator.style.display !== 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: this.getNotificationColor(type),
            color: 'white',
            padding: '12px 16px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            zIndex: '10001',
            minWidth: '300px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            animation: 'slideInRight 0.3s ease'
        });

        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.style.cssText = 'background: none; border: none; color: white; font-size: 18px; cursor: pointer; padding: 0; margin-left: 10px;';
        
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#007bff'
        };
        return colors[type] || '#007bff';
    }

    logEvent(action, details = {}) {
        // Log settings events for analytics
        try {
            fetch('/api/log-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action,
                    details,
                    timestamp: new Date().toISOString()
                })
            }).catch(err => console.warn('Could not log event:', err));
        } catch (error) {
            console.warn('Event logging error:', error);
        }
    }

    // Public API
    getSetting(category, setting) {
        return this.settings[category]?.[setting];
    }

    setSetting(category, setting, value) {
        if (this.settings[category]) {
            this.settings[category][setting] = value;
            this.showUnsavedChanges();
        }
    }

    exportSettings() {
        const blob = new Blob([JSON.stringify(this.settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'threatsense-settings.json';
        a.click();
        URL.revokeObjectURL(url);
        
        this.logEvent('settings_exported');
    }

    importSettings(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const imported = JSON.parse(e.target.result);
                this.settings = { ...this.getDefaultSettings(), ...imported };
                this.applySettingsToUI();
                this.showUnsavedChanges();
                this.showNotification('Settings imported successfully', 'success');
                this.logEvent('settings_imported');
            } catch (error) {
                this.showNotification('Error importing settings file', 'error');
            }
        };
        reader.readAsText(file);
    }
}

// Initialize settings manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing SettingsManager...');
    try {
        window.settingsManager = new SettingsManager();
        console.log('SettingsManager initialized successfully');
    } catch (error) {
        console.error('Error initializing SettingsManager:', error);
    }
    
    // Add CSS animations if not present
    if (!document.querySelector('#settings-animations')) {
        const style = document.createElement('style');
        style.id = 'settings-animations';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .no-animations * {
                animation-duration: 0s !important;
                transition-duration: 0s !important;
            }
            
            .compact-view .stat-card {
                padding: 10px !important;
            }
            
            .compact-view .feature-card {
                padding: 15px !important;
            }
        `;
        document.head.appendChild(style);
    }
});

// Export for external use
window.ThreatSenseSettings = SettingsManager;
