"""
Rule Version Management Engine

Handles version creation, comparison, and rollback
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import copy
import json
from deepdiff import DeepDiff

from backend.services.rules.rule_models import (
    RuleSet, RuleVersion, VersionComparison, VersionStatus,
    ChangeType, AuditTrail
)


class VersionManager:
    """Manages rule versions"""
    
    def __init__(self):
        self.versions: Dict[str, List[RuleVersion]] = {}  # ruleset_id -> versions
    
    def create_version(
        self,
        ruleset: RuleSet,
        version_name: Optional[str] = None,
        change_summary: Optional[str] = None,
        user_id: Optional[int] = None,
        parent_version_id: Optional[str] = None
    ) -> RuleVersion:
        """Create new version of ruleset"""
        
        # Get current version number
        existing_versions = self._get_versions(ruleset.ruleset_id)
        
        if not existing_versions:
            # First version
            version_number = "1.0"
            change_type = ChangeType.CREATED
        else:
            # Increment version
            latest = self._get_latest_version(ruleset.ruleset_id)
            version_number = self._increment_version(latest.version_number)
            change_type = ChangeType.MODIFIED
        
        # Create version record
        version = RuleVersion(
            version_id=f"ver_{uuid.uuid4().hex[:12]}",
            ruleset_id=ruleset.ruleset_id,
            version_number=version_number,
            version_name=version_name or f"Version {version_number}",
            ruleset_data=ruleset.dict(),
            status=VersionStatus.DRAFT,
            is_current=False,
            change_type=change_type,
            change_summary=change_summary,
            changed_by=user_id,
            changed_at=datetime.utcnow(),
            parent_version_id=parent_version_id or (latest.version_id if existing_versions else None)
        )
        
        # Store version
        if ruleset.ruleset_id not in self.versions:
            self.versions[ruleset.ruleset_id] = []
        self.versions[ruleset.ruleset_id].append(version)
        
        return version
    
    def activate_version(
        self,
        version_id: str,
        effective_date: Optional[datetime] = None,
        user_id: Optional[int] = None
    ) -> RuleVersion:
        """Activate a version"""
        version = self._find_version(version_id)
        
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        # Deactivate current version
        current = self._get_current_version(version.ruleset_id)
        if current:
            current.is_current = False
            current.status = VersionStatus.INACTIVE
        
        # Activate new version
        version.is_current = True
        version.status = VersionStatus.ACTIVE
        version.effective_date = effective_date or datetime.utcnow()
        
        return version
    
    def compare_versions(
        self,
        version1_id: str,
        version2_id: str,
        user_id: Optional[int] = None
    ) -> VersionComparison:
        """Compare two versions"""
        version1 = self._find_version(version1_id)
        version2 = self._find_version(version2_id)
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
        
        # Get rulesets
        ruleset1_data = version1.ruleset_data
        ruleset2_data = version2.ruleset_data
        
        # Compare rules
        added_rules, modified_rules, deleted_rules = self._compare_rules(
            ruleset1_data,
            ruleset2_data
        )
        
        # Get field-level changes
        field_changes = self._get_field_changes(ruleset1_data, ruleset2_data)
        
        comparison = VersionComparison(
            version1_id=version1_id,
            version1_number=version1.version_number,
            version2_id=version2_id,
            version2_number=version2.version_number,
            added_rules=added_rules,
            modified_rules=modified_rules,
            deleted_rules=deleted_rules,
            total_changes=len(added_rules) + len(modified_rules) + len(deleted_rules),
            rules_added_count=len(added_rules),
            rules_modified_count=len(modified_rules),
            rules_deleted_count=len(deleted_rules),
            field_changes=field_changes,
            compared_at=datetime.utcnow(),
            compared_by=user_id
        )
        
        return comparison
    
    def rollback_to_version(
        self,
        version_id: str,
        user_id: Optional[int] = None
    ) -> RuleSet:
        """Rollback to a previous version"""
        version = self._find_version(version_id)
        
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        # Create new version from the rollback target
        ruleset = RuleSet(**version.ruleset_data)
        
        # Create new version record
        new_version = self.create_version(
            ruleset,
            version_name=f"Rollback to {version.version_number}",
            change_summary=f"Rolled back to version {version.version_number}",
            user_id=user_id,
            parent_version_id=version_id
        )
        new_version.change_type = ChangeType.RESTORED
        
        # Activate the new version
        self.activate_version(new_version.version_id, user_id=user_id)
        
        return ruleset
    
    def get_version_history(
        self,
        ruleset_id: str,
        include_drafts: bool = True
    ) -> List[RuleVersion]:
        """Get version history for ruleset"""
        versions = self._get_versions(ruleset_id)
        
        if not include_drafts:
            versions = [v for v in versions if v.status != VersionStatus.DRAFT]
        
        # Sort by changed_at descending
        versions.sort(key=lambda v: v.changed_at, reverse=True)
        
        return versions
    
    def archive_version(
        self,
        version_id: str,
        user_id: Optional[int] = None
    ) -> RuleVersion:
        """Archive a version"""
        version = self._find_version(version_id)
        
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        if version.is_current:
            raise ValueError("Cannot archive current version")
        
        version.status = VersionStatus.ARCHIVED
        return version
    
    def create_audit_trail(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        before_state: Optional[Dict[str, Any]],
        after_state: Optional[Dict[str, Any]],
        user_id: Optional[int],
        tenant_id: int
    ) -> AuditTrail:
        """Create audit trail entry"""
        
        # Detect changed fields
        changed_fields = []
        if before_state and after_state:
            changed_fields = self._get_changed_fields(before_state, after_state)
        
        audit = AuditTrail(
            audit_id=f"audit_{uuid.uuid4().hex[:12]}",
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            action_details=f"{action.title()} {entity_type}",
            before_state=before_state,
            after_state=after_state,
            changed_fields=changed_fields,
            user_id=user_id,
            tenant_id=tenant_id,
            timestamp=datetime.utcnow()
        )
        
        return audit
    
    # ==================== HELPER METHODS ====================
    
    def _get_versions(self, ruleset_id: str) -> List[RuleVersion]:
        """Get all versions for ruleset"""
        return self.versions.get(ruleset_id, [])
    
    def _get_latest_version(self, ruleset_id: str) -> Optional[RuleVersion]:
        """Get latest version"""
        versions = self._get_versions(ruleset_id)
        if not versions:
            return None
        
        # Sort by version number
        versions.sort(key=lambda v: self._version_to_tuple(v.version_number), reverse=True)
        return versions[0]
    
    def _get_current_version(self, ruleset_id: str) -> Optional[RuleVersion]:
        """Get currently active version"""
        versions = self._get_versions(ruleset_id)
        for version in versions:
            if version.is_current:
                return version
        return None
    
    def _find_version(self, version_id: str) -> Optional[RuleVersion]:
        """Find version by ID"""
        for versions in self.versions.values():
            for version in versions:
                if version.version_id == version_id:
                    return version
        return None
    
    def _increment_version(self, version_number: str) -> str:
        """Increment version number"""
        parts = version_number.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        
        # Increment minor version
        minor += 1
        
        return f"{major}.{minor}"
    
    def _version_to_tuple(self, version_number: str) -> tuple:
        """Convert version string to tuple for comparison"""
        parts = version_number.split('.')
        return tuple(int(p) for p in parts)
    
    def _compare_rules(
        self,
        ruleset1: Dict[str, Any],
        ruleset2: Dict[str, Any]
    ) -> tuple:
        """Compare rules between two rulesets"""
        
        added_rules = []
        modified_rules = []
        deleted_rules = []
        
        # Compare each rule type
        rule_types = ['decision_rules', 'validation_rules', 'calculation_rules',
                     'routing_rules', 'pricing_rules', 'eligibility_rules', 'decision_tables']
        
        for rule_type in rule_types:
            rules1 = {r['rule_id'] if 'rule_id' in r else r.get('table_id'): r 
                     for r in ruleset1.get(rule_type, [])}
            rules2 = {r['rule_id'] if 'rule_id' in r else r.get('table_id'): r 
                     for r in ruleset2.get(rule_type, [])}
            
            # Find added rules
            for rule_id, rule in rules2.items():
                if rule_id not in rules1:
                    added_rules.append({
                        'rule_type': rule_type,
                        'rule_id': rule_id,
                        'rule_name': rule.get('rule_name') or rule.get('table_name'),
                        'rule_data': rule
                    })
            
            # Find deleted rules
            for rule_id, rule in rules1.items():
                if rule_id not in rules2:
                    deleted_rules.append({
                        'rule_type': rule_type,
                        'rule_id': rule_id,
                        'rule_name': rule.get('rule_name') or rule.get('table_name'),
                        'rule_data': rule
                    })
            
            # Find modified rules
            for rule_id in set(rules1.keys()) & set(rules2.keys()):
                if rules1[rule_id] != rules2[rule_id]:
                    modified_rules.append({
                        'rule_type': rule_type,
                        'rule_id': rule_id,
                        'rule_name': rules2[rule_id].get('rule_name') or rules2[rule_id].get('table_name'),
                        'before': rules1[rule_id],
                        'after': rules2[rule_id],
                        'changes': self._get_rule_changes(rules1[rule_id], rules2[rule_id])
                    })
        
        return added_rules, modified_rules, deleted_rules
    
    def _get_field_changes(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get field-level changes"""
        try:
            diff = DeepDiff(data1, data2, ignore_order=True)
            
            changes = []
            
            # Values changed
            if 'values_changed' in diff:
                for path, change in diff['values_changed'].items():
                    changes.append({
                        'type': 'changed',
                        'field': path,
                        'old_value': change.get('old_value'),
                        'new_value': change.get('new_value')
                    })
            
            # Items added
            if 'dictionary_item_added' in diff or 'iterable_item_added' in diff:
                added = diff.get('dictionary_item_added', []) + diff.get('iterable_item_added', [])
                for path in added:
                    changes.append({
                        'type': 'added',
                        'field': str(path)
                    })
            
            # Items removed
            if 'dictionary_item_removed' in diff or 'iterable_item_removed' in diff:
                removed = diff.get('dictionary_item_removed', []) + diff.get('iterable_item_removed', [])
                for path in removed:
                    changes.append({
                        'type': 'removed',
                        'field': str(path)
                    })
            
            return changes
        except Exception:
            # Fallback to simple comparison
            return []
    
    def _get_rule_changes(
        self,
        rule1: Dict[str, Any],
        rule2: Dict[str, Any]
    ) -> List[str]:
        """Get summary of rule changes"""
        changes = []
        
        # Compare key fields
        if rule1.get('rule_name') != rule2.get('rule_name'):
            changes.append('Name changed')
        
        if rule1.get('is_active') != rule2.get('is_active'):
            changes.append('Active status changed')
        
        if rule1.get('priority') != rule2.get('priority'):
            changes.append('Priority changed')
        
        if rule1.get('description') != rule2.get('description'):
            changes.append('Description changed')
        
        # Check for structural changes
        if json.dumps(rule1, sort_keys=True) != json.dumps(rule2, sort_keys=True):
            if 'Conditions changed' not in changes:
                changes.append('Logic modified')
        
        return changes
    
    def _get_changed_fields(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> List[str]:
        """Get list of changed field names"""
        changed = []
        
        all_keys = set(before.keys()) | set(after.keys())
        
        for key in all_keys:
            if before.get(key) != after.get(key):
                changed.append(key)
        
        return changed


# Global instance
version_manager = VersionManager()
