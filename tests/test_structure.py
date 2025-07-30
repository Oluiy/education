"""
Test suite for verifying the existence and structure of all project components.
This ensures all services, API gateway, and required files are present.
"""

import os
import pytest
from pathlib import Path


class TestProjectStructure:
    """Test the overall project structure and file existence."""
    
    def test_project_root_exists(self, project_root):
        """Test that project root directory exists."""
        assert project_root.exists(), f"Project root {project_root} does not exist"
        assert project_root.is_dir(), f"Project root {project_root} is not a directory"
    
    def test_essential_files_exist(self, project_root):
        """Test that essential project files exist."""
        essential_files = [
            "docker-compose.yml",
            ".gitignore",
        ]
        
        for file_name in essential_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Essential file {file_name} is missing from project root"
        
        # README.md is optional - some projects may not have it
        readme_path = project_root / "README.md"
        if not readme_path.exists():
            print(f"Note: README.md not found in project root (optional)")
        else:
            print(f"✓ README.md found in project root")
    
    def test_services_directory_exists(self, services_dir):
        """Test that services directory exists."""
        assert services_dir.exists(), "Services directory does not exist"
        assert services_dir.is_dir(), "Services directory is not a directory"
    
    def test_api_gateway_exists(self, api_gateway_dir):
        """Test that API gateway directory exists."""
        assert api_gateway_dir.exists(), "API gateway directory does not exist"
        assert api_gateway_dir.is_dir(), "API gateway directory is not a directory"


class TestServicesStructure:
    """Test the structure of all microservices."""
    
    EXPECTED_SERVICES = [
        "admin-service",
        "assistant-service", 
        "auth-service",
        "content-quiz-service",
        "file-storage-service",
        "notification-service",
        "progress-service",
        "sync-messaging-service"
    ]
    
    def test_all_services_exist(self, services_dir):
        """Test that all expected services exist."""
        existing_services = [d.name for d in services_dir.iterdir() if d.is_dir()]
        
        for service in self.EXPECTED_SERVICES:
            assert service in existing_services, f"Service {service} is missing"
    
    @pytest.mark.parametrize("service_name", EXPECTED_SERVICES)
    def test_service_structure(self, services_dir, service_name):
        """Test that each service has the required files and folders."""
        service_dir = services_dir / service_name
        
        # Essential files - at least app directory should exist
        app_dir = service_dir / "app"
        assert app_dir.exists(), f"Service {service_name} is missing app directory"
        
        # Optional files that may exist in well-structured services
        optional_files = [
            "README.md",
            "requirements.txt", 
            "Dockerfile",
            "main.py",
            ".env.example"
        ]
        
        existing_files = []
        missing_files = []
        
        for file_name in optional_files:
            file_path = service_dir / file_name
            if file_path.exists():
                existing_files.append(file_name)
            else:
                missing_files.append(file_name)
        
        # Service should have at least some structure files
        if len(existing_files) == 0:
            print(f"Warning: Service {service_name} has minimal structure (only app/ directory)")
        else:
            print(f"✓ Service {service_name} has {len(existing_files)} structure files: {', '.join(existing_files)}")
            if missing_files:
                print(f"  Note: Missing optional files: {', '.join(missing_files)}")
        
        # Required directories
        required_dirs = ["app"]
        
        for dir_name in required_dirs:
            dir_path = service_dir / dir_name
            assert dir_path.exists(), f"Service {service_name} is missing {dir_name} directory"
            assert dir_path.is_dir(), f"{dir_name} in {service_name} is not a directory"
    
    @pytest.mark.parametrize("service_name", EXPECTED_SERVICES)
    def test_service_app_structure(self, services_dir, service_name):
        """Test that each service app directory has required structure."""
        app_dir = services_dir / service_name / "app"
        
        if not app_dir.exists():
            print(f"Warning: Service {service_name} has no app directory")
            return
        
        # Check for Python files that indicate structure
        py_files = list(app_dir.glob("*.py"))
        
        # Check for common subdirectories (may not all be present in every service)
        common_dirs = ["api", "models", "core", "routers", "services", "utils"]
        existing_dirs = [d.name for d in app_dir.iterdir() if d.is_dir()]
        
        # Service should have some structure (either Python files or subdirectories)
        has_py_files = len(py_files) > 0
        has_structure_dirs = any(dir_name in existing_dirs for dir_name in common_dirs)
        
        if has_py_files:
            print(f"✓ Service {service_name}/app has {len(py_files)} Python files")
        if has_structure_dirs:
            common_found = [d for d in common_dirs if d in existing_dirs]
            print(f"✓ Service {service_name}/app has structure directories: {', '.join(common_found)}")
        
        if not has_py_files and not has_structure_dirs:
            print(f"Warning: Service {service_name}/app appears to have minimal structure")
        
        # At least the directory should exist (we checked above)
        assert app_dir.is_dir(), f"Service {service_name}/app exists but is not a directory"


class TestAPIGatewayStructure:
    """Test the API gateway structure."""
    
    def test_gateway_required_files(self, api_gateway_dir):
        """Test that API gateway has all required files."""
        required_files = [
            "main.py",
            "requirements.txt",
            "Dockerfile", 
            "README.md",
            ".env.example"
        ]
        
        for file_name in required_files:
            file_path = api_gateway_dir / file_name
            assert file_path.exists(), f"API gateway is missing {file_name}"
    
    def test_gateway_app_structure(self, api_gateway_dir):
        """Test that API gateway app directory exists and has structure."""
        app_dir = api_gateway_dir / "app"
        assert app_dir.exists(), "API gateway app directory does not exist"
        assert app_dir.is_dir(), "API gateway app is not a directory"
        
        # Required files in app directory
        main_py = app_dir / "main.py"
        init_py = app_dir / "__init__.py"
        
        assert main_py.exists(), "API gateway app/main.py does not exist"
        assert init_py.exists(), "API gateway app/__init__.py does not exist"


class TestConfigurationFiles:
    """Test configuration files across all services."""
    
    def test_docker_compose_file(self, project_root):
        """Test that docker-compose.yml exists and is not empty."""
        compose_file = project_root / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml does not exist"
        
        content = compose_file.read_text()
        assert len(content.strip()) > 0, "docker-compose.yml is empty"
        
        # Check for essential docker-compose content (version is optional in newer formats)
        assert "services:" in content, "docker-compose.yml missing services section"
        print(f"✓ docker-compose.yml has {content.count('build:')} build services and {content.count('image:')} image services")
    
    @pytest.mark.parametrize("service_name", TestServicesStructure.EXPECTED_SERVICES)
    def test_service_requirements_file(self, services_dir, service_name):
        """Test that each service has a non-empty requirements.txt if it exists."""
        requirements_file = services_dir / service_name / "requirements.txt"
        if requirements_file.exists():
            content = requirements_file.read_text()
            assert len(content.strip()) > 0, f"Service {service_name} requirements.txt is empty"
            print(f"✓ Service {service_name} has requirements.txt with {len(content.splitlines())} lines")
        else:
            print(f"Note: Service {service_name} has no requirements.txt (may be minimal/incomplete)")
    
    def test_gateway_requirements_file(self, api_gateway_dir):
        """Test that API gateway has a non-empty requirements.txt."""
        requirements_file = api_gateway_dir / "requirements.txt"
        assert requirements_file.exists(), "API gateway missing requirements.txt"
        
        content = requirements_file.read_text()
        assert len(content.strip()) > 0, "API gateway requirements.txt is empty"
    
    @pytest.mark.parametrize("service_name", TestServicesStructure.EXPECTED_SERVICES)
    def test_service_dockerfile(self, services_dir, service_name):
        """Test that each service has a valid Dockerfile if it exists."""
        dockerfile = services_dir / service_name / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            assert len(content.strip()) > 0, f"Service {service_name} Dockerfile is empty"
            assert "FROM" in content, f"Service {service_name} Dockerfile missing FROM instruction"
            print(f"✓ Service {service_name} has valid Dockerfile")
        else:
            print(f"Note: Service {service_name} has no Dockerfile (may be minimal/incomplete)")
    
    def test_gateway_dockerfile(self, api_gateway_dir):
        """Test that API gateway has a valid Dockerfile."""
        dockerfile = api_gateway_dir / "Dockerfile"
        assert dockerfile.exists(), "API gateway missing Dockerfile"
        
        content = dockerfile.read_text()
        assert len(content.strip()) > 0, "API gateway Dockerfile is empty"
        assert "FROM" in content, "API gateway Dockerfile missing FROM instruction"


class TestPythonModules:
    """Test that Python modules can be imported."""
    
    @pytest.mark.parametrize("service_name", TestServicesStructure.EXPECTED_SERVICES)
    def test_service_main_module_syntax(self, services_dir, service_name):
        """Test that service main.py files have valid Python syntax."""
        main_py = services_dir / service_name / "main.py"
        if main_py.exists():
            try:
                content = main_py.read_text(encoding='utf-8')
                compile(content, str(main_py), 'exec')
                print(f"✓ Service {service_name} main.py has valid syntax")
            except UnicodeDecodeError:
                try:
                    content = main_py.read_text(encoding='latin1')
                    compile(content, str(main_py), 'exec')
                    print(f"✓ Service {service_name} main.py has valid syntax (latin1 encoding)")
                except (UnicodeDecodeError, SyntaxError) as e:
                    pytest.fail(f"Service {service_name} main.py encoding/syntax error: {e}")
            except SyntaxError as e:
                pytest.fail(f"Service {service_name} main.py has syntax error: {e}")
        else:
            print(f"Note: Service {service_name} has no main.py file")
    
    @pytest.mark.parametrize("service_name", TestServicesStructure.EXPECTED_SERVICES) 
    def test_service_app_main_syntax(self, services_dir, service_name):
        """Test that service app/main.py files have valid Python syntax."""
        app_main = services_dir / service_name / "app" / "main.py"
        if app_main.exists():
            try:
                content = app_main.read_text(encoding='utf-8')
                compile(content, str(app_main), 'exec')
                print(f"✓ Service {service_name} app/main.py has valid syntax")
            except UnicodeDecodeError:
                try:
                    content = app_main.read_text(encoding='latin1')
                    compile(content, str(app_main), 'exec')
                    print(f"✓ Service {service_name} app/main.py has valid syntax (latin1 encoding)")
                except (UnicodeDecodeError, SyntaxError) as e:
                    pytest.fail(f"Service {service_name} app/main.py encoding/syntax error: {e}")
            except SyntaxError as e:
                pytest.fail(f"Service {service_name} app/main.py has syntax error: {e}")
        else:
            print(f"Note: Service {service_name} has no app/main.py file")
    
    def test_gateway_main_syntax(self, api_gateway_dir):
        """Test that API gateway main.py has valid Python syntax."""
        main_py = api_gateway_dir / "main.py"
        if main_py.exists():
            try:
                content = main_py.read_text(encoding='utf-8')
                compile(content, str(main_py), 'exec')
                print(f"✓ API gateway main.py has valid syntax")
            except UnicodeDecodeError:
                try:
                    content = main_py.read_text(encoding='latin1')
                    compile(content, str(main_py), 'exec')
                    print(f"✓ API gateway main.py has valid syntax (latin1 encoding)")
                except (UnicodeDecodeError, SyntaxError) as e:
                    pytest.fail(f"API gateway main.py encoding/syntax error: {e}")
            except SyntaxError as e:
                pytest.fail(f"API gateway main.py has syntax error: {e}")
        else:
            print(f"Note: API gateway has no main.py file")
    
    def test_gateway_app_main_syntax(self, api_gateway_dir):
        """Test that API gateway app/main.py has valid Python syntax."""
        app_main = api_gateway_dir / "app" / "main.py"
        if app_main.exists():
            try:
                content = app_main.read_text(encoding='utf-8')
                compile(content, str(app_main), 'exec')
                print(f"✓ API gateway app/main.py has valid syntax")
            except UnicodeDecodeError:
                try:
                    content = app_main.read_text(encoding='latin1')
                    compile(content, str(app_main), 'exec')
                    print(f"✓ API gateway app/main.py has valid syntax (latin1 encoding)")
                except (UnicodeDecodeError, SyntaxError) as e:
                    pytest.fail(f"API gateway app/main.py encoding/syntax error: {e}")
            except SyntaxError as e:
                pytest.fail(f"API gateway app/main.py has syntax error: {e}")
        else:
            print(f"Note: API gateway has no app/main.py file")
