"""
Seed script for default tenant and admin user
Creates:
- Default tenant
- Admin role with all permissions
- Default admin user
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from backend.shared.database.connection import AsyncSessionLocal
from backend.shared.database.models import Tenant, User, Role, Permission, UserRole, RolePermission
from backend.shared.common.security import hash_password
import uuid
from datetime import datetime


async def seed_default_tenant():
    """Create default tenant"""
    async with AsyncSessionLocal() as session:
        # Check if default tenant exists
        result = await session.execute(
            select(Tenant).where(Tenant.id == "default")
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            print("✓ Default tenant already exists")
            return tenant
        
        # Create default tenant
        tenant = Tenant(
            id="default",
            name="Default Organization",
            display_name="Default NBFC",
            email="admin@default.nbfc",
            phone="+91-9876543210",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            country="India",
            is_active=True,
            is_trial=False,
            subscription_plan="enterprise",
            subscription_status="active",
            max_users=100,
            max_branches=50,
            max_customers=100000,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(tenant)
        await session.commit()
        print("✓ Created default tenant")
        return tenant


async def seed_permissions():
    """Create default permissions"""
    async with AsyncSessionLocal() as session:
        tenant_id = "default"
        
        # Define core permissions
        resources = [
            ('users', 'User Management'),
            ('roles', 'Role Management'),
            ('permissions', 'Permission Management'),
            ('customers', 'Customer Management'),
            ('loans', 'Loan Management'),
            ('collections', 'Collection Management'),
            ('deposits', 'Deposit Management'),
            ('reports', 'Reports'),
            ('settings', 'System Settings'),
        ]
        
        actions = ['create', 'read', 'update', 'delete', 'export']
        
        permissions_created = 0
        
        for resource, description in resources:
            for action in actions:
                # Check if permission exists
                result = await session.execute(
                    select(Permission).where(
                        Permission.tenant_id == tenant_id,
                        Permission.resource == resource,
                        Permission.action == action
                    )
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    permission = Permission(
                        id=uuid.uuid4(),
                        tenant_id=tenant_id,
                        resource=resource,
                        action=action,
                        description=f"{action.capitalize()} {description}",
                        permission_type="entity",
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(permission)
                    permissions_created += 1
        
        await session.commit()
        print(f"✓ Created {permissions_created} permissions")


async def seed_admin_role():
    """Create admin role with all permissions"""
    async with AsyncSessionLocal() as session:
        tenant_id = "default"
        
        # Check if admin role exists
        result = await session.execute(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.name == "admin"
            )
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            admin_role = Role(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                name="admin",
                display_name="System Administrator",
                description="Full system access with all permissions",
                role_type="system",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin_role)
            await session.flush()
            print("✓ Created admin role")
        else:
            print("✓ Admin role already exists")
        
        # Assign all permissions to admin role
        result = await session.execute(
            select(Permission).where(Permission.tenant_id == tenant_id)
        )
        permissions = result.scalars().all()
        
        permissions_assigned = 0
        for permission in permissions:
            # Check if already assigned
            result = await session.execute(
                select(RolePermission).where(
                    RolePermission.tenant_id == tenant_id,
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                role_permission = RolePermission(
                    id=uuid.uuid4(),
                    tenant_id=tenant_id,
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    assigned_at=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(role_permission)
                permissions_assigned += 1
        
        await session.commit()
        print(f"✓ Assigned {permissions_assigned} permissions to admin role")
        return admin_role


async def seed_admin_user(admin_role):
    """Create default admin user"""
    async with AsyncSessionLocal() as session:
        tenant_id = "default"
        
        # Check if admin user exists
        result = await session.execute(
            select(User).where(
                User.tenant_id == tenant_id,
                User.username == "admin"
            )
        )
        admin_user = result.scalar_one_or_none()
        
        if admin_user:
            print("✓ Admin user already exists")
            return admin_user
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="admin@nbfcsuite.com",
            username="admin",
            password_hash=hash_password("admin123"),  # Default password
            first_name="System",
            last_name="Administrator",
            phone="+91-9876543210",
            employee_code="EMP001",
            designation="System Administrator",
            department="IT",
            is_active=True,
            is_superuser=True,
            is_verified=True,
            email_verified=True,
            phone_verified=True,
            language="en",
            timezone="Asia/Kolkata",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(admin_user)
        await session.flush()
        print("✓ Created admin user (username: admin, password: admin123)")
        
        # Assign admin role to user
        user_role = UserRole(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=admin_user.id,
            role_id=admin_role.id,
            assigned_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(user_role)
        
        await session.commit()
        print("✓ Assigned admin role to admin user")
        return admin_user


async def main():
    """Run all seed scripts"""
    print("=" * 50)
    print("  Seeding Default Tenant and Admin User")
    print("=" * 50)
    print()
    
    try:
        # Create default tenant
        await seed_default_tenant()
        
        # Create permissions
        await seed_permissions()
        
        # Create admin role
        admin_role = await seed_admin_role()
        
        # Create admin user
        await seed_admin_user(admin_role)
        
        print()
        print("=" * 50)
        print("  ✓ Seeding Complete!")
        print("=" * 50)
        print()
        print("Login Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        print("⚠️  Please change the default password after first login!")
        print()
        
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
