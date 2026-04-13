import subprocess
import json
import os
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class ScalableRunner:
    """Handles the execution of the Scalable CLI binary."""
    
    def __init__(self, bin_path: str):
        self.bin_path = bin_path

    def run(self, args: List[str], use_json: bool = True, capture_output: bool = True) -> Dict[str, Any]:
        """Executes a command and returns the decoded JSON or raw output."""
        cmd = [self.bin_path] + args
        
        if use_json and "--json" not in args:
            cmd.append("--json")
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        env = os.environ.copy()
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                env=env,
                check=True
            )
            
            if not capture_output:
                return {"ok": True, "output": None}

            stdout = result.stdout.strip() if result.stdout else ""
            
            if use_json:
                if not stdout:
                    return {"ok": False, "error": "No output from command"}
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to decode JSON: {stdout}")
                    return {"ok": False, "error": f"Invalid JSON output: {str(e)}"}
            
            return {"ok": True, "output": stdout}

        except subprocess.CalledProcessError as e:
            # If we didn't capture output, we can't show the error details from stdout/stderr
            if not capture_output:
                 return {"ok": False, "error": f"Process exited with code {e.returncode}"}

            stderr = e.stderr.strip() if e.stderr else e.stdout.strip()
            logger.debug(f"Command failed with exit code {e.returncode}: {stderr}")
            return {"ok": False, "error": stderr}
