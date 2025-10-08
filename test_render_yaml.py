#!/usr/bin/env python3
"""
Test suite for render.yaml configuration file.
Validates structure, syntax, and Render.com blueprint specifications.
"""

import yaml
import sys
from pathlib import Path


def test_yaml_syntax():
    """Test that render.yaml has valid YAML syntax."""
    print("✓ Testing YAML syntax...")
    
    yaml_path = Path(__file__).parent / "render.yaml"
    
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        print("  ✓ YAML syntax is valid")
        return True, data
    except yaml.YAMLError as e:
        print(f"  ✗ YAML syntax error: {e}")
        return False, None


def test_required_top_level_keys(data):
    """Test that required top-level keys are present."""
    print("✓ Testing required top-level keys...")
    
    if not data:
        print("  ✗ No data to validate")
        return False
    
    # Render.yaml can have: services, databases, envVarGroups
    if 'services' not in data:
        print("  ✗ Missing 'services' key")
        return False
    
    print("  ✓ Required keys present")
    return True


def test_env_var_groups(data):
    """Test environment variable groups configuration."""
    print("✓ Testing environment variable groups...")
    
    if 'envVarGroups' not in data:
        print("  ⚠ No envVarGroups defined (optional)")
        return True
    
    env_var_groups = data['envVarGroups']
    
    if not isinstance(env_var_groups, list):
        print("  ✗ envVarGroups must be a list")
        return False
    
    for idx, group in enumerate(env_var_groups):
        # Check required fields
        if 'name' not in group:
            print(f"  ✗ envVarGroup {idx} missing 'name' field")
            return False
        
        if 'envVars' not in group:
            print(f"  ✗ envVarGroup '{group['name']}' missing 'envVars' field")
            return False
        
        # Validate envVars
        for var_idx, env_var in enumerate(group['envVars']):
            if 'key' not in env_var:
                print(f"  ✗ envVar {var_idx} in group '{group['name']}' missing 'key'")
                return False
            
            # Check if generateValue is used (this is the potential issue)
            if 'generateValue' in env_var:
                print(f"  ⚠ WARNING: 'generateValue: {env_var['generateValue']}' found for key '{env_var['key']}'")
                print(f"     Render.com may not support 'generateValue' property.")
                print(f"     Valid properties: value, sync, fromDatabase, fromService, fromGroup")
                # This is a warning, not an error - continuing
    
    print("  ✓ Environment variable groups structure is valid")
    return True


def test_services(data):
    """Test services configuration."""
    print("✓ Testing services configuration...")
    
    services = data.get('services', [])
    
    if not isinstance(services, list):
        print("  ✗ services must be a list")
        return False
    
    if len(services) == 0:
        print("  ✗ At least one service is required")
        return False
    
    for idx, service in enumerate(services):
        # Check required service fields
        required_fields = ['type', 'name', 'env']
        for field in required_fields:
            if field not in service:
                print(f"  ✗ Service {idx} missing required field '{field}'")
                return False
        
        # Validate service type
        valid_types = ['web', 'worker', 'cron', 'pserv', 'redis']
        if service['type'] not in valid_types:
            print(f"  ✗ Service '{service['name']}' has invalid type '{service['type']}'")
            return False
        
        # Web services need specific commands
        if service['type'] == 'web':
            if 'startCommand' not in service:
                print(f"  ✗ Web service '{service['name']}' missing 'startCommand'")
                return False
        
        # Check environment variables
        if 'envVars' in service:
            for var in service['envVars']:
                # Support either key-based env var or fromGroup (which has no 'key')
                if 'fromGroup' in var:
                    grp = var['fromGroup']
                    if not isinstance(grp, dict) or 'name' not in grp:
                        print(f"  ✗ Service '{service['name']}' has invalid fromGroup reference")
                        return False
                    continue

                if 'key' not in var:
                    print(f"  ✗ Service '{service['name']}' has envVar without 'key' (and not fromGroup)")
                    return False
                
                # Check that envVar has a value source
                value_sources = ['value', 'fromDatabase', 'fromService', 'sync', 'generateValue']
                has_source = any(source in var for source in value_sources)
                
                if not has_source:
                    print(f"  ✗ Service '{service['name']}' envVar '{var['key']}' has no value source")
                    return False
    
    print(f"  ✓ {len(services)} service(s) validated successfully")
    return True


def test_databases(data):
    """Test databases configuration."""
    print("✓ Testing databases configuration...")
    
    if 'databases' not in data:
        print("  ⚠ No databases defined (optional)")
        return True
    
    databases = data['databases']
    
    if not isinstance(databases, list):
        print("  ✗ databases must be a list")
        return False
    
    for idx, db in enumerate(databases):
        if 'name' not in db:
            print(f"  ✗ Database {idx} missing 'name' field")
            return False
        
        # plan is optional but recommended
        if 'plan' not in db:
            print(f"  ⚠ Database '{db['name']}' missing 'plan' field")
    
    print(f"  ✓ {len(databases)} database(s) validated successfully")
    return True


def test_render_specific_issues(data):
    """Test for known Render.com specific issues."""
    print("✓ Testing Render.com specific configurations...")
    
    issues_found = []
    
    # Check for generateValue usage (not documented in Render API)
    if 'envVarGroups' in data:
        for group in data['envVarGroups']:
            for env_var in group.get('envVars', []):
                if 'generateValue' in env_var:
                    issues_found.append({
                        'type': 'unsupported_property',
                        'location': f"envVarGroups.{group['name']}.{env_var['key']}",
                        'issue': "'generateValue' is not a documented Render.com property",
                        'suggestion': "Use 'sync: false' to prevent syncing, or remove this property"
                    })
    
    if issues_found:
        print(f"  ⚠ Found {len(issues_found)} potential issue(s):")
        for issue in issues_found:
            print(f"     - {issue['location']}: {issue['issue']}")
            print(f"       Suggestion: {issue['suggestion']}")
        return False
    
    print("  ✓ No Render.com specific issues found")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("RENDER.YAML VALIDATION TEST SUITE")
    print("=" * 60)
    print()
    
    # Test 1: YAML syntax
    success, data = test_yaml_syntax()
    if not success:
        print("\n❌ YAML syntax test failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 2: Required keys
    if not test_required_top_level_keys(data):
        print("\n❌ Required keys test failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 3: Environment variable groups
    if not test_env_var_groups(data):
        print("\n❌ Environment variable groups test failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 4: Services
    if not test_services(data):
        print("\n❌ Services test failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 5: Databases
    if not test_databases(data):
        print("\n❌ Databases test failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 6: Render-specific issues
    render_issues = test_render_specific_issues(data)
    
    print()
    print("=" * 60)
    
    if render_issues:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("⚠️  TESTS PASSED WITH WARNINGS")
        print("=" * 60)
        print("\nThe YAML file is syntactically correct but has warnings.")
        print("Please review the warnings above and fix if necessary.")
        sys.exit(1)


if __name__ == '__main__':
    main()
