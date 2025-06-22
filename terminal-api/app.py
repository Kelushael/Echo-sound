from flask import Flask, request, jsonify
import subprocess
import os
import time
import logging
from functools import wraps

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API keys (in production, use secrets manager)
API_KEYS = {
    os.environ.get("API_KEY", "default_key"): True
}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key not in API_KEYS:
            logger.warning(f"Unauthorized access attempt with key: {api_key}")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/execute', methods=['POST'])
@require_api_key
def execute_command():
    data = request.get_json()

    # Validate input
    if not data or 'command' not in data:
        return jsonify({"error": "Missing command parameter"}), 400

    command = data['command']
    working_dir = data.get('working_dir', os.getcwd())
    timeout = data.get('timeout', 30)

    # Basic security check
    if any(banned in command for banned in ['rm ', 'format ', 'dd ', 'shutdown', 'reboot']):
        return jsonify({"error": "Potentially dangerous command blocked"}), 403

    # Validate timeout
    if not (1 <= timeout <= 300):
        return jsonify({"error": "Timeout must be between 1 and 300 seconds"}), 400

    # Resolve home directory
    if working_dir.startswith('~'):
        working_dir = os.path.expanduser(working_dir)

    # Check directory exists
    if not os.path.isdir(working_dir):
        return jsonify({"error": f"Directory not found: {working_dir}"}), 400

    logger.info(f"Executing command: {command} in {working_dir}")

    try:
        start_time = time.time()

        # Execute command
        process = subprocess.Popen(
            command,
            cwd=working_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            exit_code = -1
            stderr = f"Command timed out after {timeout} seconds\n{stderr}"

        exec_time = time.time() - start_time

        response = {
            "command": command,
            "output": stdout,
            "error": stderr,
            "exit_code": exit_code,
            "execution_time": round(exec_time, 3)
        }

        logger.info(f"Command executed in {exec_time:.3f}s with exit code {exit_code}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
