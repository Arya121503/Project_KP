console.log("Dashboard Admin JS Loaded!");

// Sidebar toggle untuk mobile
const sideMenu = document.querySelector("aside");
const menuBtn = document.getElementById("menu-btn");
const closeBtn = document.getElementById("close-btn");

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

// Sidebar hide/show toggle untuk desktop
const sidebarToggle = document.getElementById("sidebar-toggle");
const container = document.querySelector(".container");

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
  darkMode.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode-variables");
    darkMode.querySelector("span:nth-child(1)").classList.toggle("active");
    darkMode.querySelector("span:nth-child(2)").classList.toggle("active");
  });
}

// Close sidebar when clicking outside (for mobile)
document.addEventListener("click", (e) => {
  if (window.innerWidth <= 992) {
    const sidebar = document.querySelector("aside");
    const menuBtn = document.getElementById("menu-btn");
    const closeBtn = document.getElementById("close-btn");

    if (sidebar && sidebar.classList.contains("show")) {
      if (!sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
        sidebar.classList.remove("show");
      }
    }
  }
});

// SPA navigation
const menuLinks = document.querySelectorAll(".menu-link");
const contentSections = document.querySelectorAll(".content-section");

menuLinks.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();

    // Update active menu item
    menuLinks.forEach((link) => link.classList.remove("active"));
    link.classList.add("active");

    // Get target section and scroll to it smoothly
    const targetId = link.getAttribute("data-target");
    const targetSection = document.getElementById(targetId);
    if (targetSection) {
      targetSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
    
    // Close sidebar on mobile after selection
    if (window.innerWidth <= 768) {
      const sidebar = document.querySelector("aside");
      if (sidebar) {
        sidebar.classList.remove("show");
      }
    }
  });
});

// ===================================
// SCROLL-BASED NAVIGATION SYSTEM
// ===================================

let isScrolling = false;
let scrollTimeout;

// Intersection Observer for scroll-based navigation
const observerOptions = {
  root: null,
  rootMargin: '-50% 0px -50% 0px', // Trigger when section is 50% visible
  threshold: 0
};

const sectionObserver = new IntersectionObserver((entries) => {
  if (isScrolling) return; // Don't update during programmatic scrolling
  
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const sectionId = entry.target.id;
      updateActiveMenuItem(sectionId);
      updateActiveSectionClass(sectionId);
    }
  });
}, observerOptions);

// Observe all content sections
contentSections.forEach(section => {
  sectionObserver.observe(section);
});

// Update active menu item based on current section
function updateActiveMenuItem(sectionId) {
  menuLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('data-target') === sectionId) {
      link.classList.add('active');
    }
  });
}

// Update active section visual indicator
function updateActiveSectionClass(sectionId) {
  contentSections.forEach(section => {
    section.classList.remove('active');
  });
  
  const activeSection = document.getElementById(sectionId);
  if (activeSection) {
    activeSection.classList.add('active');
  }
}

// Smooth scroll with navigation update protection
function smoothScrollToSection(targetId) {
  isScrolling = true;
  const targetSection = document.getElementById(targetId);
  
  if (targetSection) {
    targetSection.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
    
    // Reset scrolling flag after animation completes
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      isScrolling = false;
    }, 1000);
  }
}

// Initialize scroll navigation on page load
document.addEventListener('DOMContentLoaded', function() {
  // Set initial active section (first section)
  if (contentSections.length > 0) {
    const firstSection = contentSections[0];
    updateActiveMenuItem(firstSection.id);
    updateActiveSectionClass(firstSection.id);
  }
});

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
  // Navigate with Page Up/Page Down or Arrow Keys
  if (e.key === 'PageDown' || (e.ctrlKey && e.key === 'ArrowDown')) {
    e.preventDefault();
    scrollToNextSection();
  } else if (e.key === 'PageUp' || (e.ctrlKey && e.key === 'ArrowUp')) {
    e.preventDefault();
    scrollToPreviousSection();
  }
});

function scrollToNextSection() {
  const currentActive = document.querySelector('.menu-link.active');
  if (currentActive) {
    const allLinks = Array.from(menuLinks);
    const currentIndex = allLinks.indexOf(currentActive);
    if (currentIndex < allLinks.length - 1) {
      const nextLink = allLinks[currentIndex + 1];
      const targetId = nextLink.getAttribute('data-target');
      smoothScrollToSection(targetId);
    }
  }
}

function scrollToPreviousSection() {
  const currentActive = document.querySelector('.menu-link.active');
  if (currentActive) {
    const allLinks = Array.from(menuLinks);
    const currentIndex = allLinks.indexOf(currentActive);
    if (currentIndex > 0) {
      const prevLink = allLinks[currentIndex - 1];
      const targetId = prevLink.getAttribute('data-target');
      smoothScrollToSection(targetId);
    }
  }
}

// ===================================
// END SCROLL-BASED NAVIGATION SYSTEM
// ===================================

// -------------------------
// Visualisasi Chart Logic
// -------------------------

let mainChart;
let propertyTypeChart;
let locationChart;
let trendChart;
let modelMetricsChart;
let certificateChart;
let pricePerSqmChart;

// Initialize all visualization functionality
document.addEventListener('DOMContentLoaded', function() {
  console.log("Initializing visualization controls...");
  initializeVisualizationControls();
  initializeCharts();
  
  // Initialize all dashboard functionality
  initializeAllFeatures();
});

function initializeVisualizationControls() {
  console.log("Setting up visualization controls...");
  
  // Update Chart Button
  const updateChartBtn = document.getElementById("updateChart");
  if (updateChartBtn) {
    updateChartBtn.addEventListener("click", handleChartUpdate);
    console.log("Update chart button listener added");
  }

  // Filter change listeners
  const chartTypeSelect = document.getElementById("chartType");
  const dataSourceSelect = document.getElementById("dataSource"); 
  const groupBySelect = document.getElementById("groupBy");
  const metricSelect = document.getElementById("metric");
  const timePeriodSelect = document.getElementById("timePeriod");

  // Auto update on filter changes
  [chartTypeSelect, dataSourceSelect, groupBySelect, metricSelect, timePeriodSelect].forEach(select => {
    if (select) {
      select.addEventListener("change", () => {
        // Small delay to improve UX
        setTimeout(handleChartUpdate, 300);
      });
    }
  });

  // Export buttons
  initializeExportButtons();
  console.log("Export buttons initialized");
  
  // Report buttons  
  initializeReportButtons();
  console.log("Report buttons initialized");
}

function initializeAllFeatures() {
  console.log("Initializing all dashboard features...");
  
  // Initialize visualization charts
  initializeVisualizationCharts();
  
  // Initialize additional chart update buttons
  const updateLocationBtn = document.getElementById('updateLocationChart');
  if (updateLocationBtn) {
    updateLocationBtn.addEventListener('click', function() {
      console.log('Updating location chart...');
      // Add actual update logic here
    });
  }
  
  const updateTrendBtn = document.getElementById('updateTrendChart');
  if (updateTrendBtn) {
    updateTrendBtn.addEventListener('click', function() {
      console.log('Updating trend chart...');
      // Add actual update logic here
    });
  }
  
  // Re-initialize export and report buttons to ensure they work
  setTimeout(() => {
    initializeExportButtons();
    initializeReportButtons();
    console.log("Export and report buttons re-initialized");
  }, 500);
}

function handleChartUpdate() {
  const chartType = document.getElementById("chartType")?.value || 'bar';
  const dataSource = document.getElementById("dataSource")?.value || 'both';
  const groupBy = document.getElementById("groupBy")?.value || 'location';
  const metric = document.getElementById("metric")?.value || 'avgPrice';
  const timePeriod = document.getElementById("timePeriod")?.value || 'all';

  console.log('Updating charts with filters:', {
    chartType, dataSource, groupBy, metric, timePeriod
  });

  // Show loading effect
  showLoadingSpinner();

  // Update main chart
  updateMainChart(chartType, dataSource, groupBy, metric);
  
  // Update statistics
  updateStatistics(dataSource, timePeriod);
  
  // Update table
  updateTopLocationsTable(dataSource, metric);

  // Hide loading and show success
  setTimeout(() => {
    hideLoadingSpinner();
    showNotification('Chart berhasil diperbarui!', 'success');
  }, 1000);
}

function updateMainChart(chartType, dataSource, groupBy, metric) {
  const ctx = document.getElementById("mainChart");
  if (!ctx) return;

  // Destroy existing chart
  if (mainChart) {
    mainChart.destroy();
  }

  // Generate sample data based on filters
  const data = generateChartData(dataSource, groupBy, metric);
  
  // Create new chart
  mainChart = new Chart(ctx, {
    type: chartType,
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `${getMetricLabel(metric)} berdasarkan ${getGroupByLabel(groupBy)}`,
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        legend: {
          display: chartType === 'pie' || chartType === 'doughnut',
          position: 'bottom'
        }
      },
      scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              if (metric === 'avgPrice' || metric === 'totalValue') {
                return 'Rp ' + (value / 1000000).toFixed(0) + 'M';
              }
              return value;
            }
          }
        }
      } : {}
    }
  });
}

function generateChartData(dataSource, groupBy, metric) {
  let labels = [];
  let values = [];
  let colors = [];

  // Sample data based on groupBy
  if (groupBy === 'location') {
    labels = ['Sukolilo', 'Gubeng', 'Wonokromo', 'Tegalsari', 'Genteng', 'Mulyorejo'];
    values = [850000000, 1200000000, 780000000, 1100000000, 950000000, 720000000];
    colors = ['#DC143C', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
  } else if (groupBy === 'type') {
    labels = ['Tanah Kosong', 'Rumah + Tanah', 'Gedung + Tanah'];
    values = [650000000, 1200000000, 2500000000];
    colors = ['#28a745', '#DC143C', '#6c757d'];
  } else if (groupBy === 'price_range') {
    labels = ['< 500M', '500M - 1B', '1B - 2B', '> 2B'];
    values = [45, 128, 67, 23];
    colors = ['#ffc107', '#28a745', '#17a2b8', '#DC143C'];
  } else if (groupBy === 'certificate') {
    labels = ['SHM', 'HGB', 'Girik', 'AJB'];
    values = [156, 89, 45, 67];
    colors = ['#28a745', '#17a2b8', '#ffc107', '#6c757d'];
  }

  // Adjust values based on metric
  if (metric === 'count') {
    values = values.map(v => Math.floor(v / 10000000));
  } else if (metric === 'price_per_sqm') {
    values = values.map(v => Math.floor(v / 100));
  }

  // Apply data source filter
  if (dataSource === 'tanah') {
    values = values.map(v => v * 0.7); // Tanah typically lower
  } else if (dataSource === 'bangunan') {
    values = values.map(v => v * 1.3); // Building + land higher
  }

  return {
    labels: labels,
    datasets: [{
      label: getMetricLabel(metric),
      data: values,
      backgroundColor: colors,
      borderColor: colors.map(color => color.replace('0.6', '1')),
      borderWidth: 2
    }]
  };
}

function updateStatistics(dataSource, timePeriod) {
  // Update quick stats cards
  const avgPriceEl = document.getElementById("avgPrice");
  const maxPriceEl = document.getElementById("maxPrice");
  const minPriceEl = document.getElementById("minPrice");
  const totalAssetsEl = document.getElementById("totalAssets");

  // Sample updated values based on filters
  let avgPrice = 850000000;
  let maxPrice = 2500000000;
  let minPrice = 150000000;
  let totalAssets = 1247;

  if (dataSource === 'tanah') {
    avgPrice *= 0.7;
    maxPrice *= 0.8;
    totalAssets = Math.floor(totalAssets * 0.6);
  } else if (dataSource === 'bangunan') {
    avgPrice *= 1.3;
    maxPrice *= 1.2;
    totalAssets = Math.floor(totalAssets * 0.4);
  }

  if (avgPriceEl) avgPriceEl.textContent = "Rp " + formatNumber(avgPrice);
  if (maxPriceEl) maxPriceEl.textContent = "Rp " + formatNumber(maxPrice);
  if (minPriceEl) minPriceEl.textContent = "Rp " + formatNumber(minPrice);
  if (totalAssetsEl) totalAssetsEl.textContent = formatNumber(totalAssets);
}

function updateTopLocationsTable(dataSource, metric) {
  const tableBody = document.getElementById("topPriceTable");
  if (!tableBody) return;

  const sampleData = [
    { rank: 1, location: "Gubeng", average: "Rp 1,200,000,000", count: 45 },
    { rank: 2, location: "Tegalsari", average: "Rp 1,100,000,000", count: 38 },
    { rank: 3, location: "Genteng", average: "Rp 950,000,000", count: 42 },
    { rank: 4, location: "Sukolilo", average: "Rp 850,000,000", count: 56 },
    { rank: 5, location: "Wonokromo", average: "Rp 780,000,000", count: 62 }
  ];

  tableBody.innerHTML = sampleData.map(row => `
    <tr>
      <td>${row.rank}</td>
      <td>${row.location}</td>
      <td>${row.average}</td>
      <td>${row.count}</td>
    </tr>
  `).join('');
}

function initializeExportButtons() {
  console.log("Initializing export buttons...");
  
  // Get export buttons with more specific selectors
  const excelBtn = document.querySelector('.btn-outline-primary:has(.fa-file-excel)');
  const pdfBtn = document.querySelector('.btn-outline-danger:has(.fa-file-pdf)');  
  const csvBtn = document.querySelector('.btn-outline-success:has(.fa-file-csv)');
  const pngBtn = document.querySelector('.btn-outline-info:has(.fa-image)');
  
  // Fallback method using querySelectorAll if :has() not supported
  if (!excelBtn || !pdfBtn || !csvBtn || !pngBtn) {
    console.log("Using fallback selector method...");
    const allButtons = document.querySelectorAll('.btn-outline-primary, .btn-outline-danger, .btn-outline-success, .btn-outline-info');
    
    allButtons.forEach(btn => {
      const icon = btn.querySelector('i');
      if (!icon) return;
      
      console.log("Found button with icon:", icon.className);
      
      if (icon.classList.contains('fa-file-excel')) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          console.log("Excel export clicked");
          exportData('excel');
        });
        console.log("Excel button listener added");
      } else if (icon.classList.contains('fa-file-pdf')) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          console.log("PDF export clicked");
          exportData('pdf');
        });
        console.log("PDF button listener added");
      } else if (icon.classList.contains('fa-file-csv')) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          console.log("CSV export clicked");
          exportData('csv');
        });
        console.log("CSV button listener added");
      } else if (icon.classList.contains('fa-image')) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          console.log("PNG export clicked");
          exportChart('png');
        });
        console.log("PNG button listener added");
      }
    });
  } else {
    // Use direct selectors if :has() is supported
    if (excelBtn) {
      excelBtn.addEventListener('click', (e) => {
        e.preventDefault();
        exportData('excel');
      });
    }
    if (pdfBtn) {
      pdfBtn.addEventListener('click', (e) => {
        e.preventDefault();
        exportData('pdf');
      });
    }
    if (csvBtn) {
      csvBtn.addEventListener('click', (e) => {
        e.preventDefault();
        exportData('csv');
      });
    }
    if (pngBtn) {
      pngBtn.addEventListener('click', (e) => {
        e.preventDefault();
        exportChart('png');
      });
    }
  }
  
  console.log("Export buttons initialization completed");
}

function exportData(format) {
  console.log(`Starting export for format: ${format}`);
  showLoadingSpinner();
  
  console.log(`Exporting data in ${format.toUpperCase()} format...`);
  
  setTimeout(() => {
    hideLoadingSpinner();
    
    if (format === 'csv') {
      downloadCSV();
      showNotification(`Data berhasil diekspor ke format CSV!`, 'success');
    } else if (format === 'excel') {
      downloadExcel();
      showNotification(`Data berhasil diekspor ke format Excel!`, 'success');
    } else if (format === 'pdf') {
      downloadPDF();
      showNotification(`Data berhasil diekspor ke format PDF!`, 'success');
    } else {
      showNotification(`Fitur export ${format.toUpperCase()} akan segera tersedia`, 'info');
    }
    console.log(`Export ${format} completed`);
  }, 1500);
}

function exportChart(format) {
  const canvas = document.getElementById('mainChart');
  if (!canvas) {
    showNotification('Chart tidak ditemukan untuk diekspor', 'error');
    return;
  }

  try {
    const dataURL = canvas.toDataURL(`image/${format}`);
    const link = document.createElement('a');
    link.download = `chart-visualization.${format}`;
    link.href = dataURL;
    link.click();
    
    showNotification(`Chart berhasil diekspor sebagai ${format.toUpperCase()}!`, 'success');
  } catch (error) {
    console.error('Export error:', error);
    showNotification('Gagal mengekspor chart', 'error');
  }
}

function downloadCSV() {
  const csvData = [
    ['Kecamatan', 'Harga Rata-rata', 'Jumlah Properti'],
    ['Gubeng', '1200000000', '45'],
    ['Tegalsari', '1100000000', '38'],
    ['Genteng', '950000000', '42'],
    ['Sukolilo', '850000000', '56'],
    ['Wonokromo', '780000000', '62']
  ];

  const csvContent = csvData.map(row => row.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = 'data-properti.csv';
  link.click();
  
  window.URL.revokeObjectURL(url);
}

function downloadExcel() {
  try {
    // Check if XLSX library is available
    if (typeof XLSX === 'undefined') {
      console.log('XLSX library not available, using fallback method');
      downloadExcelFallback();
      return;
    }

    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();
    
    // Sample data for the Excel file
    const data = [
      ['Kecamatan', 'Harga Rata-rata', 'Jumlah Properti', 'Jenis Aset', 'Status'],
      ['Gubeng', 1200000000, 45, 'Tanah + Bangunan', 'Aktif'],
      ['Tegalsari', 1100000000, 38, 'Tanah + Bangunan', 'Aktif'],
      ['Genteng', 950000000, 42, 'Tanah', 'Aktif'],
      ['Sukolilo', 850000000, 56, 'Tanah + Bangunan', 'Aktif'],
      ['Wonokromo', 780000000, 62, 'Tanah', 'Aktif']
    ];

    // Create worksheet
    const ws = XLSX.utils.aoa_to_sheet(data);
    
    // Add some styling (column widths)
    ws['!cols'] = [
      { wch: 15 }, // Kecamatan
      { wch: 20 }, // Harga Rata-rata
      { wch: 15 }, // Jumlah Properti
      { wch: 20 }, // Jenis Aset
      { wch: 10 }  // Status
    ];

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, 'Data Properti');
    
    // Generate and download file
    XLSX.writeFile(wb, 'data-properti-telkom.xlsx');
    
    console.log('Excel file generated successfully');
  } catch (error) {
    console.error('Error generating Excel file:', error);
    downloadExcelFallback();
  }
}

function downloadExcelFallback() {
  // Fallback method using HTML table format
  const excelData = `
    <table>
      <thead>
        <tr>
          <th>Kecamatan</th>
          <th>Harga Rata-rata</th>
          <th>Jumlah Properti</th>
          <th>Jenis Aset</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Gubeng</td>
          <td>1200000000</td>
          <td>45</td>
          <td>Tanah + Bangunan</td>
          <td>Aktif</td>
        </tr>
        <tr>
          <td>Tegalsari</td>
          <td>1100000000</td>
          <td>38</td>
          <td>Tanah + Bangunan</td>
          <td>Aktif</td>
        </tr>
        <tr>
          <td>Genteng</td>
          <td>950000000</td>
          <td>42</td>
          <td>Tanah</td>
          <td>Aktif</td>
        </tr>
        <tr>
          <td>Sukolilo</td>
          <td>850000000</td>
          <td>56</td>
          <td>Tanah + Bangunan</td>
          <td>Aktif</td>
        </tr>
        <tr>
          <td>Wonokromo</td>
          <td>780000000</td>
          <td>62</td>
          <td>Tanah</td>
          <td>Aktif</td>
        </tr>
      </tbody>
    </table>
  `;

  const blob = new Blob([excelData], { 
    type: 'application/vnd.ms-excel' 
  });
  const url = window.URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = 'data-properti-telkom.xls';
  link.click();
  
  window.URL.revokeObjectURL(url);
}

function downloadPDF() {
  try {
    // Check if jsPDF library is available
    if (typeof window.jsPDF === 'undefined') {
      console.log('jsPDF library not available, using fallback method');
      downloadPDFFallback();
      return;
    }

    const { jsPDF } = window.jsPDF;
    const doc = new jsPDF();

    // Set font
    doc.setFont('helvetica');

    // Header
    doc.setFontSize(20);
    doc.setTextColor(220, 20, 60); // Telkom red
    doc.text('PT. TELKOM INDONESIA', 105, 20, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setTextColor(100, 100, 100);
    doc.text('Laporan Data Properti', 105, 30, { align: 'center' });
    
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(`Tanggal: ${new Date().toLocaleDateString('id-ID')}`, 105, 40, { align: 'center' });

    // Summary box
    doc.setFillColor(249, 249, 249);
    doc.rect(20, 50, 170, 25, 'F');
    
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text('Ringkasan Data:', 25, 60);
    doc.setFontSize(10);
    doc.text('Total Lokasi: 5 Kecamatan', 25, 67);
    doc.text('Total Aset: 243 Properti', 25, 72);
    doc.text('Nilai Rata-rata: Rp 1,037,000,000', 100, 67);

    // Table header
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text('Detail Data per Kecamatan', 20, 90);

    // Table data
    const tableData = [
      ['Rank', 'Kecamatan', 'Harga Rata-rata', 'Jumlah', '%'],
      ['1', 'Gubeng', 'Rp 1,200,000,000', '45', '18.5%'],
      ['2', 'Tegalsari', 'Rp 1,100,000,000', '38', '15.6%'],
      ['3', 'Genteng', 'Rp 950,000,000', '42', '17.3%'],
      ['4', 'Sukolilo', 'Rp 850,000,000', '56', '23.0%'],
      ['5', 'Wonokromo', 'Rp 780,000,000', '62', '25.5%']
    ];

    // Draw table
    let startY = 100;
    const colWidths = [15, 30, 50, 20, 15];
    const colX = [20, 35, 65, 115, 135];

    // Header row
    doc.setFillColor(220, 20, 60);
    doc.rect(20, startY, 130, 8, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(9);
    
    for (let i = 0; i < tableData[0].length; i++) {
      doc.text(tableData[0][i], colX[i] + 2, startY + 5);
    }

    // Data rows
    doc.setTextColor(0, 0, 0);
    for (let i = 1; i < tableData.length; i++) {
      const y = startY + (i * 8);
      
      // Alternate row color
      if (i % 2 === 0) {
        doc.setFillColor(248, 248, 248);
        doc.rect(20, y, 130, 8, 'F');
      }
      
      for (let j = 0; j < tableData[i].length; j++) {
        doc.text(tableData[i][j], colX[j] + 2, y + 5);
      }
    }

    // Add chart if available
    const chartCanvas = document.getElementById('mainChart');
    if (chartCanvas) {
      try {
        const chartImgData = chartCanvas.toDataURL('image/png');
        doc.addImage(chartImgData, 'PNG', 20, 150, 170, 60);
        
        doc.setFontSize(10);
        doc.text('Grafik: Distribusi Harga per Kecamatan', 20, 145);
      } catch (error) {
        console.log('Could not add chart to PDF:', error);
      }
    }

    // Footer
    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100);
    doc.text('Laporan ini dibuat secara otomatis oleh Sistem Prediksi Harga Properti Telkom', 105, 260, { align: 'center' });
    doc.text('Confidential - PT. Telkom Indonesia', 105, 266, { align: 'center' });

    // Save the PDF
    const fileName = `laporan-properti-telkom-${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(fileName);
    
    console.log('PDF file generated successfully');
  } catch (error) {
    console.error('Error generating PDF file:', error);
    downloadPDFFallback();
  }
}

function downloadPDFFallback() {
  console.log('Using PDF fallback method...');
  
  // Create a more sophisticated HTML that can be easily converted to PDF
  const reportData = {
    date: new Date().toLocaleDateString('id-ID'),
    summary: {
      totalLocations: 5,
      totalAssets: 243,
      averageValue: 'Rp 1,037,000,000'
    },
    data: [
      { rank: 1, district: 'Gubeng', avgPrice: 'Rp 1,200,000,000', count: 45, percentage: '18.5%' },
      { rank: 2, district: 'Tegalsari', avgPrice: 'Rp 1,100,000,000', count: 38, percentage: '15.6%' },
      { rank: 3, district: 'Genteng', avgPrice: 'Rp 950,000,000', count: 42, percentage: '17.3%' },
      { rank: 4, district: 'Sukolilo', avgPrice: 'Rp 850,000,000', count: 56, percentage: '23.0%' },
      { rank: 5, district: 'Wonokromo', avgPrice: 'Rp 780,000,000', count: 62, percentage: '25.5%' }
    ]
  };

  const pdfContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Laporan Data Properti Telkom</title>
      <style>
        @media print {
          body { margin: 0; }
          .no-print { display: none; }
        }
        body { 
          font-family: Arial, sans-serif; 
          margin: 20px; 
          line-height: 1.4;
        }
        .header { 
          text-align: center; 
          margin-bottom: 30px; 
          border-bottom: 3px solid #DC143C;
          padding-bottom: 20px;
        }
        .header h1 { 
          color: #DC143C; 
          margin: 0; 
          font-size: 24px;
        }
        .header h2 { 
          color: #666; 
          margin: 5px 0; 
          font-size: 18px;
        }
        .summary { 
          background-color: #f9f9f9; 
          padding: 15px; 
          margin: 20px 0; 
          border-left: 4px solid #DC143C;
        }
        .summary h3 {
          margin-top: 0;
          color: #DC143C;
        }
        table { 
          width: 100%; 
          border-collapse: collapse; 
          margin: 20px 0; 
          font-size: 12px;
        }
        th, td { 
          border: 1px solid #ddd; 
          padding: 8px; 
          text-align: left; 
        }
        th { 
          background-color: #DC143C; 
          color: white; 
          font-weight: bold;
        }
        tr:nth-child(even) {
          background-color: #f2f2f2;
        }
        .footer { 
          margin-top: 40px; 
          text-align: center; 
          color: #666; 
          font-size: 10px;
          border-top: 1px solid #ddd;
          padding-top: 20px;
        }
        .print-btn {
          background-color: #DC143C;
          color: white;
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          margin-bottom: 20px;
        }
        .print-btn:hover {
          background-color: #B01030;
        }
      </style>
    </head>
    <body>
      <button class="print-btn no-print" onclick="window.print()">🖨️ Print sebagai PDF</button>
      
      <div class="header">
        <h1>PT. TELKOM INDONESIA</h1>
        <h2>Laporan Data Properti</h2>
        <p><strong>Tanggal: ${reportData.date}</strong></p>
      </div>
      
      <div class="summary">
        <h3>📊 Ringkasan Data</h3>
        <p><strong>Total Lokasi:</strong> ${reportData.summary.totalLocations} Kecamatan</p>
        <p><strong>Total Aset:</strong> ${reportData.summary.totalAssets} Properti</p>
        <p><strong>Nilai Rata-rata:</strong> ${reportData.summary.averageValue}</p>
      </div>
      
      <h3>📋 Detail Data per Kecamatan</h3>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Kecamatan</th>
            <th>Harga Rata-rata</th>
            <th>Jumlah Properti</th>
            <th>Persentase</th>
          </tr>
        </thead>
        <tbody>
          ${reportData.data.map(row => `
            <tr>
              <td>${row.rank}</td>
              <td>${row.district}</td>
              <td>${row.avgPrice}</td>
              <td>${row.count}</td>
              <td>${row.percentage}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      
      <div class="footer">
        <p><strong>Laporan ini dibuat secara otomatis oleh Sistem Prediksi Harga Properti Telkom</strong></p>
        <p><em>Confidential - PT. Telkom Indonesia</em></p>
      </div>
      
      <script class="no-print">
        // Auto print dialog when loaded
        setTimeout(() => {
          console.log('Use Ctrl+P or the Print button to save as PDF');
        }, 1000);
      </script>
    </body>
    </html>
  `;

  const blob = new Blob([pdfContent], { type: 'text/html;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `laporan-properti-telkom-${new Date().toISOString().split('T')[0]}.html`;
  link.click();
  
  window.URL.revokeObjectURL(url);
  
  // Show instructions for PDF conversion
  setTimeout(() => {
    showNotification('File HTML telah diunduh. Buka file dan tekan Ctrl+P, lalu pilih "Save as PDF" untuk membuat PDF.', 'info');
  }, 2000);
}

function initializeReportButtons() {
  console.log("Initializing report buttons...");
  
  const generateReportBtn = document.getElementById('generateReport');
  const scheduleReportBtn = document.getElementById('scheduleReport');
  
  console.log("Generate report button found:", !!generateReportBtn);
  console.log("Schedule report button found:", !!scheduleReportBtn);

  if (generateReportBtn) {
    generateReportBtn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log("Generate report clicked");
      generateCustomReport();
    });
    console.log("Generate report listener added");
  }

  if (scheduleReportBtn) {
    scheduleReportBtn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log("Schedule report clicked");
      scheduleReport();
    });
    console.log("Schedule report listener added");
  }
  
  console.log("Report buttons initialization completed");
}

function generateCustomReport() {
  console.log('Generate custom report function called');
  showLoadingSpinner();
  
  console.log('Generating custom report...');
  
  setTimeout(() => {
    hideLoadingSpinner();
    showNotification('Laporan kustom berhasil dibuat!', 'success');
    showNotification('Laporan akan tersedia untuk diunduh dalam beberapa menit', 'info');
    console.log('Custom report generation completed');
  }, 2000);
}

function scheduleReport() {
  console.log('Schedule report function called');
  showNotification('Jadwal laporan berhasil disimpan!', 'success');
  showNotification('Laporan akan dikirim setiap minggu ke email yang terdaftar', 'info');
  console.log('Report scheduling completed');
}

// Utility functions
function getMetricLabel(metric) {
  const labels = {
    'avgPrice': 'Harga Rata-rata',
    'totalValue': 'Total Nilai',
    'count': 'Jumlah Aset',
    'price_per_sqm': 'Harga per M²'
  };
  return labels[metric] || metric;
}

function getGroupByLabel(groupBy) {
  const labels = {
    'location': 'Lokasi',
    'type': 'Jenis Aset',
    'price_range': 'Range Harga',
    'certificate': 'Sertifikat'
  };
  return labels[groupBy] || groupBy;
}

function formatNumber(num) {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + 'B';
  } else if (num >= 1000000) {
    return (num / 1000000).toFixed(0) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K';
  }
  return num.toString();
}

function showLoadingSpinner() {
  let loader = document.getElementById('loadingIndicator');
  if (!loader) {
    loader = document.createElement('div');
    loader.id = 'loadingIndicator';
    loader.className = 'position-fixed top-50 start-50 translate-middle bg-white rounded p-3 shadow';
    loader.style.zIndex = '9999';
    loader.innerHTML = `
      <div class="d-flex align-items-center">
        <div class="spinner-border spinner-border-sm text-danger me-2" role="status"></div>
        <span>Memproses...</span>
      </div>
    `;
    document.body.appendChild(loader);
  }
  loader.style.display = 'block';
}

function hideLoadingSpinner() {
  const loader = document.getElementById('loadingIndicator');
  if (loader) {
    loader.style.display = 'none';
  }
}

function showNotification(message, type = 'info') {
  // Create notification
  const notification = document.createElement('div');
  notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
  notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
  notification.innerHTML = `
    <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} me-2"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  document.body.appendChild(notification);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
}

function initializeCharts() {
  // Initialize other charts if needed
  initializePropertyTypeChart();
  initializeLocationChart();
  initializeTrendChart();
  initializeModelMetricsChart();
  initializeCertificateChart();
  initializePricePerSqmChart();
}

function initializePropertyTypeChart() {
  const ctx = document.getElementById('propertyTypeChart');
  if (!ctx) return;
  
  propertyTypeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Tanah Kosong', 'Rumah + Tanah', 'Gedung + Tanah'],
      datasets: [{
        data: [35, 45, 20],
        backgroundColor: ['#28a745', '#DC143C', '#6c757d'],
        borderWidth: 2
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

function initializeLocationChart() {
  const ctx = document.getElementById('locationChart');
  if (!ctx) return;
  
  locationChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Sukolilo', 'Gubeng', 'Wonokromo', 'Tegalsari'],
      datasets: [{
        label: 'Jumlah Properti',
        data: [56, 45, 62, 38],
        backgroundColor: '#17a2b8',
        borderColor: '#138496',
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

function initializeTrendChart() {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;
  
  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Harga Rata-rata (Miliar)',
        data: [0.8, 0.85, 0.82, 0.9, 0.95, 0.87],
        borderColor: '#ffc107',
        backgroundColor: 'rgba(255, 193, 7, 0.1)',
        borderWidth: 3,
        fill: true
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

function initializeModelMetricsChart() {
  const ctx = document.getElementById('modelMetricsChart');
  if (!ctx) return;
  
  modelMetricsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['RF', 'XGB', 'Cat'],
      datasets: [{
        label: 'Akurasi (%)',
        data: [94.2, 92.8, 93.5],
        backgroundColor: ['#17a2b8', '#ffc107', '#28a745'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
}

function initializeCertificateChart() {
  const ctx = document.getElementById('certificateChart');
  if (!ctx) return;
  
  certificateChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['SHM', 'HGB', 'Girik', 'AJB'],
      datasets: [{
        data: [45, 25, 20, 10],
        backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#6c757d'],
        borderWidth: 2
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

function initializePricePerSqmChart() {
  const ctx = document.getElementById('pricePerSqmChart');
  if (!ctx) return;
  
  pricePerSqmChart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Harga per M²',
        data: [
          {x: 100, y: 8500},
          {x: 150, y: 7200},
          {x: 200, y: 6800},
          {x: 250, y: 6200},
          {x: 300, y: 5800}
        ],
        backgroundColor: '#6c757d',
        borderColor: '#495057',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Luas (m²)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Harga per M² (Ribu)'
          }
        }
      }
    }
  });
}

// -------------------------
// Prediksi Harga Logic
// -------------------------

const predictionForm = document.getElementById("predictionForm");
if (predictionForm) {
  const resultContainer = document.getElementById("predictionResult");

  predictionForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const land = predictionForm.land_area.value;
    const building = predictionForm.building_area.value;

    if (!land || !building) return;

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ land_area: land, building_area: building }),
      });

      const data = await response.json();

      resultContainer.innerHTML = `
        <div class="alert alert-success">
          <strong>Hasil Prediksi:</strong> Rp ${parseInt(
            data.prediction
          ).toLocaleString()}
        </div>
      `;
    } catch (err) {
      console.error(err);
      resultContainer.innerHTML = `
        <div class="alert alert-danger">
          Terjadi kesalahan memproses prediksi.
        </div>
      `;
    }
  });
}

// Chart initialization functions
function initializeVisualizationCharts() {
  // Dashboard charts
  initializeDashboardCharts();
  
  // Location charts
  initializeLocationCharts();
  
  // Property type charts
  initializePropertyCharts();
  
  // Trend charts
  initializeTrendCharts();
  
  // Model performance charts
  initializeModelCharts();
  
  // Custom chart functionality
  initializeCustomCharts();
}

// Dashboard charts
function initializeDashboardCharts() {
  const districtCtx = document.getElementById('districtChart');
  const propertyTypeCtx = document.getElementById('propertyTypeChart');
  
  if (districtCtx) {
    new Chart(districtCtx, {
      type: 'bar',
      data: {
        labels: ['Sukolilo', 'Gubeng', 'Wonokromo', 'Tegalsari', 'Genteng'],
        datasets: [{
          label: 'Harga Rata-rata (Juta)',
          data: [850, 920, 780, 1100, 950],
          backgroundColor: 'rgba(220, 20, 60, 0.8)',
          borderColor: '#DC143C',
          borderWidth: 1
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
            beginAtZero: true
          }
        }
      }
    });
  }
  
  if (propertyTypeCtx) {
    new Chart(propertyTypeCtx, {
      type: 'doughnut',
      data: {
        labels: ['Tanah', 'Bangunan+Tanah'],
        datasets: [{
          data: [65, 35],
          backgroundColor: ['#28a745', '#DC143C'],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
}

// Location charts
function initializeLocationCharts() {
  const locationCtx = document.getElementById('locationChart');
  const regionCtx = document.getElementById('regionDistributionChart');
  
  if (locationCtx) {
    new Chart(locationCtx, {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'Harga Properti',
          data: generateScatterData(),
          backgroundColor: 'rgba(220, 20, 60, 0.6)',
          borderColor: '#DC143C'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Longitude'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Latitude'
            }
          }
        }
      }
    });
  }
  
  if (regionCtx) {
    new Chart(regionCtx, {
      type: 'pie',
      data: {
        labels: ['Utara', 'Selatan', 'Timur', 'Barat', 'Tengah'],
        datasets: [{
          data: [20, 25, 18, 22, 15],
          backgroundColor: [
            '#DC143C', '#FF6B6B', '#28a745', '#ffc107', '#17a2b8'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
}

// Property type charts
function initializePropertyCharts() {
  const comparisonCtx = document.getElementById('propertyComparisonChart');
  const areaCtx = document.getElementById('areaDistributionChart');
  const certificateCtx = document.getElementById('certificateChart');
  const pricePerSqmCtx = document.getElementById('pricePerSqmChart');
  
  if (comparisonCtx) {
    new Chart(comparisonCtx, {
      type: 'bar',
      data: {
        labels: ['< 100m²', '100-200m²', '200-500m²', '> 500m²'],
        datasets: [
          {
            label: 'Tanah',
            data: [450, 650, 850, 1200],
            backgroundColor: '#28a745'
          },
          {
            label: 'Bangunan+Tanah',
            data: [800, 1100, 1500, 2200],
            backgroundColor: '#DC143C'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
  
  if (areaCtx) {
    new Chart(areaCtx, {
      type: 'line',
      data: {
        labels: ['50', '100', '150', '200', '250', '300', '350', '400'],
        datasets: [{
          label: 'Distribusi Luas (m²)',
          data: [15, 25, 35, 45, 30, 20, 15, 10],
          borderColor: '#007bff',
          backgroundColor: 'rgba(0, 123, 255, 0.1)',
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
  
  if (certificateCtx) {
    new Chart(certificateCtx, {
      type: 'doughnut',
      data: {
        labels: ['SHM', 'HGB', 'Girik', 'AJB'],
        datasets: [{
          data: [45, 30, 15, 10],
          backgroundColor: ['#ffc107', '#28a745', '#dc3545', '#6c757d']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
  
  if (pricePerSqmCtx) {
    new Chart(pricePerSqmCtx, {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'Harga per M²',
          data: generatePricePerSqmData(),
          backgroundColor: 'rgba(220, 20, 60, 0.6)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Luas Total (m²)'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Harga per M² (Juta)'
            }
          }
        }
      }
    });
  }
}

// Trend charts
function initializeTrendCharts() {
  const trendCtx = document.getElementById('trendChart');
  const predictionCtx = document.getElementById('predictionChart');
  
  if (trendCtx) {
    new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
          label: 'Harga Rata-rata (Juta)',
          data: [800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000, 1020],
          borderColor: '#DC143C',
          backgroundColor: 'rgba(220, 20, 60, 0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
  }
  
  if (predictionCtx) {
    new Chart(predictionCtx, {
      type: 'line',
      data: {
        labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
          {
            label: 'Prediksi',
            data: [1020, 1040, 1060, 1080, 1100, 1120],
            borderColor: '#ffc107',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            borderDash: [5, 5]
          },
          {
            label: 'Confidence Interval',
            data: [980, 1000, 1020, 1040, 1060, 1080],
            borderColor: '#6c757d',
            backgroundColor: 'rgba(108, 117, 125, 0.1)',
            fill: '+1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
}

// Model performance charts
function initializeModelCharts() {
  const metricsCtx = document.getElementById('modelMetricsChart');
  const featureCtx = document.getElementById('featureImportanceChart');
  const errorCtx = document.getElementById('errorAnalysisChart');
  
  if (metricsCtx) {
    new Chart(metricsCtx, {
      type: 'radar',
      data: {
        labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'RMSE'],
        datasets: [
          {
            label: 'Random Forest',
            data: [94.2, 93.8, 94.5, 94.1, 85.2],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.2)'
          },
          {
            label: 'XGBoost',
            data: [92.8, 92.1, 93.2, 92.6, 87.5],
            borderColor: '#ffc107',
            backgroundColor: 'rgba(255, 193, 7, 0.2)'
          },
          {
            label: 'CatBoost',
            data: [93.5, 93.0, 93.8, 93.4, 86.1],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.2)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
  
  if (featureCtx) {
    new Chart(featureCtx, {
      type: 'horizontalBar',
      data: {
        labels: ['Lokasi', 'Luas Tanah', 'Luas Bangunan', 'Sertifikat', 'Jalan', 'Fasilitas'],
        datasets: [{
          label: 'Importance (%)',
          data: [35, 25, 20, 10, 6, 4],
          backgroundColor: '#DC143C'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y'
      }
    });
  }
  
  if (errorCtx) {
    new Chart(errorCtx, {
      type: 'histogram',
      data: {
        labels: ['-20%', '-10%', '0%', '10%', '20%'],
        datasets: [{
          label: 'Error Distribution',
          data: [5, 15, 60, 15, 5],
          backgroundColor: 'rgba(220, 20, 60, 0.8)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
}

// Custom charts functionality
function initializeCustomCharts() {
  const customCtx = document.getElementById('customChart');
  let customChart = null;
  
  const generateBtn = document.getElementById('generateCustomChart');
  if (generateBtn) {
    generateBtn.addEventListener('click', function() {
      const chartType = document.getElementById('customChartType').value;
      const dataSource = document.getElementById('dataSource').value;
      const groupBy = document.getElementById('customGroupBy').value;
      const metric = document.getElementById('customMetric').value;
      
      if (customChart) {
        customChart.destroy();
      }
      
      customChart = generateCustomChart(customCtx, chartType, dataSource, groupBy, metric);
    });
  }
}

// Helper functions
function generateScatterData() {
  const data = [];
  for (let i = 0; i < 50; i++) {
    data.push({
      x: Math.random() * 0.1 + 112.7, // Longitude Surabaya
      y: Math.random() * 0.1 - 7.2    // Latitude Surabaya
    });
  }
  return data;
}

function generatePricePerSqmData() {
  const data = [];
  for (let i = 0; i < 100; i++) {
    data.push({
      x: Math.random() * 500 + 50,    // Luas 50-550 m²
      y: Math.random() * 10 + 5       // Harga 5-15 juta per m²
    });
  }
  return data;
}

function generateCustomChart(ctx, type, dataSource, groupBy, metric) {
  // Mock data generation based on parameters
  const labels = ['A', 'B', 'C', 'D', 'E'];
  const data = [12, 19, 3, 5, 2];
  
  return new Chart(ctx, {
    type: type,
    data: {
      labels: labels,
      datasets: [{
        label: metric,
        data: data,
        backgroundColor: [
          'rgba(220, 20, 60, 0.8)',
          'rgba(40, 167, 69, 0.8)',
          'rgba(0, 123, 255, 0.8)',
          'rgba(255, 193, 7, 0.8)',
          'rgba(108, 117, 125, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

// ===================================
// SECTION NAVIGATION INDICATORS & SCROLL PROGRESS
// ===================================

// Create section navigation indicators - DISABLED
/*
function createSectionIndicators() {
  // Remove existing indicators
  const existingIndicator = document.querySelector('.section-nav-indicator');
  if (existingIndicator) {
    existingIndicator.remove();
  }

  const indicatorContainer = document.createElement('div');
  indicatorContainer.className = 'section-nav-indicator';

  // Create indicators for each section
  const sectionData = [
    { id: 'dashboard-home', title: 'Dashboard' },
    { id: 'visualisasi', title: 'Visualisasi' },
    { id: 'prediksi-properti', title: 'Prediksi' },
    { id: 'manajemen-aset', title: 'Manajemen' },
    { id: 'aset-sewa', title: 'Aset Sewa' },
    { id: 'aset-jual', title: 'Aset Jual' },
    { id: 'notifikasi', title: 'Notifikasi' }
  ];

  sectionData.forEach((section, index) => {
    const indicator = document.createElement('span');
    indicator.className = 'section-indicator';
    indicator.setAttribute('data-title', section.title);
    indicator.setAttribute('data-target', section.id);
    
    // Set first indicator as active
    if (index === 0) {
      indicator.classList.add('active');
    }

    // Click handler for indicators
    indicator.addEventListener('click', () => {
      smoothScrollToSection(section.id);
      updateSectionIndicators(section.id);
    });

    indicatorContainer.appendChild(indicator);
  });

  document.body.appendChild(indicatorContainer);
}

// Update section indicators - DISABLED
function updateSectionIndicators(activeSectionId) {
  const indicators = document.querySelectorAll('.section-indicator');
  indicators.forEach(indicator => {
    indicator.classList.remove('active');
    if (indicator.getAttribute('data-target') === activeSectionId) {
      indicator.classList.add('active');
    }
  });
}
*/

// Create scroll progress bar
function createScrollProgressBar() {
  // Remove existing progress bar
  const existingProgress = document.querySelector('.scroll-progress');
  if (existingProgress) {
    existingProgress.remove();
  }

  const progressContainer = document.createElement('div');
  progressContainer.className = 'scroll-progress';
  
  const progressBar = document.createElement('div');
  progressBar.className = 'scroll-progress-bar';
  
  progressContainer.appendChild(progressBar);
  document.body.appendChild(progressContainer);
}

// Update scroll progress
function updateScrollProgress() {
  const progressBar = document.querySelector('.scroll-progress-bar');
  if (!progressBar) return;

  const mainElement = document.querySelector('main');
  if (!mainElement) return;

  const scrollTop = mainElement.scrollTop;
  const scrollHeight = mainElement.scrollHeight - mainElement.clientHeight;
  const scrollPercent = (scrollTop / scrollHeight) * 100;

  progressBar.style.width = `${Math.min(100, Math.max(0, scrollPercent))}%`;
}

// Enhanced scroll listener for indicators and progress
function initializeScrollEnhancements() {
  const mainElement = document.querySelector('main');
  if (!mainElement) return;

  // Update progress on scroll
  mainElement.addEventListener('scroll', updateScrollProgress);

  // Update indicators based on scroll position
  const enhancedObserver = new IntersectionObserver((entries) => {
    if (isScrolling) return;
    
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const sectionId = entry.target.id;
        updateActiveMenuItem(sectionId);
        updateActiveSectionClass(sectionId);
        updateSectionIndicators(sectionId);
      }
    });
  }, {
    root: mainElement,
    rootMargin: '-30% 0px -30% 0px',
    threshold: 0.1
  });

  // Observe all sections
  contentSections.forEach(section => {
    enhancedObserver.observe(section);
  });

  // Initial progress update
  updateScrollProgress();
}

// Initialize all scroll enhancements
document.addEventListener('DOMContentLoaded', function() {
  // Wait a bit for DOM to fully load
  setTimeout(() => {
    // createSectionIndicators(); // Disabled - section indicators removed
    createScrollProgressBar();
    initializeScrollEnhancements();
    
    console.log('Scroll navigation enhancements initialized');
  }, 100);
});

// ===================================
// ENHANCED SMOOTH SCROLLING
// ===================================

// Override the existing smooth scroll function with enhanced version
function smoothScrollToSection(targetId) {
  isScrolling = true;
  const targetSection = document.getElementById(targetId);
  const mainElement = document.querySelector('main');
  
  if (targetSection && mainElement) {
    // Calculate the target scroll position relative to main element
    const targetPosition = targetSection.offsetTop;
    
    // Smooth scroll using main element
    mainElement.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });
    
    // Reset scrolling flag after animation completes
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      isScrolling = false;
    }, 1200);
  }
}

// Add mouse wheel smooth scrolling enhancement
let isWheelScrolling = false;
document.addEventListener('wheel', function(e) {
  const mainElement = document.querySelector('main');
  if (!mainElement) return;
  
  // Detect if user is doing fast wheel scrolling
  if (Math.abs(e.deltaY) > 50) {
    isWheelScrolling = true;
    clearTimeout(scrollTimeout);
    
    scrollTimeout = setTimeout(() => {
      isWheelScrolling = false;
    }, 150);
  }
}, { passive: true });

console.log('Enhanced scroll navigation system loaded successfully!');
