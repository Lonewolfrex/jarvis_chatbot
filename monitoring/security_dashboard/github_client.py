import os
import json
import requests
import zipfile

from config import (
    GITHUB_OWNER,
    GITHUB_REPO,
    GITHUB_TOKEN,
    ARTIFACT_DIR
)

class GitHubClient:
    def __init__(self):
        self.headers = { "Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json" }
        self.base_url = ( f"https://api.github.com/repos/" f"{GITHUB_OWNER}/{GITHUB_REPO}" )

    # ----------------------------------
    # Get Workflow Runs
    # ----------------------------------
    def get_workflow_runs( self, per_page=20 ):

        url = (
            f"{self.base_url}"
            f"/actions/runs"
            f"?per_page={per_page}"
        )

        response = requests.get( url, headers=self.headers )
        response.raise_for_status()
        data = response.json()
        return data.get( "workflow_runs", [] )

    # ----------------------------------
    # Get Artifacts for Run
    # ----------------------------------
    def get_artifacts_for_run( self, run_id ):

        url = (
            f"{self.base_url}"
            f"/actions/runs/"
            f"{run_id}"
            f"/artifacts"
        )

        response = requests.get( url, headers=self.headers )
        response.raise_for_status()
        data = response.json()
        return data.get( "artifacts", [] )

    # ----------------------------------
    # Download Artifact
    # ----------------------------------
    def download_artifact( self, artifact, run_id ):
        artifact_name = artifact["name"]
        artifact_folder = os.path.join( ARTIFACT_DIR, str(run_id) )
        os.makedirs( artifact_folder, exist_ok=True )
        zip_path = os.path.join( artifact_folder, f"{artifact_name}.zip" )
        download_url = artifact[ "archive_download_url" ]
        print( f"[+] Downloading " f"{artifact_name}" )
        response = requests.get( download_url, headers=self.headers, stream=True )
        response.raise_for_status()

        with open( zip_path, "wb" ) as file:
            for chunk in response.iter_content( chunk_size=8192 ):
                file.write(chunk)

        print( f"[+] Downloaded: {artifact_name}" )
        self.extract_zip( zip_path, artifact_folder )

        try:
            os.remove( zip_path )
            print( f"[+] Removed ZIP: " f"{zip_path}" )

        except Exception as e:
            print( f"[!] Failed removing ZIP " f"{zip_path}: {e}" )

        return artifact_folder

    # ----------------------------------
    # Extract Artifact
    # ----------------------------------
    def extract_zip( self, zip_path, destination ):
        print( f"[+] Extracting " f"{zip_path}" )
        with zipfile.ZipFile( zip_path, "r" ) as zip_ref:
            zip_ref.extractall( destination )

        print( "[+] Extraction complete" )

    # ----------------------------------
    # Download All Artifacts
    # ----------------------------------
    def download_all_artifacts( self, run_id ):
        artifacts = ( self.get_artifacts_for_run( run_id ) )

        if not artifacts:
            print(
                f"[!] No artifacts "
                f"for run {run_id}"
            )
            return

        for artifact in artifacts:
            self.download_artifact( artifact, run_id )


def main():
    github = GitHubClient()
    runs = github.get_workflow_runs()
    if not runs:
        print( "No workflow runs found" )
        return

    latest_run = runs[0]
    run_id = latest_run["id"]

    print( "\nLatest Run Information" )
    print( f"Run ID : {run_id}" )
    print( f"Status : " f"{latest_run['status']}" )
    print( f"Conclusion : " f"{latest_run['conclusion']}" )
    print( "\nDownloading artifacts..." )
    github.download_all_artifacts( run_id )
    print( "\nCompleted." )

if __name__ == "__main__":
    main()