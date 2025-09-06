#!/usr/bin/env python3
"""
Database Manager for Network Scanner Application
Handles SQLite database operations for scan sessions, results, and bookmarks
"""

import aiosqlite
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: str = "network_scanner.db"):
        self.db_path = db_path
        
    async def init_database(self):
        """Initialize the database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create scan_sessions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scan_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    ports TEXT,
                    status TEXT DEFAULT 'running',
                    total_hosts INTEGER DEFAULT 0,
                    hosts_up INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Create scan_results table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    host TEXT NOT NULL,
                    status TEXT NOT NULL,
                    ports TEXT,
                    os_info TEXT,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES scan_sessions (id)
                )
            """)
            
            # Create bookmarks table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    scan_type TEXT DEFAULT 'quick',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    async def create_scan_session(self, target: str, scan_type: str, ports: Optional[str] = None) -> int:
        """Create a new scan session and return its ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO scan_sessions (target, scan_type, ports) VALUES (?, ?, ?)",
                (target, scan_type, ports)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def update_scan_session(self, session_id: int, status: str, total_hosts: int, hosts_up: int):
        """Update scan session status and statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            completed_at = datetime.now().isoformat() if status in ['completed', 'stopped', 'error'] else None
            await db.execute(
                """UPDATE scan_sessions 
                   SET status = ?, total_hosts = ?, hosts_up = ?, completed_at = ?
                   WHERE id = ?""",
                (status, total_hosts, hosts_up, completed_at, session_id)
            )
            await db.commit()
    
    async def save_scan_result(self, session_id: int, result: Dict[str, Any]):
        """Save a scan result for a specific session"""
        async with aiosqlite.connect(self.db_path) as db:
            ports_json = json.dumps(result.get('ports', []))
            await db.execute(
                """INSERT INTO scan_results (session_id, host, status, ports, os_info)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, result['host'], result['status'], ports_json, result.get('os_info'))
            )
            await db.commit()
    
    async def get_scan_sessions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scan sessions with pagination"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM scan_sessions 
                   ORDER BY created_at DESC 
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_scan_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific scan session by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM scan_sessions WHERE id = ?",
                (session_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_scan_results(self, session_id: int) -> List[Dict[str, Any]]:
        """Get all scan results for a specific session"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM scan_results WHERE session_id = ? ORDER BY scan_time",
                (session_id,)
            )
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                # Parse ports JSON
                try:
                    result['ports'] = json.loads(result['ports']) if result['ports'] else []
                except json.JSONDecodeError:
                    result['ports'] = []
                results.append(result)
            return results
    
    async def delete_scan_session(self, session_id: int) -> bool:
        """Delete a scan session and its results"""
        async with aiosqlite.connect(self.db_path) as db:
            # Delete results first (foreign key constraint)
            await db.execute("DELETE FROM scan_results WHERE session_id = ?", (session_id,))
            # Delete session
            cursor = await db.execute("DELETE FROM scan_sessions WHERE id = ?", (session_id,))
            await db.commit()
            return cursor.rowcount > 0
    
    async def search_hosts(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for hosts in scan results"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT DISTINCT sr.host, sr.status, sr.os_info, sr.scan_time,
                          ss.target, ss.scan_type
                   FROM scan_results sr
                   JOIN scan_sessions ss ON sr.session_id = ss.id
                   WHERE sr.host LIKE ? OR sr.os_info LIKE ?
                   ORDER BY sr.scan_time DESC
                   LIMIT ?""",
                (f"%{query}%", f"%{query}%", limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total sessions
            cursor = await db.execute("SELECT COUNT(*) FROM scan_sessions")
            total_sessions = (await cursor.fetchone())[0]
            
            # Total hosts scanned
            cursor = await db.execute("SELECT COUNT(DISTINCT host) FROM scan_results")
            total_hosts = (await cursor.fetchone())[0]
            
            # Hosts up
            cursor = await db.execute("SELECT COUNT(DISTINCT host) FROM scan_results WHERE status = 'up'")
            hosts_up = (await cursor.fetchone())[0]
            
            # Recent sessions (last 7 days)
            cursor = await db.execute(
                "SELECT COUNT(*) FROM scan_sessions WHERE created_at >= datetime('now', '-7 days')"
            )
            recent_sessions = (await cursor.fetchone())[0]
            
            return {
                'total_sessions': total_sessions,
                'total_hosts': total_hosts,
                'hosts_up': hosts_up,
                'recent_sessions': recent_sessions
            }
    
    async def get_bookmarks(self) -> List[Dict[str, Any]]:
        """Get all bookmarks"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM bookmarks ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def create_bookmark(self, name: str, target: str, description: str = "", scan_type: str = "quick") -> int:
        """Create a new bookmark"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO bookmarks (name, target, description, scan_type) VALUES (?, ?, ?, ?)",
                (name, target, description, scan_type)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def update_bookmark(self, bookmark_id: int, name: str, target: str, description: str = "", scan_type: str = "quick") -> bool:
        """Update an existing bookmark"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "UPDATE bookmarks SET name = ?, target = ?, description = ?, scan_type = ? WHERE id = ?",
                (name, target, description, scan_type, bookmark_id)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
            await db.commit()
            return cursor.rowcount > 0

# Create global database manager instance
db_manager = DatabaseManager()