#!/usr/bin/env python3
"""
AWS Cost Optimizer - Shared Sync Manager
Handles data synchronization between online and offline states
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

class DataType(Enum):
    """Data type enumeration"""
    COST_DATA = "cost_data"
    NOTIFICATION = "notification"
    USER_PREFERENCE = "user_preference"
    ALERT = "alert"
    OPTIMIZATION = "optimization"

@dataclass
class SyncItem:
    """Sync item data structure"""
    id: str
    type: DataType
    data: Dict[str, Any]
    timestamp: datetime
    status: SyncStatus
    attempts: int = 0
    max_attempts: int = 3
    conflict_resolution: Optional[str] = None
    last_modified: Optional[datetime] = None

@dataclass
class ConflictResolution:
    """Conflict resolution data structure"""
    item_id: str
    local_version: Dict[str, Any]
    remote_version: Dict[str, Any]
    resolution_strategy: str
    resolved_data: Dict[str, Any]
    resolved_at: datetime

class SyncManager:
    """Shared sync manager for handling data synchronization"""
    
    def __init__(self, db_path: str = "sync_manager.db"):
        """Initialize sync manager"""
        self.db_path = db_path
        self.conflict_resolutions = []
        self.sync_queue = []
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for sync management"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create sync items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_items (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    conflict_resolution TEXT,
                    last_modified TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create conflict resolutions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conflict_resolutions (
                    id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    local_version TEXT NOT NULL,
                    remote_version TEXT NOT NULL,
                    resolution_strategy TEXT NOT NULL,
                    resolved_data TEXT NOT NULL,
                    resolved_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sync history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create data versions table for conflict detection
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_versions (
                    id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    version_hash TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Sync manager database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing sync manager database: {e}")
    
    def add_sync_item(self, sync_item: SyncItem) -> bool:
        """Add item to sync queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sync_items 
                (id, type, data, timestamp, status, attempts, max_attempts, 
                 conflict_resolution, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sync_item.id,
                sync_item.type.value,
                json.dumps(sync_item.data),
                sync_item.timestamp.isoformat(),
                sync_item.status.value,
                sync_item.attempts,
                sync_item.max_attempts,
                sync_item.conflict_resolution,
                sync_item.last_modified.isoformat() if sync_item.last_modified else None
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sync item added: {sync_item.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding sync item: {e}")
            return False
    
    def get_pending_sync_items(self, limit: int = 100) -> List[SyncItem]:
        """Get pending sync items"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sync_items 
                WHERE status = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (SyncStatus.PENDING.value, limit))
            
            items = []
            for row in cursor.fetchall():
                item = SyncItem(
                    id=row[0],
                    type=DataType(row[1]),
                    data=json.loads(row[2]),
                    timestamp=datetime.fromisoformat(row[3]),
                    status=SyncStatus(row[4]),
                    attempts=row[5],
                    max_attempts=row[6],
                    conflict_resolution=row[7],
                    last_modified=datetime.fromisoformat(row[8]) if row[8] else None
                )
                items.append(item)
            
            conn.close()
            return items
            
        except Exception as e:
            logger.error(f"Error getting pending sync items: {e}")
            return []
    
    def update_sync_item_status(self, item_id: str, status: SyncStatus, 
                              details: Optional[str] = None) -> bool:
        """Update sync item status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update sync item
            cursor.execute('''
                UPDATE sync_items 
                SET status = ?, attempts = attempts + 1
                WHERE id = ?
            ''', (status.value, item_id))
            
            # Add to sync history
            cursor.execute('''
                INSERT INTO sync_history 
                (id, item_id, action, status, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                item_id,
                'status_update',
                status.value,
                details,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sync item status updated: {item_id} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating sync item status: {e}")
            return False
    
    def detect_conflict(self, local_data: Dict[str, Any], 
                       remote_data: Dict[str, Any]) -> bool:
        """Detect data conflict between local and remote versions"""
        try:
            # Generate hash for both versions
            local_hash = self.generate_data_hash(local_data)
            remote_hash = self.generate_data_hash(remote_data)
            
            # Check if hashes are different
            return local_hash != remote_hash
            
        except Exception as e:
            logger.error(f"Error detecting conflict: {e}")
            return False
    
    def generate_data_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash for data"""
        try:
            # Sort data for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
            
            # Generate SHA-256 hash
            return hashlib.sha256(sorted_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating data hash: {e}")
            return ""
    
    def resolve_conflict(self, item_id: str, local_data: Dict[str, Any], 
                        remote_data: Dict[str, Any], 
                        strategy: str = "last_modified_wins") -> Dict[str, Any]:
        """Resolve data conflict using specified strategy"""
        try:
            resolved_data = None
            
            if strategy == "last_modified_wins":
                # Use the version with the most recent last_modified timestamp
                local_time = local_data.get('last_modified', '1970-01-01T00:00:00')
                remote_time = remote_data.get('last_modified', '1970-01-01T00:00:00')
                
                if datetime.fromisoformat(local_time) > datetime.fromisoformat(remote_time):
                    resolved_data = local_data
                else:
                    resolved_data = remote_data
                    
            elif strategy == "local_wins":
                # Always use local version
                resolved_data = local_data
                
            elif strategy == "remote_wins":
                # Always use remote version
                resolved_data = remote_data
                
            elif strategy == "merge":
                # Merge both versions (for specific data types)
                resolved_data = self.merge_data(local_data, remote_data)
                
            else:
                # Default to last_modified_wins
                resolved_data = self.resolve_conflict(item_id, local_data, remote_data, "last_modified_wins")
            
            # Store conflict resolution
            resolution = ConflictResolution(
                item_id=item_id,
                local_version=local_data,
                remote_version=remote_data,
                resolution_strategy=strategy,
                resolved_data=resolved_data,
                resolved_at=datetime.now()
            )
            
            self.store_conflict_resolution(resolution)
            
            logger.info(f"Conflict resolved for item {item_id} using strategy: {strategy}")
            return resolved_data
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return local_data  # Fallback to local data
    
    def merge_data(self, local_data: Dict[str, Any], 
                  remote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge local and remote data"""
        try:
            merged_data = local_data.copy()
            
            # Merge remote data, giving priority to non-null remote values
            for key, value in remote_data.items():
                if key not in merged_data or merged_data[key] is None:
                    merged_data[key] = value
                elif isinstance(value, dict) and isinstance(merged_data[key], dict):
                    # Recursively merge nested dictionaries
                    merged_data[key] = self.merge_data(merged_data[key], value)
                elif isinstance(value, list) and isinstance(merged_data[key], list):
                    # Merge lists, removing duplicates
                    merged_data[key] = list(set(merged_data[key] + value))
            
            # Update last_modified to current time
            merged_data['last_modified'] = datetime.now().isoformat()
            
            return merged_data
            
        except Exception as e:
            logger.error(f"Error merging data: {e}")
            return local_data  # Fallback to local data
    
    def store_conflict_resolution(self, resolution: ConflictResolution):
        """Store conflict resolution in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO conflict_resolutions 
                (id, item_id, local_version, remote_version, resolution_strategy, 
                 resolved_data, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                resolution.item_id,
                json.dumps(resolution.local_version),
                json.dumps(resolution.remote_version),
                resolution.resolution_strategy,
                json.dumps(resolution.resolved_data),
                resolution.resolved_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing conflict resolution: {e}")
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get sync statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get pending items count
            cursor.execute('SELECT COUNT(*) FROM sync_items WHERE status = ?', 
                          (SyncStatus.PENDING.value,))
            pending_count = cursor.fetchone()[0]
            
            # Get completed items count
            cursor.execute('SELECT COUNT(*) FROM sync_items WHERE status = ?', 
                          (SyncStatus.COMPLETED.value,))
            completed_count = cursor.fetchone()[0]
            
            # Get failed items count
            cursor.execute('SELECT COUNT(*) FROM sync_items WHERE status = ?', 
                          (SyncStatus.FAILED.value,))
            failed_count = cursor.fetchone()[0]
            
            # Get conflict count
            cursor.execute('SELECT COUNT(*) FROM conflict_resolutions')
            conflict_count = cursor.fetchone()[0]
            
            # Get last sync time
            cursor.execute('''
                SELECT MAX(timestamp) FROM sync_history 
                WHERE status = ?
            ''', (SyncStatus.COMPLETED.value,))
            last_sync = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'pending_count': pending_count,
                'completed_count': completed_count,
                'failed_count': failed_count,
                'conflict_count': conflict_count,
                'last_sync': last_sync,
                'total_items': pending_count + completed_count + failed_count
            }
            
        except Exception as e:
            logger.error(f"Error getting sync statistics: {e}")
            return {
                'pending_count': 0,
                'completed_count': 0,
                'failed_count': 0,
                'conflict_count': 0,
                'last_sync': None,
                'total_items': 0
            }
    
    def cleanup_old_sync_items(self, days: int = 30):
        """Clean up old completed sync items"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old completed items
            cursor.execute('''
                DELETE FROM sync_items 
                WHERE status = ? AND timestamp < ?
            ''', (SyncStatus.COMPLETED.value, cutoff_date.isoformat()))
            
            deleted_count = cursor.rowcount
            
            # Delete old sync history
            cursor.execute('''
                DELETE FROM sync_history 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old sync items")
            
        except Exception as e:
            logger.error(f"Error cleaning up old sync items: {e}")
    
    def get_sync_history(self, item_id: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Get sync history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if item_id:
                cursor.execute('''
                    SELECT * FROM sync_history 
                    WHERE item_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (item_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM sync_history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'item_id': row[1],
                    'action': row[2],
                    'status': row[3],
                    'details': row[4],
                    'timestamp': row[5]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"Error getting sync history: {e}")
            return []
    
    def retry_failed_sync_items(self, max_attempts: int = 3):
        """Retry failed sync items"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get failed items that haven't exceeded max attempts
            cursor.execute('''
                SELECT * FROM sync_items 
                WHERE status = ? AND attempts < max_attempts
            ''', (SyncStatus.FAILED.value,))
            
            failed_items = cursor.fetchall()
            
            for item in failed_items:
                # Reset status to pending for retry
                cursor.execute('''
                    UPDATE sync_items 
                    SET status = ? 
                    WHERE id = ?
                ''', (SyncStatus.PENDING.value, item[0]))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Reset {len(failed_items)} failed items for retry")
            
        except Exception as e:
            logger.error(f"Error retrying failed sync items: {e}")

# Example usage
if __name__ == "__main__":
    # Create sync manager
    sync_manager = SyncManager()
    
    # Add sync item
    sync_item = SyncItem(
        id="test_item_1",
        type=DataType.COST_DATA,
        data={"cost": 100.0, "service": "EC2", "date": "2025-01-01"},
        timestamp=datetime.now(),
        status=SyncStatus.PENDING
    )
    
    sync_manager.add_sync_item(sync_item)
    
    # Get statistics
    stats = sync_manager.get_sync_statistics()
    print(f"Sync statistics: {stats}")
    
    # Cleanup old items
    sync_manager.cleanup_old_sync_items(days=30)
