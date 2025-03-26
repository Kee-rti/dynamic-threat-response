import threading
import time
from threat_signatures import ThreatSignatures
from threat_detector import ThreatDetector
from network_analyzer import NetworkAnalyzer
from process_monitor import ProcessMonitor
from ui import ThreatResponseUI
from logger import ThreatLogger

class DynamicThreatResponseSystem:
    def __init__(self):
        self.logger = ThreatLogger()
        self.threat_detector = ThreatDetector(self.logger)
        self.is_monitoring = False
        self.monitoring_thread = None

    def start_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            self.logger.log_event("Threat Monitoring Started")
            return True
        return False

    def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)  
            self.logger.log_event("Threat Monitoring Stopped")
            return True
        return False

    def _monitoring_loop(self):
        while self.is_monitoring:
            try:
                network_connections = NetworkAnalyzer.get_network_connections()
                if not network_connections:
                    self.logger.log_event("No network connections retrieved", level='warning')
                for conn in network_connections:
                    if self.threat_detector.analyze_network_connection(conn):
                        self.logger.log_threat(
                            f"Threat detected in connection: {conn['remote_address']}:{conn['remote_port']}",
                            severity='medium',
                            details=conn
                        )
                running_processes = ProcessMonitor.get_running_processes()
                for process in running_processes:
                    self.threat_detector.analyze_process(process)
                time.sleep(5)
            except Exception as e:
                self.logger.log_event(f"Monitoring loop error: {e}", level = 'error')
        
    def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout = 5)  
                if self.monitoring_thread.is_alive():
                    self.logger.log_event("Warning: Monitoring thread still alive", level = 'warning')
            self.logger.log_event("Threat Monitoring Stopped")
            return True
        return False

def main():
    threat_system = DynamicThreatResponseSystem()
    ui = ThreatResponseUI(threat_system)
    ui.run()

if __name__ == "__main__":
    main()