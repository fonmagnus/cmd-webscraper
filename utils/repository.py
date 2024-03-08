__all__ = ['Repository']
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional

class Repository:
    def __init__(self, *args, **kwargs):
        self.db_name = 'metadata.db'
        self.table_name = 'metadata'
    #end def
        
    def save_to_sqlite_driver(self, title: str, attributes: Dict[str, Any]):
        print(f'Saving metadata of {title} to local sqlite driver')
        attributes_json = json.dumps(attributes)
        conn = sqlite3.connect(f'scraped_pages/{self.db_name}')
        try:
            cursor = conn.cursor()
            self._upsert_table(cursor)
            cursor.execute(f'''
                INSERT OR REPLACE INTO {self.table_name} (title, attributes, created_at)
                VALUES (?, ?, ?)
            ''', (title, attributes_json, datetime.utcnow().isoformat()))
            conn.commit()
        except Exception as e:
            print(f'Error saving metadata to sqlite: {e}')
        finally:
            conn.close()
        #end try
    #end def
            
    def load_metadata(self, title: str) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(f'scraped_pages/{self.db_name}')
            cursor = conn.cursor()
            self._upsert_table(cursor)
            cursor.execute('SELECT attributes, created_at FROM metadata WHERE title = ? ORDER BY created_at DESC', (title,))
            result = cursor.fetchone()
            return {
                'title': title, 
                'attributes': result[0],
                'created_at': result[1],
            }
        except Exception as e:
            print(f'Error loading metadata from sqlite: {e}')
        finally:
            conn.close()
        #end try
        return None
    #end def
    
    def _upsert_table(self, cursor: sqlite3.Cursor):
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                title TEXT PRIMARY KEY,
                attributes TEXT,
                created_at TEXT
            )
        ''')
    #end def

#end class