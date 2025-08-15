// ===== NIS2 SUPPLY CHAIN - JAVASCRIPT PROFESSIONALE =====

class NIS2ProfessionalUI {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSidebar();
        this.setupAnimations();
        this.setupCharts();
        this.setupNotifications();
    }

    // ===== SETUP EVENT LISTENERS =====
    setupEventListeners() {
        // Mobile menu toggle
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }

        // Sidebar navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleNavigation(e);
            });
        });

        // User menu dropdown
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.addEventListener('click', () => {
                this.toggleUserMenu();
            });
        }

        // Form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });

        // Button interactions
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleButtonClick(e);
            });
        });

        // Table row interactions
        const tableRows = document.querySelectorAll('.table tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('click', (e) => {
                this.handleTableRowClick(e);
            });
        });

        // Card interactions
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.animateCardHover(card, true);
            });
            card.addEventListener('mouseleave', () => {
                this.animateCardHover(card, false);
            });
        });
    }

    // ===== SIDEBAR MANAGEMENT =====
    setupSidebar() {
        // Set active navigation item based on current page
        this.setActiveNavigationItem();
        
        // Handle sidebar collapse on mobile
        if (window.innerWidth <= 1024) {
            this.collapseSidebar();
        }
    }

    setActiveNavigationItem() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath.includes(href)) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    toggleMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar.classList.contains('open')) {
            this.collapseSidebar();
        } else {
            this.expandSidebar();
        }
    }

    expandSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.add('open');
        
        // Create overlay
        if (!document.querySelector('.sidebar-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 999;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(overlay);
            
            setTimeout(() => {
                overlay.style.opacity = '1';
            }, 10);
            
            overlay.addEventListener('click', () => {
                this.collapseSidebar();
            });
        }
    }

    collapseSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        sidebar.classList.remove('open');
        
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    }

    // ===== NAVIGATION HANDLING =====
    handleNavigation(e) {
        const item = e.currentTarget;
        const href = item.getAttribute('href');
        
        if (href && !href.startsWith('#')) {
            // Add loading state
            this.showLoading();
            
            // Remove active class from all items
            document.querySelectorAll('.nav-item').forEach(nav => {
                nav.classList.remove('active');
            });
            
            // Add active class to clicked item
            item.classList.add('active');
            
            // Navigate after a short delay for smooth transition
            setTimeout(() => {
                window.location.href = href;
            }, 150);
        }
    }

    // ===== USER MENU =====
    toggleUserMenu() {
        const userMenu = document.querySelector('.user-menu');
        const dropdown = document.querySelector('.user-dropdown');
        
        if (dropdown) {
            dropdown.remove();
        } else {
            this.createUserDropdown();
        }
    }

    createUserDropdown() {
        const userMenu = document.querySelector('.user-menu');
        const dropdown = document.createElement('div');
        dropdown.className = 'user-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            right: 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            min-width: 200px;
            z-index: 1000;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.2s ease;
        `;
        
        dropdown.innerHTML = `
            <div class="p-3 border-b border-gray-100">
                <div class="font-semibold text-primary">Admin User</div>
                <div class="text-sm text-secondary">admin@company.com</div>
            </div>
            <div class="p-2">
                <a href="/profile" class="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
                    <i class="fas fa-user mr-2"></i> Profilo
                </a>
                <a href="/settings" class="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
                    <i class="fas fa-cog mr-2"></i> Impostazioni
                </a>
                <hr class="my-2">
                <a href="/logout" class="block px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded">
                    <i class="fas fa-sign-out-alt mr-2"></i> Logout
                </a>
            </div>
        `;
        
        userMenu.style.position = 'relative';
        userMenu.appendChild(dropdown);
        
        setTimeout(() => {
            dropdown.style.opacity = '1';
            dropdown.style.transform = 'translateY(0)';
        }, 10);
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenu.contains(e.target)) {
                dropdown.remove();
            }
        });
    }

    // ===== FORM HANDLING =====
    handleFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> Invio...';
            submitBtn.disabled = true;
            
            // Re-enable after 3 seconds if no response
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 3000);
        }
    }

    // ===== BUTTON HANDLING =====
    handleButtonClick(e) {
        const button = e.currentTarget;
        const action = button.getAttribute('data-action');
        
        switch (action) {
            case 'generate-pdf':
                this.handlePDFGeneration(button);
                break;
            case 'delete':
                this.handleDelete(button);
                break;
            case 'export':
                this.handleExport(button);
                break;
            default:
                // Default button behavior
                break;
        }
    }

    handlePDFGeneration(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="loading"></span> Generazione PDF...';
        button.disabled = true;
        
        // Simulate PDF generation
        setTimeout(() => {
            this.showNotification('PDF generato con successo!', 'success');
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }

    handleDelete(button) {
        if (confirm('Sei sicuro di voler eliminare questo elemento?')) {
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="loading"></span> Eliminazione...';
            button.disabled = true;
            
            setTimeout(() => {
                this.showNotification('Elemento eliminato con successo!', 'success');
                button.closest('tr')?.remove();
            }, 1000);
        }
    }

    handleExport(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="loading"></span> Esportazione...';
        button.disabled = true;
        
        setTimeout(() => {
            this.showNotification('Dati esportati con successo!', 'success');
            button.innerHTML = originalText;
            button.disabled = false;
        }, 1500);
    }

    // ===== TABLE INTERACTIONS =====
    handleTableRowClick(e) {
        const row = e.currentTarget;
        const dataId = row.getAttribute('data-id');
        
        if (dataId) {
            // Add highlight effect
            row.style.backgroundColor = '#f3f4f6';
            setTimeout(() => {
                row.style.backgroundColor = '';
            }, 200);
            
            // Navigate to detail page
            window.location.href = `/supplier/${dataId}`;
        }
    }

    // ===== ANIMATIONS =====
    setupAnimations() {
        // Animate elements on page load
        const animatedElements = document.querySelectorAll('.card, .stat-card, .table-container');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });
        
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }

    animateCardHover(card, isHovering) {
        if (isHovering) {
            card.style.transform = 'translateY(-4px)';
            card.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
        } else {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
        }
    }

    // ===== CHARTS SETUP =====
    setupCharts() {
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            this.initializeCharts();
        }
    }

    initializeCharts() {
        // Compliance Score Chart
        const complianceCtx = document.getElementById('complianceChart');
        if (complianceCtx) {
            new Chart(complianceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Conforme', 'Non Conforme', 'In Valutazione'],
                    datasets: [{
                        data: [65, 20, 15],
                        backgroundColor: ['#059669', '#dc2626', '#ca8a04'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }

        // Monthly Trends Chart
        const trendsCtx = document.getElementById('trendsChart');
        if (trendsCtx) {
            new Chart(trendsCtx, {
                type: 'line',
                data: {
                    labels: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu'],
                    datasets: [{
                        label: 'Assessments Completati',
                        data: [12, 19, 15, 25, 22, 30],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#f3f4f6'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }

    // ===== NOTIFICATIONS =====
    setupNotifications() {
        // Create notification container
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        const notification = document.createElement('div');
        
        const typeConfig = {
            success: { icon: '✅', bgColor: '#f0fdf4', borderColor: '#059669', textColor: '#059669' },
            error: { icon: '❌', bgColor: '#fef2f2', borderColor: '#dc2626', textColor: '#dc2626' },
            warning: { icon: '⚠️', bgColor: '#fffbeb', borderColor: '#ea580c', textColor: '#ea580c' },
            info: { icon: 'ℹ️', bgColor: '#eff6ff', borderColor: '#3b82f6', textColor: '#3b82f6' }
        };
        
        const config = typeConfig[type] || typeConfig.info;
        
        notification.style.cssText = `
            background: ${config.bgColor};
            border: 1px solid ${config.borderColor};
            color: ${config.textColor};
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            font-weight: 500;
        `;
        
        notification.innerHTML = `
            <span style="font-size: 1.25rem;">${config.icon}</span>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: inherit; cursor: pointer; font-size: 1.25rem;">×</button>
        `;
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    }

    // ===== LOADING STATES =====
    showLoading() {
        const loading = document.createElement('div');
        loading.className = 'page-loading';
        loading.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        
        loading.innerHTML = `
            <div style="text-align: center;">
                <div class="loading" style="width: 40px; height: 40px; margin: 0 auto 1rem;"></div>
                <div style="color: #1e3a8a; font-weight: 600;">Caricamento...</div>
            </div>
        `;
        
        document.body.appendChild(loading);
    }

    hideLoading() {
        const loading = document.querySelector('.page-loading');
        if (loading) {
            loading.remove();
        }
    }

    // ===== UTILITY METHODS =====
    formatNumber(num) {
        return new Intl.NumberFormat('it-IT').format(num);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('it-IT', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('it-IT', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    window.nis2UI = new NIS2ProfessionalUI();
});

// ===== GLOBAL UTILITY FUNCTIONS =====
window.showNotification = (message, type, duration) => {
    if (window.nis2UI) {
        window.nis2UI.showNotification(message, type, duration);
    }
};

window.showLoading = () => {
    if (window.nis2UI) {
        window.nis2UI.showLoading();
    }
};

window.hideLoading = () => {
    if (window.nis2UI) {
        window.nis2UI.hideLoading();
    }
};
