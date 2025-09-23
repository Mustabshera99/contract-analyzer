#!/bin/bash

# Contract Risk Analyzer Monitoring Setup Script
# This script sets up and manages monitoring infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "Contract Risk Analyzer Monitoring Setup Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  setup       Set up monitoring infrastructure"
    echo "  start       Start monitoring services"
    echo "  stop        Stop monitoring services"
    echo "  restart     Restart monitoring services"
    echo "  status      Show monitoring status"
    echo "  logs        Show monitoring logs"
    echo "  config      Show monitoring configuration"
    echo "  test        Test monitoring setup"
    echo "  cleanup     Clean up monitoring data"
    echo "  help        Show this help message"
    echo
}

# Function to setup monitoring infrastructure
setup_monitoring() {
    print_status "Setting up monitoring infrastructure..."
    
    # Create monitoring directories
    mkdir -p monitoring/data/prometheus
    mkdir -p monitoring/data/grafana
    mkdir -p monitoring/data/alertmanager
    mkdir -p monitoring/data/jaeger
    
    # Set proper permissions
    chmod 755 monitoring/data/prometheus
    chmod 755 monitoring/data/grafana
    chmod 755 monitoring/data/alertmanager
    chmod 755 monitoring/data/jaeger
    
    # Create Grafana datasource configuration
    print_status "Creating Grafana datasource configuration..."
    cat > monitoring/grafana-datasources.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    editable: true
EOF
    
    # Create Grafana dashboard configuration
    print_status "Creating Grafana dashboard configuration..."
    cat > monitoring/grafana-dashboard.json << EOF
{
  "dashboard": {
    "id": null,
    "title": "Contract Analyzer Dashboard",
    "tags": ["contract-analyzer"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ],
        "yAxes": [
          {
            "label": "Errors/sec"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
EOF
    
    # Create Prometheus configuration
    print_status "Creating Prometheus configuration..."
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "prometheus-alerts.yml"

scrape_configs:
  - job_name: 'contract-analyzer'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
    
  - job_name: 'chroma'
    static_configs:
      - targets: ['chroma:8000']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF
    
    # Create Prometheus alerts configuration
    print_status "Creating Prometheus alerts configuration..."
    cat > monitoring/prometheus-alerts.yml << EOF
groups:
  - name: contract-analyzer
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ \$value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ \$value }} seconds"
      
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ \$labels.job }} is down"
EOF
    
    # Create Alertmanager configuration
    print_status "Creating Alertmanager configuration..."
    cat > monitoring/alertmanager.yml << EOF
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@contract-analyzer.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/'
        send_resolved: true
EOF
    
    print_success "Monitoring infrastructure setup completed"
}

# Function to start monitoring services
start_monitoring() {
    print_status "Starting monitoring services..."
    
    # Start Prometheus
    print_status "Starting Prometheus..."
    docker-compose up -d prometheus
    
    # Start Grafana
    print_status "Starting Grafana..."
    docker-compose up -d grafana
    
    # Start Alertmanager
    print_status "Starting Alertmanager..."
    docker-compose up -d alertmanager
    
    # Start Jaeger
    print_status "Starting Jaeger..."
    docker-compose up -d jaeger
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    print_success "Monitoring services started"
    echo
    echo "Monitoring URLs:"
    echo "  Prometheus:  http://localhost:9090"
    echo "  Grafana:     http://localhost:3000 (admin/admin123)"
    echo "  Alertmanager: http://localhost:9093"
    echo "  Jaeger:      http://localhost:16686"
}

# Function to stop monitoring services
stop_monitoring() {
    print_status "Stopping monitoring services..."
    docker-compose stop prometheus grafana alertmanager jaeger
    print_success "Monitoring services stopped"
}

# Function to restart monitoring services
restart_monitoring() {
    print_status "Restarting monitoring services..."
    stop_monitoring
    start_monitoring
    print_success "Monitoring services restarted"
}

# Function to show monitoring status
show_status() {
    print_status "Monitoring service status:"
    docker-compose ps prometheus grafana alertmanager jaeger
    echo
    print_status "Service health:"
    
    # Check Prometheus
    if curl -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
        print_success "Prometheus is healthy"
    else
        print_error "Prometheus is not responding"
    fi
    
    # Check Grafana
    if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
        print_success "Grafana is healthy"
    else
        print_error "Grafana is not responding"
    fi
    
    # Check Alertmanager
    if curl -s http://localhost:9093/-/healthy >/dev/null 2>&1; then
        print_success "Alertmanager is healthy"
    else
        print_error "Alertmanager is not responding"
    fi
    
    # Check Jaeger
    if curl -s http://localhost:16686/api/services >/dev/null 2>&1; then
        print_success "Jaeger is healthy"
    else
        print_error "Jaeger is not responding"
    fi
}

# Function to show monitoring logs
show_logs() {
    print_status "Showing monitoring logs..."
    docker-compose logs -f prometheus grafana alertmanager jaeger
}

# Function to show monitoring configuration
show_config() {
    print_status "Monitoring configuration:"
    echo
    echo "Prometheus configuration:"
    cat monitoring/prometheus.yml
    echo
    echo "Alertmanager configuration:"
    cat monitoring/alertmanager.yml
    echo
    echo "Grafana datasources:"
    cat monitoring/grafana-datasources.yml
}

# Function to test monitoring setup
test_monitoring() {
    print_status "Testing monitoring setup..."
    
    # Test Prometheus metrics
    print_status "Testing Prometheus metrics..."
    if curl -s http://localhost:9090/api/v1/query?query=up | grep -q "success"; then
        print_success "Prometheus metrics are working"
    else
        print_error "Prometheus metrics test failed"
    fi
    
    # Test Grafana API
    print_status "Testing Grafana API..."
    if curl -s http://localhost:3000/api/health | grep -q "ok"; then
        print_success "Grafana API is working"
    else
        print_error "Grafana API test failed"
    fi
    
    # Test Alertmanager API
    print_status "Testing Alertmanager API..."
    if curl -s http://localhost:9093/api/v1/status | grep -q "success"; then
        print_success "Alertmanager API is working"
    else
        print_error "Alertmanager API test failed"
    fi
    
    # Test Jaeger API
    print_status "Testing Jaeger API..."
    if curl -s http://localhost:16686/api/services | grep -q "services"; then
        print_success "Jaeger API is working"
    else
        print_error "Jaeger API test failed"
    fi
    
    print_success "Monitoring setup test completed"
}

# Function to cleanup monitoring data
cleanup_monitoring() {
    print_status "Cleaning up monitoring data..."
    
    # Stop services
    stop_monitoring
    
    # Remove data volumes
    docker volume rm contract-analyzer_prometheus_data 2>/dev/null || true
    docker volume rm contract-analyzer_grafana_data 2>/dev/null || true
    
    # Remove data directories
    rm -rf monitoring/data/*
    
    print_success "Monitoring data cleaned up"
}

# Main function
main() {
    case "${1:-help}" in
        setup)
            setup_monitoring
            ;;
        start)
            start_monitoring
            ;;
        stop)
            stop_monitoring
            ;;
        restart)
            restart_monitoring
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        config)
            show_config
            ;;
        test)
            test_monitoring
            ;;
        cleanup)
            cleanup_monitoring
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
