"""
Database Manager for Smart Attendance System
Handles SQLite database operations with connection pooling
"""

import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime, date
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for attendance system"""
    
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Persons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
                    person_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Attendance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (person_id) REFERENCES persons(person_id),
                    UNIQUE(person_id, date)
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_attendance_date 
                ON attendance(date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_attendance_person 
                ON attendance(person_id)
            """)
            
            logger.info("Database initialized successfully")
    
    def add_person(self, person_id: str, name: str) -> bool:
        """Add a new person to the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO persons (person_id, name) VALUES (?, ?)",
                    (person_id, name)
                )
                logger.info(f"Added person: {person_id} - {name}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Person {person_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error adding person: {str(e)}")
            return False
    
    def person_exists(self, person_id: str) -> bool:
        """Check if a person exists in the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM persons WHERE person_id = ?",
                    (person_id,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Error checking person existence: {str(e)}")
            return False
    
    def mark_attendance(
        self, 
        person_id: str, 
        name: str, 
        date: str, 
        time: str
    ) -> bool:
        """
        Mark attendance for a person
        Prevents duplicate entries for the same day
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO attendance (person_id, name, date, time) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (person_id, name, date, time)
                )
                logger.info(f"Attendance marked: {person_id} - {name} at {time} on {date}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Attendance already marked for {person_id} on {date}")
            return False
        except Exception as e:
            logger.error(f"Error marking attendance: {str(e)}")
            return False
    
    def has_attendance_today(self, person_id: str, date: str) -> bool:
        """Check if attendance is already marked for today"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM attendance WHERE person_id = ? AND date = ?",
                    (person_id, date)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Error checking attendance: {str(e)}")
            return False
    
    def get_attendance(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        person_id: Optional[str] = None
    ) -> List[Tuple]:
        """
        Get attendance records with optional filtering
        Returns: List of tuples (id, person_id, name, date, time)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT id, person_id, name, date, time FROM attendance WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)
                
                if person_id:
                    query += " AND person_id = ?"
                    params.append(person_id)
                
                query += " ORDER BY date DESC, time DESC"
                
                cursor.execute(query, params)
                records = cursor.fetchall()
                
                return records
        except Exception as e:
            logger.error(f"Error getting attendance: {str(e)}")
            return []
    
    def get_all_persons(self) -> List[Tuple]:
        """Get all registered persons"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT person_id, name FROM persons ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting persons: {str(e)}")
            return []
    
    def delete_person(self, person_id: str) -> bool:
        """Delete a person and their attendance records"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Delete attendance records first
                cursor.execute("DELETE FROM attendance WHERE person_id = ?", (person_id,))
                # Delete person
                cursor.execute("DELETE FROM persons WHERE person_id = ?", (person_id,))
                logger.info(f"Deleted person: {person_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting person: {str(e)}")
            return False
    
    def get_attendance_stats(self) -> dict:
        """Get attendance statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total persons
                cursor.execute("SELECT COUNT(*) FROM persons")
                stats['total_persons'] = cursor.fetchone()[0]
                
                # Total attendance records
                cursor.execute("SELECT COUNT(*) FROM attendance")
                stats['total_records'] = cursor.fetchone()[0]
                
                # Today's attendance
                today = date.today().isoformat()
                cursor.execute(
                    "SELECT COUNT(*) FROM attendance WHERE date = ?",
                    (today,)
                )
                stats['today_count'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
