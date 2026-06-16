import json
from prometheus_client import start_http_server
from prometheus_client import Gauge
import time

bandit_high = Gauge(
    "bandit_high_issues",
    "High severity Bandit issues"
)

gitleaks_findings = Gauge(
    "gitleaks_findings",
    "Secrets detected"
)

trivy_critical = Gauge(
    "trivy_critical_vulnerabilities",
    "Critical vulnerabilities"
)

pip_audit_vulns = Gauge(
    "pip_audit_vulnerabilities",
    "Python dependency vulnerabilities"
)

def update_metrics():

    try:
        with open( "reports/bandit-results.json" ) as f:
            report=json.load(f)
            highs=sum(
                1
                for r in report["results"]
                if r["issue_severity"]=="HIGH"
            )
            bandit_high.set(highs)

    except:
        pass

    try:
        with open( "reports/gitleaks-results.json" ) as f:
            report=json.load(f)
            gitleaks_findings.set( len(report) )
    except:
        pass

if __name__=="__main__":
    start_http_server( 8001 )
    while True:
        update_metrics()
        time.sleep(60)