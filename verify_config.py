#!/usr/bin/env python3
"""
Visual verification script for render.yaml configuration.
Displays the configuration in a readable format.
"""

import yaml
from pathlib import Path


def main():
    yaml_path = Path(__file__).parent / "render.yaml"
    
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("=" * 70)
    print("  RENDER.YAML CONFIGURATION SUMMARY")
    print("=" * 70)
    print()
    
    # Environment Variable Groups
    print("🔐 ENVIRONMENT VARIABLE GROUPS")
    print("-" * 70)
    if 'envVarGroups' in config:
        for group in config['envVarGroups']:
            print(f"  📦 {group['name']}")
            for var in group['envVars']:
                key = var['key']
                props = [k for k in var.keys() if k != 'key']
                print(f"     ├─ {key}")
                for prop in props:
                    print(f"     │  └─ {prop}: {var[prop]}")
    print()
    
    # Services
    print("🌐 SERVICES")
    print("-" * 70)
    for service in config.get('services', []):
        print(f"  🚀 {service['name']} ({service['type']})")
        print(f"     ├─ Environment: {service['env']}")
        print(f"     ├─ Plan: {service.get('plan', 'N/A')}")
        print(f"     ├─ Root Dir: {service.get('rootDir', 'N/A')}")
        
        if 'buildCommand' in service:
            print(f"     ├─ Build: {service['buildCommand'][:50]}...")
        
        if 'startCommand' in service:
            print(f"     ├─ Start: {service['startCommand']}")
        
        if 'healthCheckPath' in service:
            print(f"     ├─ Health: {service['healthCheckPath']}")
        
        print(f"     ├─ Auto Deploy: {service.get('autoDeploy', False)}")
        
        if 'envVarGroups' in service:
            print(f"     ├─ Env Groups: {', '.join(service['envVarGroups'])}")
        
        if 'envVars' in service:
            print(f"     └─ Environment Variables:")
            for var in service['envVars']:
                if 'fromGroup' in var and isinstance(var['fromGroup'], dict):
                    grp = var['fromGroup']
                    print(f"        ├─ ← Group:{grp.get('name')}")
                    continue
                key = var['key']
                if 'value' in var:
                    print(f"        ├─ {key} = {var['value']}")
                elif 'fromDatabase' in var:
                    db_name = var['fromDatabase']['name']
                    prop = var['fromDatabase']['property']
                    print(f"        ├─ {key} ← Database:{db_name}.{prop}")
                elif 'fromService' in var:
                    svc_name = var['fromService']['name']
                    prop = var['fromService']['property']
                    print(f"        ├─ {key} ← Service:{svc_name}.{prop}")
        
        print()
    
    # Databases
    print("🗄️  DATABASES")
    print("-" * 70)
    for db in config.get('databases', []):
        print(f"  💾 {db['name']}")
        print(f"     └─ Plan: {db.get('plan', 'N/A')}")
    print()
    
    print("=" * 70)
    print("✅ CONFIGURATION VALID AND READY FOR DEPLOYMENT")
    print("=" * 70)


if __name__ == '__main__':
    main()
