#!/usr/bin/env python3
"""
Rule Engine Module

Handles email rule processing and action execution.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from email_handler import EmailHandler

class RuleEngine:
    """Manages email rule processing and actions."""
    
    def __init__(self, email_handler: EmailHandler):
        self.email_handler = email_handler
    
    def process_emails(self, emails: List[Dict], rules: List[Dict]) -> Dict[str, List[str]]:
        """Process emails against defined rules."""
        results = {}
        
        for email in emails:
            applied_actions = []
            for rule in rules:
                if self._evaluate_rule(email, rule):
                    actions = self._apply_actions(email, rule['actions'])
                    applied_actions.extend(actions)
            
            if applied_actions:
                results[email['message_id']] = applied_actions
        
        return results
    
    def _evaluate_rule(self, email: Dict, rule: Dict) -> bool:
        """Evaluate if an email matches a rule's conditions."""
        conditions = rule.get('conditions', [])
        if not conditions:
            return False
        
        match_type = rule.get('match_type', 'all').lower()
        results = [self._check_condition(email, condition) for condition in conditions]
        
        return all(results) if match_type == 'all' else any(results)
    
    def _check_condition(self, email: Dict, condition: Dict) -> bool:
        """Check if an email matches a specific condition."""
        field = condition['field']
        operation = condition['operation']
        value = condition['value']
        
        # Map field names to database column names
        field_mapping = {
            'From': 'sender',
            'Subject': 'subject',
            'Message': 'content',
            'Date received': 'received_date'
        }
        
        if field not in field_mapping or field_mapping[field] not in email:
            return False
        
        field_value = email[field_mapping[field]]
        
        # Handle date comparisons
        if field == 'Date received':
            try:
                if not isinstance(field_value, datetime):
                    field_value = datetime.fromisoformat(field_value)
                days_old = (datetime.now() - field_value).days
                
                if operation == 'is less than':
                    return days_old < int(value)
                elif operation == 'is greater than':
                    return days_old > int(value)
            except (ValueError, TypeError):
                return False
        
        # Handle string comparisons
        field_value = str(field_value).lower()
        value = str(value).lower()
        
        if operation == 'contains':
            return value in field_value
        elif operation == 'does not contain':
            return value not in field_value
        elif operation == 'equals':
            return field_value == value
        elif operation == 'does not equal':
            return field_value != value
        
        return False
    
    def _apply_actions(self, email: Dict, actions: List[Dict]) -> List[str]:
        """Apply actions to an email."""
        applied_actions = []
        
        for action in actions:
            action_type = action['type']
            action_value = action.get('value', '')
            
            if action_type == 'Move Message':
                if self.email_handler.move_to_folder(email['message_id'], action_value.lower()):
                    applied_actions.append(f"Moved to {action_value}")
            
            elif action_type == 'Mark as Read':
                if self.email_handler.mark_as_read(email['message_id']):
                    applied_actions.append("Marked as read")
            
            elif action_type == 'Mark as Unread':
                if self.email_handler.mark_as_unread(email['message_id']):
                    applied_actions.append("Marked as unread")
        
        return applied_actions
    
    def _compare_dates(self, date_value: datetime, days: int, comparison: str) -> bool:
        """Compare dates for date-based conditions."""
        if not isinstance(date_value, datetime):
            return False
        
        reference_date = datetime.now() - timedelta(days=int(days))
        
        if comparison == 'gt':
            return date_value > reference_date
        elif comparison == 'lt':
            return date_value < reference_date
        
        return False
    
    @staticmethod
    def load_rules(rules_file: str) -> List[Dict]:
        """Load rules from a JSON file."""
        try:
            with open(rules_file, 'r') as f:
                data = json.load(f)
                return data.get('rules', [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading rules: {e}")
            return []
    
    @staticmethod
    def save_rules(rules_file: str, rules: List[Dict]) -> bool:
        """Save rules to a JSON file."""
        try:
            with open(rules_file, 'w') as f:
                json.dump({'rules': rules}, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving rules: {e}")
            return False