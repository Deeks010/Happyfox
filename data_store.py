#!/usr/bin/env python3
"""
Email Data Store Manager

Handles database operations for storing and retrieving email data.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class EmailDataStore:
    """Manages email storage and retrieval operations."""
    
    def __init__(self, db_path: str = 'email_store.db'):
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    message_id TEXT PRIMARY KEY,
                    subject TEXT,
                    sender TEXT,
                    recipient TEXT,
                    received_date TIMESTAMP,
                    content TEXT,
                    is_read BOOLEAN,
                    labels TEXT
                )
            """)
            
            # Create rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    match_type TEXT,
                    conditions TEXT,
                    actions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def store_email(self, email_data: Dict) -> bool:
        """Store a new email in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO emails (
                        message_id, subject, sender, recipient,
                        received_date, content, is_read, labels
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email_data['message_id'],
                    email_data['subject'],
                    email_data['sender'],
                    email_data['recipient'],
                    email_data['received_date'],
                    email_data['content'],
                    email_data['is_read'],
                    ','.join(email_data.get('labels', []))
                ))
                return True
        except Exception as e:
            print(f"Error storing email: {e}")
            return False
    
    def get_emails(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve emails from the database."""
        query = "SELECT * FROM emails ORDER BY received_date DESC"
        if limit:
            query += f" LIMIT {limit}"
            
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_email_status(self, message_id: str, is_read: bool) -> bool:
        """Update the read status of an email."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE emails SET is_read = ? WHERE message_id = ?",
                    (is_read, message_id)
                )
                return True
        except Exception as e:
            print(f"Error updating email status: {e}")
            return False
    
    def update_email_labels(self, message_id: str, labels: List[str]) -> bool:
        """Update the labels of an email."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE emails SET labels = ? WHERE message_id = ?",
                    (','.join(labels), message_id)
                )
                return True
        except Exception as e:
            print(f"Error updating email labels: {e}")
            return False
    
    def store_rule(self, rule_data: Dict) -> bool:
        """Store a new rule in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO rules (name, match_type, conditions, actions)
                    VALUES (?, ?, ?, ?)
                """, (
                    rule_data['name'],
                    rule_data['match_type'],
                    str(rule_data['conditions']),
                    str(rule_data['actions'])
                ))
                return True
        except Exception as e:
            print(f"Error storing rule: {e}")
            return False
    
    def get_rules(self) -> List[Dict]:
        """Retrieve all rules from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rules ORDER BY created_at DESC")
            
            rules = []
            for row in cursor.fetchall():
                rule_dict = dict(row)
                try:
                    # Convert string representations back to lists/dicts
                    rule_dict['conditions'] = eval(rule_dict['conditions'])
                    rule_dict['actions'] = eval(rule_dict['actions'])
                except (SyntaxError, ValueError) as e:
                    print(f"Error parsing rule data: {e}")
                    continue
                rules.append(rule_dict)
            return rules
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM rules WHERE rule_id = ?", (rule_id,))
                return True
        except Exception as e:
            print(f"Error deleting rule: {e}")
            return False