import os
import json
import shutil
import logging
from datetime import datetime
from . import gemini

logger = logging.getLogger(__name__)

def duplicate_app_directory(branch_name, port, api_key=None):
    """Duplicate the app directory for the new branch"""
    try:
        source_dir = 'app'
        target_dir = f'branches/{branch_name}'
        
        # Remove existing directory if it exists
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # Copy the app directory
        shutil.copytree(source_dir, target_dir)
        logger.info(f"Duplicated app directory to {target_dir}")
        
        # Create branch-specific environment file
        create_branch_env_file(branch_name, target_dir, port, api_key)
        
        # Create branch-specific Docker Compose file
        create_branch_docker_compose(branch_name, target_dir, port)
        
        # Create branch-specific Gemini config if API key is provided
        if api_key:
            gemini.create_branch_gemini_settings(branch_name, target_dir, api_key)
        
        return target_dir
    except Exception as e:
        logger.error(f"Error duplicating app directory: {e}")
        raise

def create_branch_env_file(branch_name, target_dir, port, api_key=None):
    """Create environment file for the branch"""
    try:
        env_content = f"""# Environment variables for branch: {branch_name}
FLASK_APP=app.py
FLASK_ENV=development
PORT={port}
BRANCH_NAME={branch_name}
"""
        
        # Add Gemini API key if provided
        if api_key:
            env_content += f"GEMINI_API_KEY={api_key}\n"
        
        env_file = os.path.join(target_dir, '.env')
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Created environment file: {env_file}")
    except Exception as e:
        logger.warning(f"Could not create environment file: {e}")

def create_branch_docker_compose(branch_name, target_dir, port):
    """Create Docker Compose file for the branch using template"""
    try:
        # Read the template file
        template_path = os.path.join('app', 'docker-compose.branch.template.yaml')
        if not os.path.exists(template_path):
            logger.warning(f"Template file not found: {template_path}")
            return
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Calculate TTYD port (branch port + 1000)
        ttyd_port = port + 1000
        
        # Replace placeholders with actual values
        compose_content = template_content.replace('{{BRANCH_NAME}}', branch_name)
        compose_content = compose_content.replace('{{PORT}}', str(port))
        compose_content = compose_content.replace('{{PORT_TTYD}}', str(ttyd_port))
        
        compose_file = os.path.join(target_dir, 'docker-compose.yaml')
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        logger.info(f"Created Docker Compose file from template: {compose_file}")
    except Exception as e:
        logger.warning(f"Could not create Docker Compose file: {e}")

def create_branch_config(branch_name, port, app_dir):
    """Create configuration for the new branch"""
    config = {
        'branch_name': branch_name,
        'port': port,
        'app_directory': app_dir,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'status': 'created'
    }
    
    # Save config to file
    config_file = f'branches/{branch_name}/branch_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Note: Docker Compose file is already created by create_branch_docker_compose function
    
    return config 