import json

class SarifParser:
    @staticmethod
    def parse( file_path, run_id, db, tool_name="SARIF", default_severity="HIGH" ):
        print( f"[{tool_name}] Parsing " f"{file_path}" )

        with open( file_path, "r", encoding="utf-8" ) as file:
            sarif = json.load(file)

        imported = 0

        for run in sarif.get( "runs", [] ):
            tool = ( run.get( "tool", {} ) .get( "driver", {} ) .get( "name", tool_name ) )
            results = run.get( "results", [] )

            for result in results:
                message = ( result.get( "message", {} ).get( "text", "Security Finding" ) )
                severity = ( result.get( "level", default_severity ) )
                vulnerability_id = ""
                rule_id = result.get( "ruleId" )
                if rule_id: 
                    vulnerability_id = ( rule_id )
                file_path_value = ""
                locations = result.get( "locations", [] )

                if locations:
                    try:
                        file_path_value = ( locations[0] ["physicalLocation"] ["artifactLocation"] ["uri"] )

                    except Exception:
                        pass

                db.insert_finding(
                    run_id=run_id,
                    tool=tool,
                    severity=severity,
                    title=message,
                    file_path=file_path_value,
                    vulnerability_id=
                    vulnerability_id
                )

                imported += 1

        print( f"[{tool_name}] Imported " f"{imported} findings" )