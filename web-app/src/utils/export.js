/**
 * Export utilities for CSV and data exports
 */

// Export data to CSV
export const exportToCSV = (data, filename = 'export.csv') => {
  if (!data || data.length === 0) {
    console.error('No data to export');
    return;
  }

  // Convert array of objects to CSV
  const headers = Object.keys(data[0]);
  const csvRows = [];

  // Add headers
  csvRows.push(headers.join(','));

  // Add data rows
  for (const row of data) {
    const values = headers.map(header => {
      const value = row[header];
      // Escape quotes and wrap in quotes if contains comma, quote, or newline
      if (value == null) return '';
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    });
    csvRows.push(values.join(','));
  }

  // Create CSV content
  const csvContent = csvRows.join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// Export dashboard data
export const exportDashboardData = (dashboardData) => {
  const exportData = [
    { Metric: 'Total Cost', Value: `$${dashboardData.totalCost?.toLocaleString()}` },
    { Metric: 'Monthly Cost', Value: `$${dashboardData.monthlyCost?.toLocaleString()}` },
    { Metric: 'Daily Cost', Value: `$${dashboardData.dailyCost?.toLocaleString()}` },
    { Metric: 'Savings', Value: `$${dashboardData.savings?.toLocaleString()}` },
    { Metric: 'Optimization Score', Value: `${dashboardData.optimizationScore}%` },
    { Metric: 'Forecast', Value: `$${dashboardData.forecast?.toLocaleString()}` },
    { Metric: 'Active Alerts', Value: dashboardData.alerts },
  ];

  // Add top services
  if (dashboardData.topServices) {
    dashboardData.topServices.forEach(service => {
      exportData.push({
        Metric: `Service: ${service.name}`,
        Value: `$${service.cost?.toLocaleString()} (${service.percentage}%)`
      });
    });
  }

  exportToCSV(exportData, `dashboard-export-${new Date().toISOString().split('T')[0]}.csv`);
};

// Export optimizations
export const exportOptimizations = (optimizations) => {
  const exportData = optimizations.map(opt => ({
    ID: opt.id,
    Type: opt.type,
    Service: opt.service,
    Description: opt.description,
    'Potential Savings': `$${opt.potentialSavings.toLocaleString()}`,
    Impact: opt.impact,
    Effort: opt.effort,
    Status: opt.status,
    Priority: opt.priority,
  }));

  exportToCSV(exportData, `optimizations-export-${new Date().toISOString().split('T')[0]}.csv`);
};

// Export alerts
export const exportAlerts = (alerts) => {
  const exportData = alerts.map(alert => ({
    ID: alert.id,
    Type: alert.type,
    Severity: alert.severity,
    Message: alert.message,
    Status: alert.status,
    Service: alert.service,
    Timestamp: alert.timestamp,
  }));

  exportToCSV(exportData, `alerts-export-${new Date().toISOString().split('T')[0]}.csv`);
};

// Export cost trends
export const exportCostTrends = (trends) => {
  exportToCSV(trends, `cost-trends-export-${new Date().toISOString().split('T')[0]}.csv`);
};

// Export service costs
export const exportServiceCosts = (services) => {
  const exportData = services.map(service => ({
    Service: service.name,
    Cost: `$${service.cost.toLocaleString()}`,
    Percentage: `${service.percentage}%`,
    Change: `${service.change > 0 ? '+' : ''}${service.change}%`,
  }));

  exportToCSV(exportData, `service-costs-export-${new Date().toISOString().split('T')[0]}.csv`);
};


