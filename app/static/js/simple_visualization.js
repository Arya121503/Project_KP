/**
 * Simplified Visualization Dashboard JS
 * Fix for loading issues
 */

class SimpleVisualizationDashboard {
    constructor() {
        this.data = {};
        this.init();
    }

    init() {
        console.log('Initializing Simple Visualization Dashboard...');
        this.loadAllData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Update chart button
        document.getElementById('updateChart')?.addEventListener('click', () => {
            this.loadAllData();
        });

        // Manual refresh button
        document.getElementById('refreshData')?.addEventListener('click', () => {
            this.loadAllData();
        });
    }

    async loadAllData() {
        try {
            this.showLoading();
            
            // Load data sequentially to avoid overload
            await this.loadStats();
            await this.loadLocationData();
            
            this.hideLoading();
            this.showSuccess('Data berhasil dimuat!');
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.hideLoading();
            this.showError('Gagal memuat data: ' + error.message);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/visualization/stats');
            const result = await response.json();
            
            if (result.success) {
                this.data.stats = result.data;
                this.updateStatsDisplay();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
            throw error;
        }
    }

    async loadLocationData() {
        try {
            const response = await fetch('/api/visualization/location-analysis');
            const result = await response.json();
            
            if (result.success) {
                this.data.locationAnalysis = result.data;
                this.updateLocationTable();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Error loading location data:', error);
            throw error;
        }
    }

    updateStatsDisplay() {
        if (!this.data.stats) return;
        
        const stats = this.data.stats;
        
        // Update stats cards safely
        this.updateElement('avgPrice', this.formatCurrency(stats.avg_price));
        this.updateElement('maxPrice', this.formatCurrency(stats.max_price));
        this.updateElement('minPrice', this.formatCurrency(stats.min_price));
        this.updateElement('totalAssets', this.formatNumber(stats.total_assets));
    }

    updateLocationTable() {
        const tableBody = document.getElementById('topPriceTable');
        if (!tableBody || !this.data.locationAnalysis) return;

        tableBody.innerHTML = '';
        
        if (this.data.locationAnalysis.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted">
                        <i class="fas fa-info-circle me-2"></i>Tidak ada data tersedia
                    </td>
                </tr>
            `;
            return;
        }
        
        // Show all kecamatan data
        this.data.locationAnalysis.forEach((location, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="text-center"><strong>${index + 1}</strong></td>
                <td>
                    <div class="d-flex align-items-center">
                        <i class="fas fa-map-marker-alt text-danger me-2"></i>
                        ${location.kecamatan}
                    </div>
                </td>
                <td class="text-end">
                    <strong class="text-success">${this.formatCurrency(location.avg_price)}</strong>
                </td>
                <td class="text-center">
                    <span class="badge bg-primary">${location.total_properties}</span>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    showLoading() {
        // Show loading in stats
        ['avgPrice', 'maxPrice', 'minPrice', 'totalAssets'].forEach(id => {
            this.updateElement(id, '...');
        });
        
        // Show loading in table
        const tableBody = document.getElementById('topPriceTable');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">
                        <i class="fas fa-spinner fa-spin me-2"></i>Memuat data...
                    </td>
                </tr>
            `;
        }
        
        // Update status
        const statusElement = document.getElementById('dataStatus');
        if (statusElement) {
            statusElement.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>Loading...`;
            statusElement.className = 'badge bg-warning me-2';
        }
    }

    hideLoading() {
        // Update status
        const statusElement = document.getElementById('dataStatus');
        if (statusElement) {
            statusElement.innerHTML = `<i class="fas fa-circle me-1"></i>real-time`;
            statusElement.className = 'badge bg-success me-2';
        }
        
        // Update last update time
        const now = new Date();
        const timeString = now.toLocaleString('id-ID', {
            year: 'numeric',
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const lastUpdateElement = document.getElementById('lastUpdateTime');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = timeString;
        }
    }

    showSuccess(message) {
        console.log('Success:', message);
        // You can add toast notification here
    }

    showError(message) {
        console.error('Error:', message);
        alert(message); // Simple error display
    }

    formatCurrency(amount) {
        if (!amount || isNaN(amount)) return 'Rp 0';
        
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatNumber(number) {
        if (!number || isNaN(number)) return '0';
        
        return new Intl.NumberFormat('id-ID').format(number);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Simple Visualization Dashboard...');
    
    // Wait a bit for all elements to be ready
    setTimeout(() => {
        try {
            window.simpleVisualizationDashboard = new SimpleVisualizationDashboard();
            
            // Add global refresh function
            window.refreshVisualizationData = () => {
                if (window.simpleVisualizationDashboard) {
                    window.simpleVisualizationDashboard.loadAllData();
                }
            };
            
            console.log('Simple Visualization Dashboard initialized successfully');
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
        }
    }, 500);
});

// Export for global access
window.SimpleVisualizationDashboard = SimpleVisualizationDashboard;
