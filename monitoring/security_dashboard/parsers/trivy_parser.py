import json

class TrivyParser:
    @staticmethod
    def parse( file_path, run_id, db ):

        print( f"[Trivy] Parsing " f"{file_path}" )

        with open( file_path, "r", encoding="utf-8" ) as file:
            report = json.load(file)

        imported = 0

        for result in report.get( "Results", [] ):
            vulnerabilities = ( result.get( "Vulnerabilities", [] ) )

            for vuln in vulnerabilities:
                db.insert_finding(
                    run_id=run_id,
                    tool="Trivy",
                    severity=vuln.get( "Severity", "UNKNOWN" ),
                    title=vuln.get( "Title", vuln.get( "PkgName", "" ) ),
                    vulnerability_id= vuln.get( "VulnerabilityID", "" )
                )

                imported += 1

        print( f"[Trivy] Imported " f"{imported} findings" )