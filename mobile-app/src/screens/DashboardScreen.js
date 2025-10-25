import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
  Alert,
} from 'react-native';
import { useQuery } from 'react-query';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

const { width } = Dimensions.get('window');

const DashboardScreen = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');

  // Fetch dashboard data
  const { data: dashboardData, isLoading, refetch } = useQuery(
    ['dashboard', selectedPeriod],
    async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return {
        totalCost: 12000,
        monthlyCost: 12000,
        dailyCost: 400,
        savings: 2400,
        alerts: 3,
        optimizationScore: 85,
        costTrend: 5.2,
        forecast: 13000,
        services: [
          { name: 'EC2', cost: 5400, percentage: 45, color: '#3b82f6' },
          { name: 'RDS', cost: 3000, percentage: 25, color: '#10b981' },
          { name: 'S3', cost: 1800, percentage: 15, color: '#f59e0b' },
          { name: 'Lambda', cost: 1200, percentage: 10, color: '#ef4444' },
          { name: 'Other', cost: 600, percentage: 5, color: '#8b5cf6' },
        ],
        costHistory: [
          { date: '2025-01-01', cost: 1200 },
          { date: '2025-01-02', cost: 1350 },
          { date: '2025-01-03', cost: 1100 },
          { date: '2025-01-04', cost: 1450 },
          { date: '2025-01-05', cost: 1300 },
          { date: '2025-01-06', cost: 1600 },
          { date: '2025-01-07', cost: 1400 },
        ],
      };
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleOptimizationPress = () => {
    navigation.navigate('Optimization');
  };

  const handleAlertsPress = () => {
    navigation.navigate('Alerts');
  };

  const handleAnalyticsPress = () => {
    navigation.navigate('Analytics');
  };

  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#3b82f6',
    },
  };

  const pieData = dashboardData?.services.map((service, index) => ({
    name: service.name,
    population: service.cost,
    color: service.color,
    legendFontColor: '#7F7F7F',
    legendFontSize: 12,
  })) || [];

  const lineData = {
    labels: dashboardData?.costHistory.map(item => 
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ) || [],
    datasets: [
      {
        data: dashboardData?.costHistory.map(item => item.cost) || [],
        strokeWidth: 2,
      },
    ],
  };

  if (isLoading && !dashboardData) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <LinearGradient
        colors={['#3b82f6', '#1d4ed8']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Dashboard</Text>
          <Text style={styles.headerSubtitle}>AWS Cost Overview</Text>
        </View>
      </LinearGradient>

      {/* Period Selector */}
      <View style={styles.periodSelector}>
        {['7d', '30d', '90d'].map((period) => (
          <TouchableOpacity
            key={period}
            style={[
              styles.periodButton,
              selectedPeriod === period && styles.periodButtonActive,
            ]}
            onPress={() => setSelectedPeriod(period)}
          >
            <Text
              style={[
                styles.periodButtonText,
                selectedPeriod === period && styles.periodButtonTextActive,
              ]}
            >
              {period}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Metrics Cards */}
      <View style={styles.metricsContainer}>
        <View style={styles.metricCard}>
          <View style={styles.metricHeader}>
            <Icon name="attach-money" size={24} color="#3b82f6" />
            <Text style={styles.metricLabel}>Total Cost</Text>
          </View>
          <Text style={styles.metricValue}>
            ${dashboardData?.totalCost?.toLocaleString() || '0'}
          </Text>
          <Text style={styles.metricChange}>
            +{dashboardData?.costTrend || 0}% vs last month
          </Text>
        </View>

        <View style={styles.metricCard}>
          <View style={styles.metricHeader}>
            <Icon name="trending-down" size={24} color="#10b981" />
            <Text style={styles.metricLabel}>Savings</Text>
          </View>
          <Text style={styles.metricValue}>
            ${dashboardData?.savings?.toLocaleString() || '0'}
          </Text>
          <Text style={styles.metricChange}>+12.1% this month</Text>
        </View>
      </View>

      {/* Cost Trend Chart */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Cost Trend</Text>
        <LineChart
          data={lineData}
          width={width - 40}
          height={220}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Service Breakdown */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Service Breakdown</Text>
        <PieChart
          data={pieData}
          width={width - 40}
          height={220}
          chartConfig={chartConfig}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
          style={styles.chart}
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.actionsTitle}>Quick Actions</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleOptimizationPress}
          >
            <Icon name="trending-up" size={24} color="#3b82f6" />
            <Text style={styles.actionButtonText}>Optimization</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleAlertsPress}
          >
            <Icon name="notifications" size={24} color="#ef4444" />
            <Text style={styles.actionButtonText}>Alerts ({dashboardData?.alerts || 0})</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleAnalyticsPress}
          >
            <Icon name="analytics" size={24} color="#10b981" />
            <Text style={styles.actionButtonText}>Analytics</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('CostDetails')}
          >
            <Icon name="receipt" size={24} color="#f59e0b" />
            <Text style={styles.actionButtonText}>Details</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingText: {
    fontSize: 16,
    color: '#6b7280',
  },
  header: {
    paddingTop: 20,
    paddingBottom: 30,
    paddingHorizontal: 20,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  periodSelector: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginTop: -15,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  periodButtonActive: {
    backgroundColor: '#3b82f6',
  },
  periodButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
  },
  periodButtonTextActive: {
    color: '#ffffff',
  },
  metricsContainer: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginTop: 20,
    gap: 10,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 8,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  metricChange: {
    fontSize: 12,
    color: '#10b981',
  },
  chartContainer: {
    backgroundColor: '#ffffff',
    marginHorizontal: 20,
    marginTop: 20,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  chart: {
    borderRadius: 16,
  },
  actionsContainer: {
    marginHorizontal: 20,
    marginTop: 20,
    marginBottom: 30,
  },
  actionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionButtonText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#1f2937',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default DashboardScreen;
