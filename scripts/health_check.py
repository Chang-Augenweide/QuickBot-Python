#!/usr/bin/python3
"""
QuickBot Health Check Module

Monitors system health, performance metrics,
and ensures all components are functioning properly.
"""

import os
import sys
import time
import sqlite3
import psutil
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class HealthChecker:
    """Health checker for QuickBot"""

    def __init__(self, config):
        self.config = config

    def check_disk_space(self) -> Dict:
        """Check disk space"""
        disk = psutil.disk_usage('/')
        free_percent = (disk.free / disk.total) * 100

        return {
            'status': 'healthy' if free_percent > 10 else 'warning' if free_percent > 5 else 'critical',
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'free_percent': free_percent
        }

    def check_memory_usage(self) -> Dict:
        """Check memory usage"""
        mem = psutil.virtual_memory()
        result = {
            'status': 'healthy' if mem.percent < 80 else 'warning' if mem.percent < 90 else 'critical',
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }
        return result

    def check_cpu_usage(self) -> Dict:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)

        return {
            'status': 'healthy' if cpu_percent < 70 else 'warning' if cpu_percent < 90 else 'critical',
            'percent': cpu_percent,
            'core_count': psutil.cpu_count()
        }

    def check_database(self, db_path: str) -> Dict:
        """Check database health"""
        if not os.path.exists(db_path):
            return {'status': 'error', 'message': 'Database file not found'}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check database size
            size = os.path.getsize(db_path)
            size_mb = size / (1024 * 1024)

            # Test connection
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            table_count = cursor.fetchone()[0]

            conn.close()

            return {
                'status': 'healthy' if size_mb < 100 else 'warning',
                'path': db_path,
                'size_bytes': size,
                'size_mb': round(size_mb, 2),
                'table_count': table_count
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_api_endpoints(self) -> Dict:
        """Check API endpoint health"""
        try:
            import requests

            api_url = f"http://localhost:{self.config.get('api.port', 8080)}/health"
            response = requests.get(api_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'data': data
                }
            else:
                return {'status': 'error', 'message': f'status_code={response.status_code}'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_memory_db_size(self, db_path: str) -> Dict:
        """Check memory database size and message count"""
        if not os.path.exists(db_path):
            return {'status': 'error', 'message': 'Database not found'}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get message count
            cursor.execute("SELECT COUNT(*) FROM messages")
            msg_count = cursor.fetchone()[0]

            # Get session count
            cursor.execute("SELECT COUNT(*) FROM sessions")
            session_count = cursor.fetchone()[0]

            conn.close()

            return {
                'status': 'healthy',
                'message_count': msg_count,
                'session_count': session_count
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_scheduler_db(self, db_path: str) -> Dict:
        """Check scheduler database"""
        if not os.path.exists(db_path):
            return {'status': 'error', 'message': 'Database not found'}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get task count
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]

            # Get enabled task count
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE enabled = 1")
            enabled_count = cursor.fetchone()[0]

            conn.close()

            return {
                'status': 'healthy',
                'task_count': task_count,
                'enabled_count': enabled_count
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_uptime(self) -> Dict:
        """Check system uptime"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        return {
            'status': 'healthy',
            'boot_time': boot_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'uptime_human': f"{days}d {hours}h {minutes}m"
        }

    def run_complete_check(self) -> Dict:
        """Run complete health check"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }

        # Run all checks
        results['checks']['disk'] = self.check_disk_space()
        results['checks']['memory'] = self.check_memory_usage()
        results['checks']['cpu'] = self.check_cpu_usage()
        results['checks']['uptime'] = self.check_uptime()

        # Check databases
        memory_db = self.config.get('memory.storage', 'memory.db')
        results['checks']['memory_db'] = self.check_database(memory_db)
        results['checks']['memory_db_details'] = self.check_memory_db_size(memory_db)

        scheduler_db = self.config.get('scheduler.storage', 'scheduler.db')
        results['checks']['scheduler_db'] = self.check_database(scheduler_db)
        results['checks']['scheduler_db_details'] = self.check_scheduler_db(scheduler_db)

        # Check API if enabled
        # results['checks']['api'] = self.check_api_endpoints()

        # Determine overall status
        for check_name, check_result in results['checks'].items():
            if isinstance(check_result, dict):
                status = check_result.get('status', 'healthy')
                if status == 'critical':
                    results['overall_status'] = 'critical'
                    break
                elif status == 'warning' and results['overall_status'] != 'critical':
                    results['overall_status'] = 'warning'
                elif status == 'error':
                    results['overall_status'] = 'error'

        return results

    def print_health_report(self, results: Dict):
        """Print health report"""
        status_symbols = {
            'healthy': '✓',
            'warning': '⚠',
            'error': '✗',
            'critical': '🔴'
        }

        status_emoji = status_symbols.get(results['overall_status'], '?')
        print(f"\nQuickBot Health Check - {results['overall_status'].upper()} {status_emoji}")
        print("=" * 50)

        for check_name, check_result in results['checks'].items():
            if isinstance(check_result, dict):
                status = check_result.get('status', 'healthy')
                emoji = status_symbols.get(status, '?')
                print(f"{emoji} {check_name}: {status}")

                # Print details for some checks
                if check_name == 'disk':
                    free_percent = check_result.get('free_percent', 0)
                    print(f"    Free space: {free_percent:.1f}%")
                elif check_name == 'memory':
                    percent = check_result.get('percent', 0)
                    print(f"    Usage: {percent:.1f}%")
                elif check_name == 'cpu':
                    percent = check_result.get('percent', 0)
                    print(f"    Usage: {percent:.1f}%")
                elif check_name == 'uptime':
                    uptime = check_result.get('uptime_human', 'N/A')
                    print(f"    Uptime: {uptime}")


def main():
    """Main function"""
    print("QuickBot Health Check Module")
    print("=" * 50)

    # Load config
    from config import Config

    try:
        config = Config('config.yaml')
    except:
        print("Error: Could not load configuration")
        return 1

    # Create health checker
    checker = HealthChecker(config)

    # Run health check
    results = checker.run_complete_check()

    # Print report
    checker.print_health_report(results)

    # Return exit code
    if results['overall_status'] in ['error', 'critical']:
        return 1
    elif results['overall_status'] == 'warning':
        return 0
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
