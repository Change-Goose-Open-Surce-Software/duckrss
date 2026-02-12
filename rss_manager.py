#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckRSS - RSS Feed Manager
"""

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("Warning: feedparser not available - fetch_feed() will not work")

import requests
from datetime import datetime
from database import get_db
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
import re

class RSSManager:
    
    @staticmethod
    def create_input(user_id, name, feed_url):
        """Neuen Feed-Eingang erstellen"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inputs (user_id, name, feed_url)
            VALUES (?, ?, ?)
        ''', (user_id, name, feed_url))
        input_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return input_id
    
    @staticmethod
    def get_inputs(user_id):
        """Alle Eingänge eines Benutzers"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inputs WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        inputs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return inputs
    
    @staticmethod
    def create_output(user_id, name, description=''):
        """Neuen Feed-Ausgang erstellen"""
        slug = RSSManager._create_slug(name)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO outputs (user_id, name, slug, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, slug, description))
        output_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return output_id, slug
    
    @staticmethod
    def get_outputs(user_id):
        """Alle Ausgänge eines Benutzers"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM outputs WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        outputs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return outputs
    
    @staticmethod
    def link_input_to_output(input_id, output_id):
        """Eingang mit Ausgang verknüpfen"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO input_output_mapping (input_id, output_id)
                VALUES (?, ?)
            ''', (input_id, output_id))
            conn.commit()
        except:
            pass  # Bereits verknüpft
        conn.close()
    
    @staticmethod
    def fetch_feed(input_id):
        """Feed von URL abrufen und Items speichern"""
        if not FEEDPARSER_AVAILABLE:
            print("Error: feedparser module not available")
            return False
            
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM inputs WHERE id = ?', (input_id,))
        input_feed = dict(cursor.fetchone())
        
        try:
            feed = feedparser.parse(input_feed['feed_url'])
            
            for entry in feed.entries:
                guid = entry.get('id', entry.get('link', ''))
                if not guid:
                    guid = hashlib.md5(entry.get('title', '').encode()).hexdigest()
                
                title = entry.get('title', 'Kein Titel')
                link = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                content = entry.get('content', [{}])[0].get('value', description) if 'content' in entry else description
                author = entry.get('author', '')
                
                # Datum parsen
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                # Item speichern
                try:
                    cursor.execute('''
                        INSERT INTO feed_items (input_id, guid, title, link, description, content, author, published)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (input_id, guid, title, link, description, content, author, published))
                    item_id = cursor.lastrowid
                    
                    # Automatisch zu allen verknüpften Ausgängen hinzufügen
                    cursor.execute('''
                        INSERT INTO item_output_mapping (item_id, output_id)
                        SELECT ?, output_id FROM input_output_mapping WHERE input_id = ?
                    ''', (item_id, input_id))
                except:
                    pass  # Item existiert bereits
            
            # Last fetch aktualisieren
            cursor.execute('UPDATE inputs SET last_fetch = CURRENT_TIMESTAMP WHERE id = ?', (input_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Fehler beim Abrufen des Feeds: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def create_custom_item(user_id, title, content, output_ids):
        """Eigenen Feed-Artikel erstellen"""
        conn = get_db()
        cursor = conn.cursor()
        
        guid = hashlib.md5(f"{user_id}{title}{datetime.now()}".encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO feed_items (user_id, guid, title, content, description, is_custom, published)
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        ''', (user_id, guid, title, content, content[:200]))
        
        item_id = cursor.lastrowid
        
        # Zu Ausgängen hinzufügen
        for output_id in output_ids:
            cursor.execute('''
                INSERT INTO item_output_mapping (item_id, output_id)
                VALUES (?, ?)
            ''', (item_id, output_id))
        
        conn.commit()
        conn.close()
        return item_id
    
    @staticmethod
    def get_output_feed(slug):
        """RSS-Feed für Ausgang generieren"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM outputs WHERE slug = ?', (slug,))
        output = cursor.fetchone()
        
        if not output:
            conn.close()
            return None
        
        output = dict(output)
        
        # Items für diesen Ausgang laden
        cursor.execute('''
            SELECT fi.* FROM feed_items fi
            JOIN item_output_mapping iom ON fi.id = iom.item_id
            WHERE iom.output_id = ?
            ORDER BY fi.published DESC, fi.created_at DESC
            LIMIT 50
        ''', (output['id'],))
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return RSSManager._generate_rss_xml(output, items)
    
    @staticmethod
    def get_all_items(user_id):
        """Alle Items eines Benutzers mit Metadaten"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                fi.*,
                i.name as input_name,
                GROUP_CONCAT(o.name) as output_names
            FROM feed_items fi
            LEFT JOIN inputs i ON fi.input_id = i.id
            LEFT JOIN item_output_mapping iom ON fi.id = iom.item_id
            LEFT JOIN outputs o ON iom.output_id = o.id
            WHERE fi.user_id = ? OR fi.input_id IN (SELECT id FROM inputs WHERE user_id = ?)
            GROUP BY fi.id
            ORDER BY fi.published DESC, fi.created_at DESC
            LIMIT 100
        ''', (user_id, user_id))
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    @staticmethod
    def share_item_to_output(item_id, output_id):
        """Item zu anderem Ausgang teilen"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO item_output_mapping (item_id, output_id)
                VALUES (?, ?)
            ''', (item_id, output_id))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def _create_slug(name):
        """URL-freundlichen Slug erstellen"""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\-]', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug or 'feed'
    
    @staticmethod
    def _generate_rss_xml(output, items):
        """RSS 2.0 XML generieren - FIXED VERSION"""
        # Namespace für content:encoded registrieren
        ET.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')
        
        rss = ET.Element('rss', {'version': '2.0'})
        channel = ET.SubElement(rss, 'channel')
        
        # Sicherstellen dass description nicht None ist
        description = output.get('description') or ''
        
        ET.SubElement(channel, 'title').text = output['name']
        ET.SubElement(channel, 'description').text = description
        ET.SubElement(channel, 'link').text = f"http://localhost:5000/exit/{output['slug']}.xml"
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        ET.SubElement(channel, 'generator').text = 'DuckRSS'
        
        for item in items:
            item_elem = ET.SubElement(channel, 'item')
            
            # Title ist required
            ET.SubElement(item_elem, 'title').text = item['title'] or 'Kein Titel'
            
            # Link ist optional
            if item.get('link'):
                ET.SubElement(item_elem, 'link').text = item['link']
            
            # Description - sicherstellen dass es nicht None ist
            description_text = item.get('description') or ''
            ET.SubElement(item_elem, 'description').text = description_text
            
            # Content:encoded - mit korrektem Namespace
            if item.get('content'):
                content_elem = ET.SubElement(item_elem, '{http://purl.org/rss/1.0/modules/content/}encoded')
                content_elem.text = item['content']
            
            # Author ist optional
            if item.get('author'):
                ET.SubElement(item_elem, 'author').text = item['author']
            
            # GUID ist required
            ET.SubElement(item_elem, 'guid').text = item['guid']
            
            # PubDate ist optional
            if item.get('published'):
                try:
                    if isinstance(item['published'], str):
                        pub_date = datetime.fromisoformat(item['published'])
                    else:
                        pub_date = item['published']
                    ET.SubElement(item_elem, 'pubDate').text = pub_date.strftime('%a, %d %b %Y %H:%M:%S +0000')
                except:
                    pass  # Skip bei Fehler
        
        # XML formatieren
        xml_str = ET.tostring(rss, encoding='unicode')
        try:
            dom = minidom.parseString(xml_str)
            return dom.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
        except:
            # Fallback: unformatiert zurückgeben
            return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
