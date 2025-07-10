/**
 * Visualization Dashboard JS
 * Handles all chart rendering and data fetching for admin dashboard
 */

class VisualizationDashboard {
    constructor() {
        this.charts = {};
        this.data = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.initializeCharts();
        this.loadAllData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    startAutoRefresh() {
        // Auto refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadAllData();
        }, 300000); // 5 minutes
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    setupEventListeners() {
        // Update chart button
        document.getElementById('updateChart')?.addEventListener('click', () => {
            this.updateMainChart();
        });

        // Export buttons
        document.getElementById('generateReport')?.addEventListener('click', () => {
            this.generateCustomReport();
        });

        // Optimized filter change handlers with debouncing
        ['chartType', 'dataSource', 'groupBy', 'metric'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', (e) => {
                const filters = this.collectFilters();
                this.debouncedApplyFilters(filters);
            });
        });
        
        // Additional filter elements
        ['filterKecamatan', 'filterPropertyType', 'filterPriceRange', 'filterDateRange'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', (e) => {
                const filters = this.collectFilters();
                this.debouncedApplyFilters(filters);
            });
        });
        
        // Window resize handler
        window.addEventListener('resize', () => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.handleChartResize();
            }, 250);
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.destroy();
        });
    }

    collectFilters() {
        const filters = {};
        
        // Collect all filter values
        const filterElements = [
            'chartType', 'dataSource', 'groupBy', 'metric',
            'filterKecamatan', 'filterPropertyType', 'filterPriceRange', 'filterDateRange'
        ];
        
        filterElements.forEach(id => {
            const element = document.getElementById(id);
            if (element && element.value) {
                filters[id] = element.value;
            }
        });
        
        return filters;
    }

    async loadAllData() {
        try {
            // Show loading state
            this.showLoadingState();
            
            // Load essential data first (quick stats)
            await this.loadEssentialData();
            await this.loadDetailedData();
            
            // Update all charts
            this.updateAllCharts();
            
            // Hide loading state
            this.hideLoadingState();
            
            console.log('All data loaded successfully');
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Error loading data: ' + error.message);
            this.hideLoadingState();
        }
    }

    showLoadingState() {
        // Show loading spinner in stats
        ['avgPrice', 'maxPrice', 'minPrice', 'totalAssets'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = '<i class="fas fa-spinner fa-spin text-muted"></i>';
            }
        });
        
        // Show loading in table
        const tableBody = document.getElementById('topPriceTable');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">
                        <i class="fas fa-spinner fa-spin me-2"></i>Loading data...
                    </td>
                </tr>
            `;
        }
        
        // Update status
        const statusElement = document.getElementById('dataStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <i class="fas fa-spinner fa-spin me-1"></i>Loading...
            `;
            statusElement.className = 'badge bg-warning me-2';
        }
    }

    hideLoadingState() {
        // Stats will be updated by updateStatsDisplay
        this.showSuccessMessage('Data berhasil dimuat dan diperbarui!');
        
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

    async loadStatistics() {
        const response = await fetch('/api/visualization/stats');
        const result = await response.json();
        
        if (result.success) {
            this.data.stats = result.data;
            this.updateStatsDisplay();
        } else {
            throw new Error(result.error);
        }
    }

    async loadLocationAnalysis() {
        const response = await fetch('/api/visualization/location-analysis');
        const result = await response.json();
        
        if (result.success) {
            this.data.locationAnalysis = result.data;
            this.updateLocationTable();
        } else {
            throw new Error(result.error);
        }
    }

    async loadPropertyTypeDistribution() {
        const response = await fetch('/api/visualization/property-type-distribution');
        const result = await response.json();
        
        if (result.success) {
            this.data.propertyTypes = result.data;
        } else {
            throw new Error(result.error);
        }
    }

    async loadCertificateAnalysis() {
        const response = await fetch('/api/visualization/certificate-analysis');
        const result = await response.json();
        
        if (result.success) {
            this.data.certificates = result.data;
        } else {
            throw new Error(result.error);
        }
    }

    async loadPriceRangeDistribution() {
        const response = await fetch('/api/visualization/price-range-distribution');
        const result = await response.json();
        
        if (result.success) {
            this.data.priceRanges = result.data;
        } else {
            throw new Error(result.error);
        }
    }

    async loadTrendAnalysis() {
        const response = await fetch('/api/visualization/trend-analysis');
        const result = await response.json();
        
        if (result.success) {
            this.data.trendAnalysis = result.data;
        } else {
            throw new Error(result.error);
        }
    }

    async loadModelPerformance() {
        const response = await fetch('/api/visualization/model-performance');
        const result = await response.json();
        
        if (result.success) {
            this.data.modelPerformance = result.data;
        } else {
            throw new Error(result.error);
        }
    }

    async loadDataInfo() {
        const response = await fetch('/api/visualization/data-info');
        const result = await response.json();
        
        if (result.success) {
            this.data.dataInfo = result.data;
            this.updateDataStatus();
        } else {
            throw new Error(result.error);
        }
    }

    async loadQuickStats() {
        try {
            const response = await fetch('/api/visualization/quick-stats');
            const result = await response.json();
            
            if (result.success) {
                this.data.quickStats = result.data;
                this.updateQuickStatsDisplay();
            }
        } catch (error) {
            console.error('Error loading quick stats:', error);
        }
    }

    updateQuickStatsDisplay() {
        if (!this.data.quickStats) return;
        
        const stats = this.data.quickStats;
        
        // Update quick stats cards with animation
        this.animateNumber('avgPrice', stats.avg_price, this.formatCurrency);
        this.animateNumber('maxPrice', stats.max_price, this.formatCurrency);
        this.animateNumber('minPrice', stats.min_price, this.formatCurrency);
        this.animateNumber('totalAssets', stats.total_assets, this.formatNumber);
    }

    animateNumber(elementId, targetValue, formatter) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent.replace(/[^\d]/g, '')) || 0;
        const duration = 1000; // 1 second
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = startValue + (targetValue - startValue) * progress;
            element.textContent = formatter(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    async loadEssentialData() {
        try {
            // Load most important data first
            const [
                statsResponse,
                locationResponse,
                dataInfoResponse
            ] = await Promise.all([
                this.loadStatistics(),
                this.loadLocationAnalysis(),
                this.loadDataInfo()
            ]);
            
            // Update essential displays immediately
            this.updateStatsDisplay();
            this.updateLocationTable();
            this.updateDataStatus();
            
        } catch (error) {
            console.error('Error loading essential data:', error);
        }
    }

    async loadDetailedData() {
        try {
            // Load detailed data in smaller batches
            const batch1 = await Promise.all([
                this.loadPropertyTypeDistribution(),
                this.loadCertificateAnalysis()
            ]);
            
            const batch2 = await Promise.all([
                this.loadPriceRangeDistribution(),
                this.loadTrendAnalysis()
            ]);
            
            // Load model performance separately as it's less critical
            await this.loadModelPerformance();
            
        } catch (error) {
            console.error('Error loading detailed data:', error);
        }
    }

    // Optimized filter method
    async applyFilters(filters = {}) {
        try {
            this.showLoadingState();
            
            // Use the optimized filtered-data endpoint
            const response = await fetch('/api/visualization/filtered-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(filters)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update data with filtered results
                this.data.filteredData = result.data;
                this.updateFilteredDisplays();
                
                // Show success notification
                this.showNotification('Filter berhasil diterapkan', 'success');
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('Error applying filters:', error);
            this.showNotification('Gagal menerapkan filter', 'error');
        } finally {
            this.hideLoadingState();
        }
    }

    updateFilteredDisplays() {
        if (!this.data.filteredData) return;
        
        // Update main chart with filtered data
        this.updateMainChartWithFilteredData();
        
        // Update location table with filtered data
        this.updateLocationTableWithFilteredData();
        
        // Update other charts as needed
        this.updateChartsWithFilteredData();
    }

    updateMainChartWithFilteredData() {
        if (!this.charts.main || !this.data.filteredData.location_analysis) return;
        
        const data = this.data.filteredData.location_analysis;
        const labels = data.map(item => item.kecamatan);
        const values = data.map(item => item.avg_price);
        
        this.charts.main.data.labels = labels;
        this.charts.main.data.datasets[0].data = values;
        this.charts.main.update('none'); // No animation for better performance
    }

    updateLocationTableWithFilteredData() {
        if (!this.data.filteredData.location_analysis) return;
        
        const tableBody = document.getElementById('topPriceTable');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        this.data.filteredData.location_analysis.forEach((location, index) => {
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

    updateChartsWithFilteredData() {
        // Update other charts with filtered data
        if (this.data.filteredData.property_types && this.charts.propertyType) {
            this.updatePropertyTypeChart(this.data.filteredData.property_types);
        }
        
        if (this.data.filteredData.certificates && this.charts.certificate) {
            this.updateCertificateChart(this.data.filteredData.certificates);
        }
        
        if (this.data.filteredData.price_ranges && this.charts.priceRange) {
            this.updatePriceRangeChart(this.data.filteredData.price_ranges);
        }
    }

    // Debounced filter application
    debouncedApplyFilters = this.debounce(this.applyFilters.bind(this), 300);
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    initializeCharts() {
        // Initialize all chart containers
        this.initMainChart();
        this.initPropertyTypeChart();
        this.initLocationChart();
        this.initTrendChart();
        this.initModelMetricsChart();
        this.initCertificateChart();
        this.initPricePerSqmChart();
    }

    initMainChart() {
        const ctx = document.getElementById('mainChart');
        if (!ctx) return;

        this.charts.main = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Harga Rata-rata',
                    data: [],
                    backgroundColor: 'rgba(220, 20, 60, 0.8)',
                    borderColor: 'rgba(220, 20, 60, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `Harga: ${this.formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    initPropertyTypeChart() {
        const ctx = document.getElementById('propertyTypeChart');
        if (!ctx) return;

        this.charts.propertyType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(220, 20, 60, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(0, 123, 255, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initLocationChart() {
        const ctx = document.getElementById('locationChart');
        if (!ctx) return;

        this.charts.location = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Jumlah Properti',
                    data: [],
                    backgroundColor: 'rgba(23, 162, 184, 0.8)',
                    borderColor: 'rgba(23, 162, 184, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Trend Harga',
                    data: [],
                    backgroundColor: 'rgba(255, 193, 7, 0.2)',
                    borderColor: 'rgba(255, 193, 7, 1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                }
            }
        });
    }

    initModelMetricsChart() {
        const ctx = document.getElementById('modelMetricsChart');
        if (!ctx) return;

        this.charts.modelMetrics = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                datasets: [
                    {
                        label: 'Random Forest',
                        data: [94.2, 93.8, 94.5, 94.1],
                        backgroundColor: 'rgba(23, 162, 184, 0.2)',
                        borderColor: 'rgba(23, 162, 184, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'XGBoost',
                        data: [92.8, 92.3, 93.1, 92.7],
                        backgroundColor: 'rgba(255, 193, 7, 0.2)',
                        borderColor: 'rgba(255, 193, 7, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'CatBoost',
                        data: [93.5, 93.2, 93.8, 93.5],
                        backgroundColor: 'rgba(40, 167, 69, 0.2)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    initCertificateChart() {
        const ctx = document.getElementById('certificateChart');
        if (!ctx) return;

        this.charts.certificate = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(220, 20, 60, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(0, 123, 255, 0.8)',
                        'rgba(108, 117, 125, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initPricePerSqmChart() {
        const ctx = document.getElementById('pricePerSqmChart');
        if (!ctx) return;

        this.charts.pricePerSqm = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Jumlah Properti',
                    data: [],
                    backgroundColor: 'rgba(52, 58, 64, 0.8)',
                    borderColor: 'rgba(52, 58, 64, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateAllCharts() {
        this.updateMainChart();
        this.updatePropertyTypeChart();
        this.updateLocationChart();
        this.updateTrendChart();
        this.updateCertificateChart();
        this.updatePricePerSqmChart();
    }

    updateMainChart() {
        if (!this.charts.main || !this.data.locationAnalysis) return;

        const chart = this.charts.main;
        const data = this.data.locationAnalysis;
        
        // Get filter values
        const chartType = document.getElementById('chartType')?.value || 'bar';
        const dataSource = document.getElementById('dataSource')?.value || 'both';
        const metric = document.getElementById('metric')?.value || 'avgPrice';
        
        // Filter data based on source
        let filteredData = data;
        if (dataSource === 'tanah') {
            filteredData = data.filter(item => item.tanah_count > 0);
        } else if (dataSource === 'bangunan') {
            filteredData = data.filter(item => item.bangunan_count > 0);
        }
        
        // Update chart type
        chart.config.type = chartType;
        
        // Prepare data based on metric
        let chartData, chartLabels;
        
        switch (metric) {
            case 'avgPrice':
                chartLabels = filteredData.map(item => item.kecamatan);
                chartData = filteredData.map(item => item.avg_price);
                chart.data.datasets[0].label = 'Harga Rata-rata';
                break;
            case 'totalValue':
                chartLabels = filteredData.map(item => item.kecamatan);
                chartData = filteredData.map(item => item.total_value);
                chart.data.datasets[0].label = 'Total Nilai';
                break;
            case 'count':
                chartLabels = filteredData.map(item => item.kecamatan);
                chartData = filteredData.map(item => item.total_properties);
                chart.data.datasets[0].label = 'Jumlah Properti';
                break;
            case 'price_per_sqm':
                chartLabels = filteredData.map(item => item.kecamatan);
                chartData = filteredData.map(item => item.avg_price / (item.avg_land_area || 1));
                chart.data.datasets[0].label = 'Harga per M²';
                break;
            default:
                chartLabels = filteredData.map(item => item.kecamatan);
                chartData = filteredData.map(item => item.avg_price);
                chart.data.datasets[0].label = 'Harga Rata-rata';
        }
        
        chart.data.labels = chartLabels;
        chart.data.datasets[0].data = chartData;
        chart.update();
        
        // Update chart title based on filters
        this.updateChartTitle('mainChart', `${chart.data.datasets[0].label} - ${dataSource === 'both' ? 'Semua Data' : dataSource === 'tanah' ? 'Data Tanah' : 'Data Bangunan'}`);
    }

    updateChartTitle(chartId, title) {
        const chartContainer = document.getElementById(chartId)?.closest('.card');
        if (chartContainer) {
            const titleElement = chartContainer.querySelector('.card-header h6');
            if (titleElement) {
                const icon = titleElement.querySelector('i');
                titleElement.innerHTML = `${icon ? icon.outerHTML : ''} ${title}`;
            }
        }
    }

    updatePropertyTypeChart() {
        if (!this.charts.propertyType || !this.data.propertyTypes) return;

        const chart = this.charts.propertyType;
        const data = this.data.propertyTypes;
        
        chart.data.labels = data.map(item => item.type);
        chart.data.datasets[0].data = data.map(item => item.count);
        chart.update();
    }

    updateLocationChart() {
        if (!this.charts.location || !this.data.locationAnalysis) return;

        const chart = this.charts.location;
        const data = this.data.locationAnalysis;
        
        chart.data.labels = data.map(item => item.kecamatan);
        chart.data.datasets[0].data = data.map(item => item.total_properties);
        chart.update();
    }

    updateTrendChart() {
        if (!this.charts.trend || !this.data.trendAnalysis) return;

        const chart = this.charts.trend;
        const data = this.data.trendAnalysis;
        
        // Sort by month
        const sortedData = [...data].sort((a, b) => a.month.localeCompare(b.month));
        
        chart.data.labels = sortedData.map(item => item.month);
        chart.data.datasets[0].data = sortedData.map(item => item.avg_price);
        chart.update();
    }

    updateCertificateChart() {
        if (!this.charts.certificate || !this.data.certificates) return;

        const chart = this.charts.certificate;
        const data = this.data.certificates;
        
        chart.data.labels = data.map(item => item.certificate);
        chart.data.datasets[0].data = data.map(item => item.total_count);
        chart.update();
    }

    updatePricePerSqmChart() {
        if (!this.charts.pricePerSqm || !this.data.priceRanges) return;

        const chart = this.charts.pricePerSqm;
        const data = this.data.priceRanges;
        
        chart.data.labels = data.map(item => item.range);
        chart.data.datasets[0].data = data.map(item => item.count);
        chart.update();
    }

    generateCustomReport() {
        // Implementation for custom report generation
        alert('Fitur generate report akan segera tersedia');
    }

    formatCurrency(amount) {
        if (!amount) return 'Rp 0';
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatNumber(num) {
        if (!num) return '0';
        return new Intl.NumberFormat('id-ID').format(num);
    }

    showError(message) {
        console.error(message);
        this.showNotification('Error: ' + message, 'danger');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    verifyChartsLoaded() {
        const requiredCharts = ['main', 'propertyType', 'location', 'trend', 'certificate', 'pricePerSqm'];
        const loadedCharts = Object.keys(this.charts);
        
        const missingCharts = requiredCharts.filter(chart => !loadedCharts.includes(chart));
        
        if (missingCharts.length > 0) {
            console.warn('Missing charts:', missingCharts);
            return false;
        }
        
        return true;
    }

    // Method to handle chart resize
    handleChartResize() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }

    // Cleanup method
    destroy() {
        this.stopAutoRefresh();
        
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.data = {};
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the visualization section
    if (document.getElementById('mainChart')) {
        console.log('Initializing Visualization Dashboard...');
        
        // Wait a bit for all elements to be ready
        setTimeout(() => {
            window.visualizationDashboard = new VisualizationDashboard();
            
            // Add global refresh function
            window.refreshVisualizationData = () => {
                if (window.visualizationDashboard) {
                    window.visualizationDashboard.loadAllData();
                }
            };
            
            console.log('Visualization Dashboard initialized successfully');
        }, 100);
    }
});

// Export for global access
window.VisualizationDashboard = VisualizationDashboard;
