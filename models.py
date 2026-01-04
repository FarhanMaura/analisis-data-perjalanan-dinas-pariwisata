"""
Database models for multi-role authentication system
"""
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """User model for authentication"""
    
    def __init__(self, id, username, password_hash, role, email, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'hotel', 'tourism'
        self.email = email
        self.created_at = created_at or datetime.now()
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create(db_path, username, password, role, email):
        """Create new user"""
        password_hash = generate_password_hash(password)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, role, email))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    @staticmethod
    def get_by_id(db_path, user_id):
        """Get user by ID"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=row['role'],
                email=row['email'],
                created_at=row['created_at']
            )
        return None
    
    @staticmethod
    def get_by_username(db_path, username):
        """Get user by username"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=row['role'],
                email=row['email'],
                created_at=row['created_at']
            )
        return None
    
    @staticmethod
    def get_all(db_path):
        """Get all users"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at ASC')
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                'id': row['id'],
                'username': row['username'],
                'role': row['role'],
                'email': row['email'],
                'created_at': row['created_at']
            })
        return users
    
    @staticmethod
    def update(db_path, user_id, username=None, email=None, password=None, role=None):
        """Update user"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if username:
            updates.append('username = ?')
            params.append(username)
        if email:
            updates.append('email = ?')
            params.append(email)
        if password:
            updates.append('password_hash = ?')
            params.append(generate_password_hash(password))
        if role:
            updates.append('role = ?')
            params.append(role)
        
        if updates:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    @staticmethod
    def delete(db_path, user_id):
        """Delete user"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()


class HotelData:
    """Hotel data model"""
    
    @staticmethod
    def get_hotel_info(db_path, user_id):
        """Get hotel info for user"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT hotel_name, total_rooms 
            FROM hotel_info 
            WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'hotel_name': row['hotel_name'],
                'total_rooms': row['total_rooms']
            }
        return None
    
    @staticmethod
    def set_hotel_info(db_path, user_id, hotel_name, total_rooms):
        """Set hotel info for user"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute('SELECT id FROM hotel_info WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE hotel_info 
                SET hotel_name = ?, total_rooms = ?
                WHERE user_id = ?
            ''', (hotel_name, total_rooms, user_id))
        else:
            cursor.execute('''
                INSERT INTO hotel_info (user_id, hotel_name, total_rooms)
                VALUES (?, ?, ?)
            ''', (user_id, hotel_name, total_rooms))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def add_daily_data(db_path, user_id, date, occupied_rooms):
        """Add daily hotel data"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hotel_data (user_id, date, occupied_rooms)
            VALUES (?, ?, ?)
        ''', (user_id, date, occupied_rooms))
        conn.commit()
        conn.close()
    
    @staticmethod
    def check_date_exists(db_path, user_id, date):
        """Check if data exists for date"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM hotel_data 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        exists = cursor.fetchone()
        conn.close()
        return exists is not None
    
    @staticmethod
    def get_all_data(db_path, user_id):
        """Get all hotel data for user"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM hotel_data 
            WHERE user_id = ?
            ORDER BY date DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'date': row['date'],
                'occupied_rooms': row['occupied_rooms'],
                'guest_count': row['guest_count'],
                'created_at': row['created_at']
            })
        return data
    
    @staticmethod
    def update_occupied_rooms(db_path, data_id, occupied_rooms):
        """Update occupied rooms for a record"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE hotel_data 
            SET occupied_rooms = ?
            WHERE id = ?
        ''', (occupied_rooms, data_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all_hotels_data(db_path):
        """Get all hotel data from all users (for admin)"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT hd.*, hi.hotel_name, u.username
            FROM hotel_data hd
            JOIN hotel_info hi ON hd.user_id = hi.user_id
            JOIN users u ON hd.user_id = u.id
            ORDER BY hd.date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'hotel_name': row['hotel_name'],
                'username': row['username'],
                'date': row['date'],
                'occupied_rooms': row['occupied_rooms'],
                'guest_count': row['guest_count'],
                'created_at': row['created_at']
            })
        return data


class TourismData:
    """Tourism data model"""
    
    @staticmethod
    def add_data(db_path, user_id, date, origin, total_visitors, male_adult, female_adult, male_child, female_child):
        """Add tourism data"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tourism_data 
            (user_id, date, origin, total_visitors, male_adult, female_adult, male_child, female_child)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, origin, total_visitors, male_adult, female_adult, male_child, female_child))
        conn.commit()
        conn.close()
    
    @staticmethod
    def check_date_exists(db_path, user_id, date):
        """Check if data exists for date"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM tourism_data 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        exists = cursor.fetchone()
        conn.close()
        return exists is not None
    
    @staticmethod
    def get_all_data(db_path, user_id):
        """Get all tourism data for user"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tourism_data 
            WHERE user_id = ?
            ORDER BY date DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'date': row['date'],
                'origin': row['origin'],
                'total_visitors': row['total_visitors'],
                'male_adult': row['male_adult'],
                'female_adult': row['female_adult'],
                'male_child': row['male_child'],
                'female_child': row['female_child'],
                'created_at': row['created_at']
            })
        return data
    
    @staticmethod
    def update_data(db_path, data_id, origin=None, total_visitors=None, male_adult=None, female_adult=None, male_child=None, female_child=None):
        """Update tourism data"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if origin is not None:
            updates.append('origin = ?')
            params.append(origin)
        if total_visitors is not None:
            updates.append('total_visitors = ?')
            params.append(total_visitors)
        if male_adult is not None:
            updates.append('male_adult = ?')
            params.append(male_adult)
        if female_adult is not None:
            updates.append('female_adult = ?')
            params.append(female_adult)
        if male_child is not None:
            updates.append('male_child = ?')
            params.append(male_child)
        if female_child is not None:
            updates.append('female_child = ?')
            params.append(female_child)
        
        if updates:
            params.append(data_id)
            query = f"UPDATE tourism_data SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    @staticmethod
    def get_all_tourism_data(db_path):
        """Get all tourism data from all users (for admin)"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT td.*, u.username
            FROM tourism_data td
            JOIN users u ON td.user_id = u.id
            ORDER BY td.date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'username': row['username'],
                'date': row['date'],
                'origin': row['origin'],
                'total_visitors': row['total_visitors'],
                'male_adult': row['male_adult'],
                'female_adult': row['female_adult'],
                'male_child': row['male_child'],
                'female_child': row['female_child'],
                'created_at': row['created_at']
            })
        return data
