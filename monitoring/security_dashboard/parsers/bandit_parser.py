import json

class BanditParser:

    @staticmethod
    def parse( file_path, run_id, db ):
        print( f"[Bandit] Parsing {file_path}" )

        with open( file_path, "r", encoding="utf-8" ) as file:
            report = json.load(file)

        findings = report.get( "results", [] )

        for finding in findings:

            db.insert_finding(
                run_id=run_id,
                tool="Bandit",
                severity=finding.get( "issue_severity", "UNKNOWN" ),
                title=finding.get( "issue_text", "" ),
                file_path=finding.get( "filename", "" )
            )

        print(
            f"[Bandit] Imported "
            f"{len(findings)} findings"
        )