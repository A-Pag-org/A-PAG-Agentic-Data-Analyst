#!/usr/bin/env python3
"""
Integration tests for render.yaml configuration.
Tests service dependencies, environment variable references, and deployment readiness.
"""

import yaml
import sys
from pathlib import Path


def load_render_config():
    """Load and parse render.yaml."""
    yaml_path = Path(__file__).parent / "render.yaml"
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def test_service_dependencies(data):
    """Test that service dependencies are correctly configured."""
    print("✓ Testing service dependencies...")
    
    services = data.get('services', [])
    databases = data.get('databases', [])
    
    # Create lookup maps
    service_names = {s['name'] for s in services}
    db_names = {db['name'] for db in databases}
    
    issues = []
    
    for service in services:
        if 'envVars' in service:
            for env_var in service['envVars']:
                # Check fromDatabase references
                if 'fromDatabase' in env_var:
                    db_ref = env_var['fromDatabase'].get('name')
                    if db_ref not in db_names:
                        issues.append(
                            f"Service '{service['name']}' references non-existent database '{db_ref}'"
                        )
                
                # Check fromService references
                if 'fromService' in env_var:
                    service_ref = env_var['fromService'].get('name')
                    if service_ref not in service_names:
                        issues.append(
                            f"Service '{service['name']}' references non-existent service '{service_ref}'"
                        )
    
    if issues:
        print("  ✗ Found dependency issues:")
        for issue in issues:
            print(f"     - {issue}")
        return False
    
    print("  ✓ All service dependencies are valid")
    return True


def test_backend_configuration(data):
    """Test backend service configuration."""
    print("✓ Testing backend service configuration...")
    
    services = data.get('services', [])
    backend = next((s for s in services if s['name'] == 'ai-backend'), None)
    
    if not backend:
        print("  ✗ Backend service 'ai-backend' not found")
        return False
    
    # Check required backend configurations
    checks = []
    
    # Check environment
    if backend.get('env') != 'python':
        checks.append("Backend should use 'python' environment")
    
    # Check commands
    if 'buildCommand' not in backend:
        checks.append("Backend missing 'buildCommand'")
    elif 'pip install -r requirements.txt' not in backend['buildCommand']:
        checks.append("Backend buildCommand should install requirements.txt")
    
    if 'startCommand' not in backend:
        checks.append("Backend missing 'startCommand'")
    elif 'uvicorn' not in backend['startCommand']:
        checks.append("Backend should use uvicorn to start")
    
    # Check health check
    if 'healthCheckPath' not in backend:
        checks.append("Backend should have healthCheckPath")
    elif backend['healthCheckPath'] != '/api/v1/health':
        checks.append("Backend healthCheckPath should be '/api/v1/health'")
    
    # Check environment variables
    has_environment = False
    has_database_url = False
    has_auth_token = False
    
    if 'envVars' in backend:
        for env_var in backend['envVars']:
            if env_var.get('key') == 'ENVIRONMENT':
                has_environment = True
            if env_var.get('key') == 'DATABASE_URL':
                has_database_url = True
    
    # Accept either service-level envVarGroups or envVars with fromGroup
    if 'envVarGroups' in backend:
        for group_name in backend['envVarGroups']:
            if group_name == 'shared-auth':
                has_auth_token = True
    if 'envVars' in backend and not has_auth_token:
        for env_var in backend['envVars']:
            if 'fromGroup' in env_var and isinstance(env_var['fromGroup'], dict):
                if env_var['fromGroup'].get('name') == 'shared-auth':
                    has_auth_token = True
    
    if not has_environment:
        checks.append("Backend missing ENVIRONMENT variable")
    if not has_database_url:
        checks.append("Backend missing DATABASE_URL variable")
    if not has_auth_token:
        checks.append("Backend missing shared-auth group (AUTH_BEARER_TOKEN)")
    
    if checks:
        print("  ✗ Backend configuration issues:")
        for check in checks:
            print(f"     - {check}")
        return False
    
    print("  ✓ Backend service is properly configured")
    return True


def test_frontend_configuration(data):
    """Test frontend service configuration."""
    print("✓ Testing frontend service configuration...")
    
    services = data.get('services', [])
    frontend = next((s for s in services if s['name'] == 'ai-frontend'), None)
    
    if not frontend:
        print("  ✗ Frontend service 'ai-frontend' not found")
        return False
    
    checks = []
    
    # Check environment
    if frontend.get('env') != 'node':
        checks.append("Frontend should use 'node' environment")
    
    # Check commands
    if 'buildCommand' not in frontend:
        checks.append("Frontend missing 'buildCommand'")
    elif 'npm' not in frontend['buildCommand'] or 'build' not in frontend['buildCommand']:
        checks.append("Frontend buildCommand should build the app")
    
    if 'startCommand' not in frontend:
        checks.append("Frontend missing 'startCommand'")
    elif 'npm' not in frontend['startCommand'] or 'start' not in frontend['startCommand']:
        checks.append("Frontend should use 'npm start' or 'npm run start'")
    
    # Check environment variables
    has_backend_url = False
    has_public_backend_url = False
    
    if 'envVars' in frontend:
        for env_var in frontend['envVars']:
            if env_var.get('key') == 'BACKEND_URL':
                has_backend_url = True
                # Should reference ai-backend service
                if 'fromService' in env_var:
                    if env_var['fromService'].get('name') != 'ai-backend':
                        checks.append("BACKEND_URL should reference 'ai-backend' service")
            
            if env_var.get('key') == 'NEXT_PUBLIC_BACKEND_URL':
                has_public_backend_url = True
                # Should reference ai-backend service
                if 'fromService' in env_var:
                    if env_var['fromService'].get('name') != 'ai-backend':
                        checks.append("NEXT_PUBLIC_BACKEND_URL should reference 'ai-backend' service")
    
    if not has_backend_url:
        checks.append("Frontend missing BACKEND_URL variable")
    if not has_public_backend_url:
        checks.append("Frontend missing NEXT_PUBLIC_BACKEND_URL variable")
    
    if checks:
        print("  ✗ Frontend configuration issues:")
        for check in checks:
            print(f"     - {check}")
        return False
    
    print("  ✓ Frontend service is properly configured")
    return True


def test_database_configuration(data):
    """Test database configuration."""
    print("✓ Testing database configuration...")
    
    databases = data.get('databases', [])
    
    if not databases:
        print("  ✗ No databases configured")
        return False
    
    db = databases[0]
    
    checks = []
    
    if db.get('name') != 'ai-db':
        checks.append("Database should be named 'ai-db'")
    
    # Check if database is referenced by services
    services = data.get('services', [])
    db_referenced = False
    
    for service in services:
        if 'envVars' in service:
            for env_var in service['envVars']:
                if 'fromDatabase' in env_var:
                    if env_var['fromDatabase'].get('name') == db['name']:
                        db_referenced = True
                        break
    
    if not db_referenced:
        checks.append("Database is not referenced by any service")
    
    if checks:
        print("  ✗ Database configuration issues:")
        for check in checks:
            print(f"     - {check}")
        return False
    
    print("  ✓ Database is properly configured")
    return True


def test_environment_variable_groups(data):
    """Test environment variable groups are properly used."""
    print("✓ Testing environment variable groups usage...")
    
    env_var_groups = data.get('envVarGroups', [])
    
    if not env_var_groups:
        print("  ⚠ No environment variable groups defined")
        return True
    
    group_names = {g['name'] for g in env_var_groups}
    
    # Check if groups are used by services
    services = data.get('services', [])
    used_groups = set()
    
    for service in services:
        if 'envVarGroups' in service:
            used_groups.update(service['envVarGroups'])
        if 'envVars' in service:
            for env_var in service['envVars']:
                if 'fromGroup' in env_var and isinstance(env_var['fromGroup'], dict):
                    name = env_var['fromGroup'].get('name')
                    if name:
                        used_groups.add(name)
    
    unused_groups = group_names - used_groups
    
    if unused_groups:
        print(f"  ⚠ WARNING: Groups defined but not used: {', '.join(unused_groups)}")
    
    # Verify AUTH_BEARER_TOKEN is in shared-auth group
    shared_auth = next((g for g in env_var_groups if g['name'] == 'shared-auth'), None)
    
    if shared_auth:
        auth_token = next((v for v in shared_auth['envVars'] if v['key'] == 'AUTH_BEARER_TOKEN'), None)
        
        if not auth_token:
            print("  ✗ shared-auth group missing AUTH_BEARER_TOKEN")
            return False
        
        if 'sync' not in auth_token or auth_token['sync'] != False:
            print("  ⚠ WARNING: AUTH_BEARER_TOKEN should have 'sync: false' to prevent syncing")
    
    print("  ✓ Environment variable groups are properly configured")
    return True


def test_production_readiness(data):
    """Test configuration for production readiness."""
    print("✓ Testing production readiness...")
    
    checks = []
    warnings = []
    
    services = data.get('services', [])
    
    for service in services:
        # Check autoDeploy
        if service.get('autoDeploy') != True:
            warnings.append(f"Service '{service['name']}' doesn't have autoDeploy enabled")
        
        # Check rootDir
        if 'rootDir' not in service:
            checks.append(f"Service '{service['name']}' missing rootDir")
        
        # Check web services have health checks
        if service.get('type') == 'web':
            if 'healthCheckPath' not in service:
                warnings.append(f"Web service '{service['name']}' missing healthCheckPath")
    
    # Check for production environment
    backend = next((s for s in services if s['name'] == 'ai-backend'), None)
    if backend and 'envVars' in backend:
        env_var = next((v for v in backend['envVars'] if v['key'] == 'ENVIRONMENT'), None)
        if env_var and env_var.get('value') == 'production':
            print("  ✓ Backend configured for production environment")
    
    if checks:
        print("  ✗ Production readiness issues:")
        for check in checks:
            print(f"     - {check}")
        return False
    
    if warnings:
        print("  ⚠ Production warnings:")
        for warning in warnings:
            print(f"     - {warning}")
    
    print("  ✓ Configuration is production-ready")
    return True


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("RENDER.YAML INTEGRATION TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        data = load_render_config()
    except Exception as e:
        print(f"❌ Failed to load render.yaml: {e}")
        sys.exit(1)
    
    # Run all tests
    tests = [
        test_service_dependencies,
        test_backend_configuration,
        test_frontend_configuration,
        test_database_configuration,
        test_environment_variable_groups,
        test_production_readiness,
    ]
    
    all_passed = True
    
    for test_func in tests:
        if not test_func(data):
            all_passed = False
        print()
    
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print("\nYour render.yaml is properly configured and ready for deployment!")
        sys.exit(0)
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("=" * 60)
        print("\nPlease review the issues above and fix them.")
        sys.exit(1)


if __name__ == '__main__':
    main()
