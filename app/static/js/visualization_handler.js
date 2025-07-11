class VisualizationHandler {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEventListeners();
            this.loadData(); // Initial data load
        });
    }

    setupEventListeners() {
        const updateButton = document.getElementById('updateChart');
        if (updateButton) {
            updateButton.addEventListener('click', () => this.loadData());
        }
    }

    async fetchData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'API request failed');
            }
            return result.data;
        } catch (error) {
            console.error('Fetch error:', error);
            this.showError(`Failed to fetch data from ${url}. ${error.message}`);
            throw error;
        }
    }

    async loadData() {
        this.showLoading();
        const dataType = document.getElementById('dataType')?.value || 'prediksi';
        const dataSource = document.getElementById('dataSource')?.value || 'both';
        const groupBy = document.getElementById('groupBy')?.value || 'location';
        const metric = document.getElementById('metric')?.value || 'avgPrice';

        try {
            const statsUrl = `/api/visualization/stats?data_type=${dataType}&data_source=${dataSource}`;
            const locationUrl = `/api/visualization/location-analysis?data_type=${dataType}&data_source=${dataSource}`;
            const mainChartUrl = `/api/visualization/main-chart?data_type=${dataType}&data_source=${dataSource}&group_by=${groupBy}&metric=${metric}`;

            const [stats, locationData, mainChartData] = await Promise.all([
                this.fetchData(statsUrl),
                this.fetchData(locationUrl),
                this.fetchData(mainChartUrl)
            ]);

            this.data.stats = stats;
            this.data.locationAnalysis = locationData;
            this.data.mainChartData = mainChartData;

            this.updateUI();
            this.hideLoading();
            this.showSuccess('Data updated successfully.');

        } catch (error) {
            this.hideLoading();
            // Error is already logged in fetchData
        }
    }

    updateUI() {
        this.updateStatsDisplay();
        this.updateLocationTable();
        this.renderMainChart();
        this.toggleVisualizationDisplay();
    }

    updateStatsDisplay() {
        if (!this.data.stats) return;
        const { avg_price, max_price, min_price, total_assets } = this.data.stats;
        this.updateElement('avgPrice', this.formatCurrency(avg_price));
        this.updateElement('maxPrice', this.formatCurrency(max_price));
        this.updateElement('minPrice', this.formatCurrency(min_price));
        this.updateElement('totalAssets', this.formatNumber(total_assets));
    }

    updateLocationTable() {
        const tableBody = document.getElementById('topPriceTable');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (!this.data.locationAnalysis || this.data.locationAnalysis.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted p-4"><i class="fas fa-info-circle me-2"></i>No data available for the selected filters.</td></tr>`;
            return;
        }

        this.data.locationAnalysis.forEach((item, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="text-center"><strong>${index + 1}</strong></td>
                <td><div class="d-flex align-items-center"><i class="fas fa-map-marker-alt text-danger me-2"></i>${item.kecamatan}</div></td>
                <td class="text-end"><strong class="text-success">${this.formatCurrency(item.avg_price)}</strong></td>
                <td class="text-center"><span class="badge bg-primary">${this.formatNumber(item.total_properties)}</span></td>
            `;
            tableBody.appendChild(row);
        });
    }

    renderMainChart() {
        const ctx = document.getElementById('mainChart')?.getContext('2d');
        if (!ctx || !this.data.mainChartData) return;

        if (this.charts.mainChart) {
            this.charts.mainChart.destroy();
        }

        this.charts.mainChart = new Chart(ctx, {
            type: document.getElementById('chartType')?.value || 'bar',
            data: {
                labels: this.data.mainChartData.labels,
                datasets: this.data.mainChartData.datasets
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
    
    toggleVisualizationDisplay() {
        const chartsContainer = document.getElementById('main-charts-container');
        const messageContainer = document.getElementById('visualization-message');
        if (!chartsContainer || !messageContainer) return;

        const hasData = this.data.stats && this.data.stats.total_assets > 0;
        chartsContainer.style.display = hasData ? 'flex' : 'none';
        messageContainer.style.display = hasData ? 'none' : 'block';
    }

    updateElement(id, value) {
        const el = document.getElementById(id);
        if (el) el.innerHTML = value;
    }

    showLoading() {
        ['avgPrice', 'maxPrice', 'minPrice', 'totalAssets'].forEach(id => this.updateElement(id, '<i class="fas fa-spinner fa-spin"></i>'));
        const tableBody = document.getElementById('topPriceTable');
        if (tableBody) tableBody.innerHTML = `<tr><td colspan="4" class="text-center"><i class="fas fa-spinner fa-spin me-2"></i>Loading...</td></tr>`;
        const status = document.getElementById('dataStatus');
        if (status) {
            status.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>Loading...`;
            status.className = 'badge bg-warning me-2';
        }
    }

    hideLoading() {
        const status = document.getElementById('dataStatus');
        if (status) {
            status.innerHTML = `<i class="fas fa-check-circle me-1"></i>Updated`;
            status.className = 'badge bg-success me-2';
        }
    }

    showSuccess(message) {
        console.log(message);
    }

    showError(message) {
        console.error(message);
        const messageContainer = document.getElementById('visualization-message');
        if (messageContainer) {
            messageContainer.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
            messageContainer.style.display = 'block';
        }
    }

    formatCurrency(amount) {
        if (amount === null || isNaN(amount)) return 'Rp 0';
        return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(amount);
    }

    formatNumber(number) {
        if (number === null || isNaN(number)) return '0';
        return new Intl.NumberFormat('id-ID').format(number);
    }
}

new VisualizationHandler();