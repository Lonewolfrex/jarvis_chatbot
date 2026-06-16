import json

class PipAuditParser:
    @staticmethod
    def parse( file_path, run_id, db ):
        print( f"[PipAudit] Parsing {file_path}" )

        with open( file_path, "r", encoding="utf-8" ) as file:
            report = json.load(file)

        count = 0
        dependencies = report.get( "dependencies", [] )

        for dependency in dependencies:
            package_name = dependency.get( "name", "" )
            vulns = dependency.get( "vulns", [] )

            for vuln in vulns:

                db.insert_finding(
                    run_id=run_id,
                    tool="PipAudit",
                    severity="HIGH",
                    title=f"{package_name}: " f"{vuln.get('id', '')}",
                    vulnerability_id=vuln.get( "id", "" )
                )
                count += 1

        print( f"[PipAudit] Imported " f"{count} findings" )