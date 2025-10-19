"""
Database Backup and Restore Utilities

Provides automated backup, restore, and integrity checking for SQLite database.
Includes rotation, compression, and health monitoring features.
"""

import os
import shutil
import sqlite3
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DatabaseBackupManager:
    """Manages database backups with rotation and integrity checking."""
    
    def __init__(self, db_path: str, backup_dir: str = None):
        """
        Initialize the backup manager.
        
        Args:
            db_path: Path to the SQLite database file
            backup_dir: Directory to store backups (defaults to database/backups)
        """
        self.db_path = Path(db_path)
        
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            # Default to database/backups directory
            self.backup_dir = self.db_path.parent / 'backups'
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup configuration
        self.max_backups = int(os.environ.get('MAX_DATABASE_BACKUPS', '10'))
        self.compress_backups = os.environ.get('COMPRESS_BACKUPS', 'true').lower() == 'true'
        
    def create_backup(self, backup_name: Optional[str] = None, compress: bool = None) -> Tuple[bool, str, str]:
        """
        Create a backup of the database.
        
        Args:
            backup_name: Optional custom name for the backup
            compress: Whether to compress the backup (defaults to self.compress_backups)
            
        Returns:
            Tuple of (success, message, backup_path)
        """
        try:
            if not self.db_path.exists():
                return False, f"Database file not found: {self.db_path}", ""
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if backup_name:
                filename = f"{backup_name}_{timestamp}.db"
            else:
                filename = f"backup_{timestamp}.db"
            
            backup_path = self.backup_dir / filename
            
            # Use SQLite's backup API for safe online backup
            logger.info(f"Creating database backup: {backup_path}")
            
            # Connect to source and destination databases
            source_conn = sqlite3.connect(str(self.db_path))
            dest_conn = sqlite3.connect(str(backup_path))
            
            # Perform the backup
            with dest_conn:
                source_conn.backup(dest_conn)
            
            source_conn.close()
            dest_conn.close()
            
            # Verify the backup
            if not self._verify_backup(backup_path):
                backup_path.unlink()  # Delete corrupted backup
                return False, "Backup verification failed", ""
            
            # Compress if requested
            should_compress = compress if compress is not None else self.compress_backups
            if should_compress:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    backup_path = compressed_path
            
            # Get backup size
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            # Rotate old backups
            self._rotate_backups()
            
            logger.info(f"Backup created successfully: {backup_path} ({size_mb:.2f} MB)")
            return True, f"Backup created successfully ({size_mb:.2f} MB)", str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}", exc_info=True)
            return False, f"Error creating backup: {str(e)}", ""
    
    def restore_backup(self, backup_path: str, create_backup_before_restore: bool = True) -> Tuple[bool, str]:
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to the backup file to restore
            create_backup_before_restore: Whether to backup current DB before restoring
            
        Returns:
            Tuple of (success, message)
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return False, f"Backup file not found: {backup_path}"
            
            # Create a safety backup of current database
            if create_backup_before_restore and self.db_path.exists():
                success, msg, _ = self.create_backup(backup_name="pre_restore")
                if not success:
                    logger.warning(f"Could not create pre-restore backup: {msg}")
            
            # Decompress if needed
            restore_from = backup_file
            if backup_file.suffix == '.gz':
                restore_from = self._decompress_backup(backup_file)
                if not restore_from:
                    return False, "Failed to decompress backup file"
            
            # Verify the backup before restoring
            if not self._verify_backup(restore_from):
                return False, "Backup file is corrupted or invalid"
            
            # Close all connections (this should be done by the caller)
            logger.info(f"Restoring database from: {restore_from}")
            
            # Replace the current database
            shutil.copy2(restore_from, self.db_path)
            
            # Clean up temporary decompressed file
            if restore_from != backup_file:
                restore_from.unlink()
            
            logger.info("Database restored successfully")
            return True, "Database restored successfully"
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}", exc_info=True)
            return False, f"Error restoring backup: {str(e)}"
    
    def list_backups(self) -> List[Dict]:
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        try:
            for backup_file in sorted(self.backup_dir.glob('*.db*'), reverse=True):
                stat = backup_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_mb': round(size_mb, 2),
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'compressed': backup_file.suffix == '.gz'
                })
        except Exception as e:
            logger.error(f"Error listing backups: {e}", exc_info=True)
        
        return backups
    
    def delete_backup(self, backup_path: str) -> Tuple[bool, str]:
        """
        Delete a specific backup file.
        
        Args:
            backup_path: Path to the backup file to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return False, f"Backup file not found: {backup_path}"
            
            # Ensure the file is in the backup directory
            if self.backup_dir not in backup_file.parents and backup_file.parent != self.backup_dir:
                return False, "Cannot delete files outside backup directory"
            
            backup_file.unlink()
            logger.info(f"Deleted backup: {backup_path}")
            return True, "Backup deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting backup: {e}", exc_info=True)
            return False, f"Error deleting backup: {str(e)}"
    
    def check_database_integrity(self) -> Tuple[bool, str, Dict]:
        """
        Check the integrity of the database.
        
        Returns:
            Tuple of (is_healthy, message, details)
        """
        try:
            if not self.db_path.exists():
                return False, "Database file does not exist", {}
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            # Get database statistics
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            db_size_mb = (page_count * page_size) / (1024 * 1024)
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            is_healthy = result == "ok"
            
            details = {
                'integrity_check': result,
                'size_mb': round(db_size_mb, 2),
                'table_count': table_count,
                'page_count': page_count,
                'page_size': page_size
            }
            
            message = "Database is healthy" if is_healthy else f"Database integrity issues: {result}"
            
            return is_healthy, message, details
            
        except Exception as e:
            logger.error(f"Error checking database integrity: {e}", exc_info=True)
            return False, f"Error checking integrity: {str(e)}", {}
    
    def _verify_backup(self, backup_path: Path) -> bool:
        """Verify that a backup file is valid."""
        try:
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            return result == "ok"
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """Compress a backup file using gzip."""
        try:
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Delete original uncompressed file
            backup_path.unlink()
            
            return compressed_path
        except Exception as e:
            logger.error(f"Error compressing backup: {e}")
            return None
    
    def _decompress_backup(self, compressed_path: Path) -> Optional[Path]:
        """Decompress a gzipped backup file."""
        try:
            decompressed_path = compressed_path.with_suffix('')
            
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return decompressed_path
        except Exception as e:
            logger.error(f"Error decompressing backup: {e}")
            return None
    
    def _rotate_backups(self):
        """Remove old backups to maintain max_backups limit."""
        try:
            backups = sorted(self.backup_dir.glob('*.db*'), key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Keep only the most recent max_backups
            for old_backup in backups[self.max_backups:]:
                logger.info(f"Rotating out old backup: {old_backup}")
                old_backup.unlink()
                
        except Exception as e:
            logger.error(f"Error rotating backups: {e}", exc_info=True)

