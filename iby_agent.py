#!/usr/bin/env python3
"""
Complete Assignment Scraper Agent - Single File Version
All functionality in one file for easy setup.
"""

import re
import time
import getpass
import json
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Optional imports (will fallback if not available)
try:
    import dateparser
except ImportError:
    dateparser = None
    print("⚠️ dateparser not installed. Using basic date parsing.")

try:
    from plyer import notification
except ImportError:
    notification = None
    print("⚠️ plyer not installed. Desktop notifications disabled.")


class AssignmentStorage:
    """Handles storing and retrieving assignment data"""
    
    def __init__(self, db_path: str = "assignments.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_url TEXT NOT NULL,
                assignment_name TEXT NOT NULL,
                due_date_raw TEXT,
                due_date_parsed TIMESTAMP,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE,
                UNIQUE(course_url, assignment_name)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def parse_due_date(self, due_date_raw: str) -> Optional[datetime]:
        """Parse due date string into datetime object"""
        if not due_date_raw or due_date_raw == "No due date found":
            return None
        
        # Clean up the due date string
        cleaned = due_date_raw.replace("Due:", "").strip()
        
        # Try dateparser first (if available)
        if dateparser:
            parsed_date = dateparser.parse(cleaned)
            if parsed_date:
                return parsed_date
        
        # Fallback: manual parsing for common formats
        try:
            # Format: "Tuesday, 19 August 2025, 12:00 AM"
            parsed_date = datetime.strptime(cleaned, "%A, %d %B %Y, %I:%M %p")
            return parsed_date
        except:
            pass
        
        try:
            # Format: "Saturday, 30 August 2025, 11:59 PM"  
            parsed_date = datetime.strptime(cleaned, "%A, %d %B %Y, %I:%M %p")
            return parsed_date
        except:
            pass
        
        return None
    
    def store_assignments(self, course_url: str, assignments: List[Dict[str, str]]) -> Dict[str, int]:
        """Store assignments in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {'new': 0, 'updated': 0, 'total': 0}
        
        for assignment in assignments:
            title = assignment.get('title', '').replace('Title: ', '')
            due_date_raw = assignment.get('due_date', 'No due date found')
            due_date_parsed = self.parse_due_date(due_date_raw)
            
            # Check if assignment already exists
            cursor.execute("""
                SELECT id FROM assignments 
                WHERE course_url = ? AND assignment_name = ?
            """, (course_url, title))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE assignments 
                    SET due_date_raw = ?, due_date_parsed = ?, extracted_at = CURRENT_TIMESTAMP
                    WHERE course_url = ? AND assignment_name = ?
                """, (due_date_raw, due_date_parsed, course_url, title))
                stats['updated'] += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO assignments 
                    (course_url, assignment_name, due_date_raw, due_date_parsed)
                    VALUES (?, ?, ?, ?)
                """, (course_url, title, due_date_raw, due_date_parsed))
                stats['new'] += 1
            
            stats['total'] += 1
        
        conn.commit()
        conn.close()
        
        return stats
    
    def get_upcoming_deadlines(self, days_ahead: int = 7) -> List[Dict]:
        """Get assignments with deadlines in next X days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        future_date = datetime.now() + timedelta(days=days_ahead)
        
        cursor.execute("""
            SELECT assignment_name, due_date_parsed, due_date_raw, course_url, notified
            FROM assignments 
            WHERE due_date_parsed IS NOT NULL 
            AND due_date_parsed BETWEEN datetime('now') AND ?
            ORDER BY due_date_parsed ASC
        """, (future_date,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'assignment_name': row[0],
                'due_date_parsed': datetime.fromisoformat(row[1]) if row[1] else None,
                'due_date_raw': row[2],
                'course_url': row[3],
                'notified': bool(row[4])
            })
        
        conn.close()
        return results
    
    def mark_as_notified(self, course_url: str, assignment_name: str):
        """Mark assignment as notified"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE assignments 
            SET notified = TRUE 
            WHERE course_url = ? AND assignment_name = ?
        """, (course_url, assignment_name))
        
        conn.commit()
        conn.close()
    
    def get_all_assignments(self) -> List[Dict]:
        """Get all stored assignments"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT assignment_name, due_date_parsed, due_date_raw, course_url, extracted_at, notified
            FROM assignments 
            ORDER BY due_date_parsed ASC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'assignment_name': row[0],
                'due_date_parsed': datetime.fromisoformat(row[1]) if row[1] else None,
                'due_date_raw': row[2],
                'course_url': row[3],
                'extracted_at': row[4],
                'notified': bool(row[5])
            })
        
        conn.close()
        return results


class NotificationSystem:
    """Handles different types of notifications"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load notification configuration"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipient_email": ""
            },
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "chat_id": ""
            },
            "desktop": {
                "enabled": True
            },
            "notification_settings": {
                "advance_days": [7, 3, 1],
                "daily_reminder_hour": 9
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    for key in default_config:
                        if key in loaded_config:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(loaded_config[key])
                            else:
                                default_config[key] = loaded_config[key]
                return default_config
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Create default config file
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✅ Created config file: {self.config_file}")
        return default_config
    
    def send_desktop_notification(self, title: str, message: str):
        """Send desktop notification"""
        if not self.config["desktop"]["enabled"] or not notification:
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10,
                app_name="Assignment Deadline Agent"
            )
            print(f"✅ Desktop notification sent: {title}")
        except Exception as e:
            print(f"❌ Desktop notification failed: {e}")
    
    def send_email(self, subject: str, body: str):
        """Send email notification"""
        if not self.config["email"]["enabled"]:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["sender_email"]
            msg['To'] = self.config["email"]["recipient_email"]
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"])
            server.starttls()
            server.login(self.config["email"]["sender_email"], self.config["email"]["sender_password"])
            
            text = msg.as_string()
            server.sendmail(self.config["email"]["sender_email"], self.config["email"]["recipient_email"], text)
            server.quit()
            
            print(f"✅ Email sent: {subject}")
        except Exception as e:
            print(f"❌ Email failed: {e}")
    
    def notify_assignment_deadline(self, assignment: Dict, days_until: int):
        """Send notification for assignment deadline"""
        name = assignment['assignment_name']
        due_date = assignment['due_date_raw']
        
        if days_until == 0:
            urgency = "📢 DUE TODAY!"
            title = "Assignment Due TODAY!"
        elif days_until == 1:
            urgency = "⚠️ Due Tomorrow!"
            title = "Assignment Due Tomorrow!"
        elif days_until <= 3:
            urgency = f"📅 Due in {days_until} days"
            title = f"Assignment Due in {days_until} days"
        else:
            urgency = f"📋 Due in {days_until} days"
            title = f"Assignment Due in {days_until} days"
        
        message = f"{urgency}\n\n📚 {name}\n🗓️ {due_date}"
        
        # Send notifications
        self.send_desktop_notification(title, name)
        
        subject = f"📚 {title}: {name}"
        self.send_email(subject, message)


class AssignmentClassifier:
    """Simple AI classifier for assignments"""
    
    def classify_text(self, text: str) -> Dict:
        """Classify text as assignment or not using heuristics"""
        text_lower = text.lower()
        
        # Assignment indicators
        assignment_indicators = [
            'assignment', 'homework', 'project', 'essay', 'lab', 
            'programming', 'coding', 'research', 'report', 'analysis'
        ]
        
        # Non-assignment indicators
        non_assignment_indicators = [
            'syllabus', 'lecture', 'quiz', 'exam', 'announcement', 
            'discussion', 'forum', 'schedule', 'calendar', 'policy',
            'introduction', 'overview', 'welcome', 'resources'
        ]
        
        assignment_score = sum(1 for indicator in assignment_indicators if indicator in text_lower)
        non_assignment_score = sum(1 for indicator in non_assignment_indicators if indicator in text_lower)
        
        is_assignment = assignment_score > non_assignment_score
        confidence = max(assignment_score, non_assignment_score) / (assignment_score + non_assignment_score + 1)
        
        return {
            'is_assignment': is_assignment,
            'confidence': confidence,
            'method': 'heuristic'
        }


class CompleteAssignmentScraper:
    """Complete assignment scraper with all functionality"""
    
    def __init__(self):
        print("🤖 Initializing Assignment Scraper Agent...")
        self.storage = AssignmentStorage()
        self.notifier = NotificationSystem()
        self.classifier = AssignmentClassifier()
        print("✅ Agent initialized successfully!")
    
    def is_valid_url(self, url: str) -> bool:
        return bool(re.match(r'https?://', url))
    
    def try_fill(self, driver, selectors, value) -> bool:
        """Try to fill form fields with given value"""
        for sel in selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    for e in elems:
                        try:
                            e.clear()
                            e.send_keys(value)
                            return True
                        except Exception:
                            continue
            except Exception:
                continue
        return False
    
    def scrape_assignments(self, url: str, username: str = None, password: str = None) -> list:
        """Scrape assignments from LMS"""
        print("🌐 Starting browser...")
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        assignments = []
        
        try:
            print("📱 Opening LMS URL...")
            driver.get(url)
            time.sleep(3)
            
            # Login if credentials provided
            if username and password:
                print("🔐 Attempting login...")
                username_selectors = [
                    'input[name="username"]', 'input[name="user"]', 'input[id*="user"]',
                    'input[name="email"]', 'input[type="email"]', 'input[id*="login"]'
                ]
                password_selectors = [
                    'input[type="password"]', 'input[name="password"]', 'input[id*="pass"]'
                ]
                
                filled_user = self.try_fill(driver, username_selectors, username)
                filled_pass = self.try_fill(driver, password_selectors, password)
                
                if filled_user and filled_pass:
                    try:
                        pw_elem = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
                        pw_elem.send_keys(Keys.RETURN)
                    except Exception:
                        try:
                            btn = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
                            btn.click()
                        except Exception:
                            pass
                    print("⏳ Waiting for login...")
                    time.sleep(5)
                    print("✅ Login completed")
                else:
                    print("⚠️ Could not find login fields")
            
            # Navigate to assignments
            print("📋 Looking for Assignments section...")
            try:
                assignments_link = driver.find_element(By.LINK_TEXT, "Assignments")
                assignments_link.click()
                time.sleep(3)
                print("✅ Navigated to Assignments")
            except Exception:
                print("⚠️ Could not find 'Assignments' link automatically")
                input("🖱️ Please click on 'Assignments' manually, then press Enter here...")
            
            # Wait for content to load
            print("⏳ Waiting for assignment content to load...")
            time.sleep(5)
            
            # Try to wait for assignment elements
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Assignment')]"))
                )
                print("✅ Assignment content detected")
            except:
                print("⚠️ Timeout waiting for assignments, continuing anyway...")
            
            # Scrape assignments using your proven method
            print("🔍 Scraping assignment data...")
            
            def normalize_title(title):
                return re.sub(r'\s+', ' ', title.strip().lower())
            
            def is_duplicate_title(title, found_set):
                normalized = normalize_title(title)
                for existing in found_set:
                    existing_normalized = normalize_title(existing)
                    if normalized == existing_normalized or normalized in existing_normalized or existing_normalized in normalized:
                        return True
                return False
            
            assignments_found = set()
            
            # Method 1: Look for assignment elements
            assignment_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Assignment') and not(contains(text(), 'Assignments'))]"
            )
            
            print(f"🔍 Found {len(assignment_elements)} potential assignment elements")
            
            for element in assignment_elements:
                try:
                    element_text = element.text.strip()
                    
                    if (not element_text or len(element_text) < 5 or
                        any(skip_word in element_text.lower() for skip_word in ['skip', 'click', 'open', 'view', 'navigate'])):
                        continue
                    
                    due_date = "No due date found"
                    title = None
                    
                    try:
                        current = element
                        for level in range(5):
                            try:
                                parent_text = current.text.strip()
                                if parent_text and 'Due:' in parent_text:
                                    lines = parent_text.split('\n')
                                    
                                    for line in lines:
                                        line = line.strip()
                                        if 'Assignment' in line and not any(word in line for word in ['Due:', 'Opened:', 'Closed:']):
                                            if len(line) > 5 and not line.startswith(('Click', 'View', 'Open', 'Navigate', 'Skip')):
                                                title = line
                                        elif line.startswith('Due:'):
                                            due_date = line
                                    
                                    if title:
                                        break
                                current = current.find_element(By.XPATH, "./parent::*")
                            except:
                                break
                    except:
                        pass
                    
                    if title and not is_duplicate_title(title, assignments_found):
                        assignments_found.add(title)
                        assignments.append({
                            'title': title,
                            'due_date': due_date
                        })
                        print(f"📚 Found: {title}")
                        
                except Exception:
                    continue
            
            # Method 2: Page source analysis (fallback)
            if len(assignments_found) == 0:
                print("🔄 Using fallback method...")
                
                all_elements = driver.find_elements(By.XPATH, "//*[text()]")
                current_assignment = None
                current_due = None
                
                for elem in all_elements:
                    text = elem.text.strip()
                    if not text:
                        continue
                        
                    if 'Assignment' in text and len(text) < 100:
                        if not any(word in text for word in ['Due:', 'Opened:', 'Closed:']):
                            current_assignment = text
                    
                    elif text.startswith('Due:') and current_assignment:
                        current_due = text
                        
                        if not is_duplicate_title(current_assignment, assignments_found):
                            assignments_found.add(current_assignment)
                            assignments.append({
                                'title': current_assignment,
                                'due_date': current_due
                            })
                            print(f"📚 Found: {current_assignment}")
                        
                        current_assignment = None
                        current_due = None
            
            print(f"✅ Scraping completed! Found {len(assignments)} assignments")
            input("🖱️ Press Enter to close browser and continue...")
            
        finally:
            driver.quit()
        
        return assignments
    
    def process_assignments(self, url: str, assignments: list):
        """Process assignments with AI classification"""
        print(f"\n🤖 Processing {len(assignments)} assignments with AI...")
        
        classified_assignments = []
        
        for assignment in assignments:
            title = assignment['title']
            
            # Classify with AI
            classification = self.classifier.classify_text(title)
            
            if classification['is_assignment']:
                classified_assignments.append(assignment)
                print(f"✅ {title} (confidence: {classification['confidence']:.2f})")
            else:
                print(f"❌ {title} - filtered out (confidence: {classification['confidence']:.2f})")
        
        # Store in database
        if classified_assignments:
            stats = self.storage.store_assignments(url, classified_assignments)
            print(f"\n💾 Storage stats: {stats}")
            
            # Check for notifications
            self.check_and_notify_deadlines()
        
        return classified_assignments
    
    def check_and_notify_deadlines(self):
        """Check for upcoming deadlines and send notifications"""
        print("\n🔔 Checking for upcoming deadlines...")
        
        upcoming = self.storage.get_upcoming_deadlines(days_ahead=30)
        
        for assignment in upcoming:
            if assignment['due_date_parsed'] and not assignment['notified']:
                days_until = (assignment['due_date_parsed'] - datetime.now()).days
                
                notification_days = self.notifier.config['notification_settings']['advance_days']
                
                if days_until in notification_days or days_until <= 1:
                    print(f"🚨 Sending notification for: {assignment['assignment_name']} (due in {days_until} days)")
                    self.notifier.notify_assignment_deadline(assignment, days_until)
                    self.storage.mark_as_notified(assignment['course_url'], assignment['assignment_name'])
    
    def show_summary(self):
        """Show summary of stored assignments"""
        print("\n📊 Assignment Summary")
        print("=" * 40)
        
        all_assignments = self.storage.get_all_assignments()
        upcoming = [a for a in all_assignments if a['due_date_parsed']]
        
        print(f"📚 Total assignments tracked: {len(all_assignments)}")
        print(f"📅 With due dates: {len(upcoming)}")
        
        if upcoming:
            print("\n🔔 Upcoming deadlines:")
            for assignment in upcoming[:5]:
                print(f"  • {assignment['assignment_name']}")
                print(f"    {assignment['due_date_raw']}")
        else:
            print("\n📭 No upcoming deadlines found")
    
    def run(self):
        """Main execution flow"""
        print("\n🚀 Assignment Deadline Agent")
        print("=" * 50)
        
        # Get course details
        url = input("📚 Enter your LMS course URL: ").strip()
        if not self.is_valid_url(url):
            print("❌ Invalid URL format")
            return
        
        username = input("👤 Enter username (or press Enter to skip): ").strip()
        password = ""
        if username:
            password = getpass.getpass("🔐 Enter password: ").strip()
        
        # Scrape assignments
        print("\n" + "="*50)
        raw_assignments = self.scrape_assignments(url, username, password)
        
        if not raw_assignments:
            print("❌ No assignments found!")
            return
        
        print(f"\n📋 Raw assignments found:")
        for i, assignment in enumerate(raw_assignments, 1):
            print(f"  {i}. {assignment['title']}")
            print(f"     {assignment['due_date']}")
        
        # Process with AI
        print("\n" + "="*50)
        final_assignments = self.process_assignments(url, raw_assignments)
        
        print(f"\n✅ Successfully processed {len(final_assignments)} assignments!")
        
        # Show summary
        self.show_summary()
        
        print("\n🎉 Assignment Agent completed successfully!")
        print("💡 Your assignments are now stored and you'll be notified of upcoming deadlines!")


if __name__ == "__main__":
    try:
        scraper = CompleteAssignmentScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Assignment Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("🔧 Try running: pip install selenium webdriver-manager dateparser plyer requests")