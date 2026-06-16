import sqlite3
from config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect( DB_PATH )
        self.cur = self.conn.cursor()

    # ----------------------------------
    # Run Tracking
    # ----------------------------------
    def is_processed( self, run_id ):
        self.cur.execute(
            """
            SELECT run_id
            FROM processed_runs
            WHERE run_id = ?
            """,
            (run_id,)
        )

        return ( self.cur.fetchone() is not None )

    def mark_processed( self, run_id ):
        self.cur.execute(
            """
            INSERT OR IGNORE
            INTO processed_runs(run_id)
            VALUES(?)
            """,
            (run_id,)
        )
        self.conn.commit()

    # ----------------------------------
    # Workflow Metadata
    # ----------------------------------
    def insert_workflow_run( self, run ):
        self.cur.execute(
            """
            INSERT OR REPLACE
            INTO workflow_runs
            (
                run_id,
                workflow_name,
                branch,
                status,
                conclusion,
                run_created_at
            )
            VALUES
            (
                ?,?,?,?,?,?
            )
            """,
            (
                run["id"],
                run["name"],
                run["head_branch"],
                run["status"],
                run["conclusion"],
                run["created_at"]
            )
        )

        self.conn.commit()

    # ----------------------------------
    # Findings
    # ----------------------------------
    def insert_finding( self, run_id, tool, severity, title, file_path="", cwe="", vulnerability_id="" ):
        self.cur.execute(
            """
            INSERT INTO findings
            (
                run_id,
                tool,
                severity,
                title,
                file_path,
                cwe,
                vulnerability_id
            )
            VALUES
            (
                ?,?,?,?,?,?,?
            )
            """,
            (
                run_id,
                tool,
                severity,
                title,
                file_path,
                cwe,
                vulnerability_id
            )
        )

        self.conn.commit()

    # ----------------------------------
    # Close
    # ----------------------------------
    def close(self):
        self.conn.close()