import os

from github_client import GitHubClient
from db_manager import DatabaseManager
from config import ARTIFACT_DIR

from parsers.bandit_parser import BanditParser
from parsers.pip_audit_parser import PipAuditParser
from parsers.sarif_parser import SarifParser
from parsers.trivy_parser import ( TrivyParser )

class ArtifactSync:
    def __init__(self):
        self.github = GitHubClient()
        self.db = DatabaseManager()

    # ----------------------------------
    # Find File
    # ----------------------------------
    def find_file( self, root_dir, target_name ):
        for root, dirs, files in os.walk( root_dir ):
            for file in files:
                if file == target_name:
                    return os.path.join( root, file )

        return None

    # ----------------------------------
    # Process One Run
    # ----------------------------------
    def process_run( self, run ):
        run_id = run["id"]
        if self.db.is_processed( run_id ):
            print( f"[SKIP] " f"Run {run_id}" )
            return

        print( f"\n[PROCESS] " f"Run {run_id}" )

        # Save workflow metadata
        self.db.insert_workflow_run( run )

        # Download artifacts
        self.github.download_all_artifacts( run_id )
        run_folder = os.path.join( ARTIFACT_DIR, str(run_id) )

        # ----------------------------------
        # Bandit
        # ----------------------------------
        bandit_file = self.find_file( run_folder, "bandit-results.json" )

        if bandit_file:
            BanditParser.parse( bandit_file, run_id, self.db )

        # ----------------------------------
        # Pip Audit
        # ----------------------------------
        pip_audit_file = self.find_file( run_folder, "pip-audit-report.json" )
        if pip_audit_file:
            PipAuditParser.parse( pip_audit_file, run_id, self.db )

        # ----------------------------------
        # Gitleaks SARIF
        # ----------------------------------
        sarif_file = self.find_file( run_folder, "results.sarif" )

        if sarif_file:
            SarifParser.parse( file_path=sarif_file, run_id=run_id, db=self.db, tool_name="Gitleaks", default_severity="CRITICAL" )

        # ----------------------------------
        # Trivy JSON
        # ----------------------------------
        trivy_file = self.find_file( run_folder, "trivy-results.json" )

        if trivy_file:
            TrivyParser.parse( trivy_file, run_id, self.db )

        self.db.mark_processed( run_id )
        print( f"[DONE] " f"Run {run_id}" )

    # ----------------------------------
    # Main Sync
    # ----------------------------------
    def sync(self):
        runs = ( self.github .get_workflow_runs( per_page=3 ) )
        for run in runs:
            self.process_run( run )

        self.db.close()


if __name__ == "__main__":
    ArtifactSync().sync()