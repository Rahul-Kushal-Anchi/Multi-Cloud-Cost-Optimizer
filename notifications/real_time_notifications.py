#!/usr/bin/env python3
"""
AWS Cost Optimizer - Real-time Notifications System
Comprehensive notification system with WebSocket, push notifications, and multi-channel delivery
"""

import asyncio
import json
import logging
import websockets
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import boto3
import requests
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Notification types"""
    COST_SPIKE = "cost_spike"
    BUDGET_EXCEEDED = "budget_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    THRESHOLD_BREACH = "threshold_breach"
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    SYSTEM_ALERT = "system_alert"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"

@dataclass
class Notification:
    """Notification data structure"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    user_id: str
    channels: List[NotificationChannel]
    data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    delivered: bool = False
    delivery_attempts: int = 0

@dataclass
class WebSocketClient:
    """WebSocket client information"""
    websocket: websockets.WebSocketServerProtocol
    user_id: str
    subscribed_types: Set[NotificationType]
    connected_at: datetime

class RealTimeNotificationSystem:
    """Real-time notification system with WebSocket support"""
    
    def __init__(self):
        """Initialize notification system"""
        self.websocket_clients: Dict[str, WebSocketClient] = {}
        self.notification_queue = asyncio.Queue()
        self.is_running = False
        
        # AWS services
        self.sns_client = boto3.client('sns')
        self.ses_client = boto3.client('ses')
        
        # External services
        self.twilio_client = None
        self.slack_webhook_url = None
        self.teams_webhook_url = None
        
        # Database
        self.db_path = 'notifications.db'
        self.init_database()
        
        # Load configurations
        self.load_configurations()
        
        # Start background tasks
        self.start_background_tasks()
    
    def init_database(self):
        """Initialize SQLite database for notifications"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    channels TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    delivered BOOLEAN DEFAULT FALSE,
                    delivery_attempts INTEGER DEFAULT 0
                )
            ''')
            
            # Create user preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    email TEXT,
                    phone TEXT,
                    push_enabled BOOLEAN DEFAULT TRUE,
                    email_enabled BOOLEAN DEFAULT TRUE,
                    sms_enabled BOOLEAN DEFAULT FALSE,
                    slack_webhook TEXT,
                    teams_webhook TEXT,
                    custom_webhooks TEXT
                )
            ''')
            
            # Create device tokens table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_tokens (
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, token)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def load_configurations(self):
        """Load external service configurations"""
        try:
            # Twilio configuration
            twilio_sid = "your-twilio-account-sid"
            twilio_token = "your-twilio-auth-token"
            if twilio_sid and twilio_token:
                self.twilio_client = Client(twilio_sid, twilio_token)
            
            # Webhook URLs
            self.slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            self.teams_webhook_url = "https://your-company.webhook.office.com/webhookb2/YOUR-TEAMS-WEBHOOK"
            
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    def start_background_tasks(self):
        """Start background processing tasks"""
        # Start notification processor in background thread
        def run_processor():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_notifications())
        
        processor_thread = threading.Thread(target=run_processor, daemon=True)
        processor_thread.start()
        
        logger.info("Background tasks started")
    
    async def register_websocket_client(self, websocket, path):
        """Register new WebSocket client"""
        try:
            # Extract user ID from path or query parameters
            user_id = path.split('/')[-1] if '/' in path else 'anonymous'
            
            client = WebSocketClient(
                websocket=websocket,
                user_id=user_id,
                subscribed_types=set(),
                connected_at=datetime.now()
            )
            
            self.websocket_clients[user_id] = client
            logger.info(f"WebSocket client registered: {user_id}")
            
            # Send welcome message
            await self.send_websocket_message(user_id, {
                'type': 'connected',
                'message': 'Connected to AWS Cost Optimizer notifications',
                'timestamp': datetime.now().isoformat()
            })
            
            # Handle messages from client
            async for message in websocket:
                await self.handle_websocket_message(user_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling WebSocket client: {e}")
        finally:
            if user_id in self.websocket_clients:
                del self.websocket_clients[user_id]
                logger.info(f"WebSocket client disconnected: {user_id}")
    
    async def handle_websocket_message(self, user_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Subscribe to specific notification types
                types = data.get('types', [])
                for notification_type in types:
                    try:
                        self.websocket_clients[user_id].subscribed_types.add(
                            NotificationType(notification_type)
                        )
                    except ValueError:
                        logger.warning(f"Invalid notification type: {notification_type}")
                
                await self.send_websocket_message(user_id, {
                    'type': 'subscribed',
                    'types': types,
                    'timestamp': datetime.now().isoformat()
                })
                
            elif message_type == 'unsubscribe':
                # Unsubscribe from notification types
                types = data.get('types', [])
                for notification_type in types:
                    try:
                        self.websocket_clients[user_id].subscribed_types.discard(
                            NotificationType(notification_type)
                        )
                    except ValueError:
                        pass
                
                await self.send_websocket_message(user_id, {
                    'type': 'unsubscribed',
                    'types': types,
                    'timestamp': datetime.now().isoformat()
                })
                
            elif message_type == 'ping':
                # Respond to ping
                await self.send_websocket_message(user_id, {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await self.send_websocket_message(user_id, {
                'type': 'error',
                'message': 'Invalid JSON format',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def send_websocket_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket client"""
        if user_id in self.websocket_clients:
            try:
                await self.websocket_clients[user_id].websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                del self.websocket_clients[user_id]
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
    
    async def broadcast_websocket_message(self, message: Dict[str, Any], 
                                        notification_type: Optional[NotificationType] = None):
        """Broadcast message to all connected WebSocket clients"""
        if not self.websocket_clients:
            return
        
        disconnected_clients = []
        
        for user_id, client in self.websocket_clients.items():
            try:
                # Check if client is subscribed to this notification type
                if notification_type is None or notification_type in client.subscribed_types:
                    await client.websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(user_id)
            except Exception as e:
                logger.error(f"Error broadcasting to client {user_id}: {e}")
        
        # Remove disconnected clients
        for user_id in disconnected_clients:
            del self.websocket_clients[user_id]
    
    async def create_notification(self, notification: Notification) -> bool:
        """Create and queue notification"""
        try:
            # Store in database
            await self.store_notification(notification)
            
            # Add to processing queue
            await self.notification_queue.put(notification)
            
            logger.info(f"Notification queued: {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return False
    
    async def store_notification(self, notification: Notification):
        """Store notification in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notifications 
                (id, type, priority, title, message, user_id, channels, data, 
                 created_at, expires_at, delivered, delivery_attempts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notification.id,
                notification.type.value,
                notification.priority.value,
                notification.title,
                notification.message,
                notification.user_id,
                json.dumps([c.value for c in notification.channels]),
                json.dumps(notification.data),
                notification.created_at.isoformat(),
                notification.expires_at.isoformat() if notification.expires_at else None,
                notification.delivered,
                notification.delivery_attempts
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing notification: {e}")
    
    async def process_notifications(self):
        """Process notifications from queue"""
        logger.info("Notification processor started")
        
        while True:
            try:
                # Get notification from queue
                notification = await self.notification_queue.get()
                
                # Process notification
                await self.deliver_notification(notification)
                
                # Mark as processed
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
                await asyncio.sleep(1)
    
    async def deliver_notification(self, notification: Notification):
        """Deliver notification through specified channels"""
        try:
            success_count = 0
            total_channels = len(notification.channels)
            
            for channel in notification.channels:
                try:
                    if channel == NotificationChannel.WEBSOCKET:
                        await self.deliver_websocket_notification(notification)
                        success_count += 1
                    elif channel == NotificationChannel.PUSH:
                        await self.deliver_push_notification(notification)
                        success_count += 1
                    elif channel == NotificationChannel.EMAIL:
                        await self.deliver_email_notification(notification)
                        success_count += 1
                    elif channel == NotificationChannel.SMS:
                        await self.deliver_sms_notification(notification)
                        success_count += 1
                    elif channel == NotificationChannel.SLACK:
                        await self.deliver_slack_notification(notification)
                        success_count += 1
                    elif channel == NotificationChannel.TEAMS:
                        await self.deliver_teams_notification(notification)
                        success_count += 1
                    elif channel == NotificationChannel.WEBHOOK:
                        await self.deliver_webhook_notification(notification)
                        success_count += 1
                    
                    logger.info(f"Notification delivered via {channel.value}")
                    
                except Exception as e:
                    logger.error(f"Failed to deliver via {channel.value}: {e}")
            
            # Update delivery status
            notification.delivered = success_count > 0
            notification.delivery_attempts += 1
            
            # Update in database
            await self.update_notification_status(notification)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error delivering notification: {e}")
            return False
    
    async def deliver_websocket_notification(self, notification: Notification):
        """Deliver notification via WebSocket"""
        message = {
            'type': 'notification',
            'data': {
                'id': notification.id,
                'type': notification.type.value,
                'priority': notification.priority.value,
                'title': notification.title,
                'message': notification.message,
                'timestamp': notification.created_at.isoformat(),
                'data': notification.data
            }
        }
        
        await self.broadcast_websocket_message(message, notification.type)
    
    async def deliver_push_notification(self, notification: Notification):
        """Deliver push notification via SNS"""
        try:
            # Get user's device tokens
            device_tokens = await self.get_user_device_tokens(notification.user_id)
            
            for token in device_tokens:
                message = {
                    "default": notification.message,
                    "APNS": json.dumps({
                        "aps": {
                            "alert": {
                                "title": notification.title,
                                "body": notification.message
                            },
                            "badge": 1,
                            "sound": "default"
                        }
                    }),
                    "GCM": json.dumps({
                        "notification": {
                            "title": notification.title,
                            "body": notification.message
                        },
                        "data": notification.data
                    })
                }
                
                self.sns_client.publish(
                    TargetArn=token,
                    Message=json.dumps(message),
                    MessageStructure='json'
                )
                
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            raise
    
    async def deliver_email_notification(self, notification: Notification):
        """Deliver email notification via SES"""
        try:
            # Get user email
            user_email = await self.get_user_email(notification.user_id)
            
            # Create email message
            subject = f"AWS Cost Optimizer - {notification.title}"
            body = f"""
            {notification.message}
            
            Priority: {notification.priority.value.upper()}
            Time: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            
            ---
            AWS Cost Optimizer
            """
            
            # Send email via SES
            self.ses_client.send_email(
                Source='noreply@awscostoptimizer.com',
                Destination={'ToAddresses': [user_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            raise
    
    async def deliver_sms_notification(self, notification: Notification):
        """Deliver SMS notification via Twilio"""
        try:
            if not self.twilio_client:
                logger.warning("Twilio not configured, skipping SMS")
                return
            
            # Get user phone number
            user_phone = await self.get_user_phone(notification.user_id)
            
            # Send SMS
            self.twilio_client.messages.create(
                body=f"AWS Cost Alert: {notification.message}",
                from_='+1234567890',  # Your Twilio number
                to=user_phone
            )
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            raise
    
    async def deliver_slack_notification(self, notification: Notification):
        """Deliver Slack notification via webhook"""
        try:
            if not self.slack_webhook_url:
                logger.warning("Slack webhook not configured")
                return
            
            # Create Slack message
            color = self.get_priority_color(notification.priority)
            slack_message = {
                "text": notification.title,
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "Message",
                                "value": notification.message,
                                "short": False
                            },
                            {
                                "title": "Priority",
                                "value": notification.priority.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                self.slack_webhook_url,
                json=slack_message,
                timeout=10
            )
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            raise
    
    async def deliver_teams_notification(self, notification: Notification):
        """Deliver Teams notification via webhook"""
        try:
            if not self.teams_webhook_url:
                logger.warning("Teams webhook not configured")
                return
            
            # Create Teams message
            teams_message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": self.get_priority_color(notification.priority),
                "summary": notification.title,
                "sections": [
                    {
                        "activityTitle": notification.title,
                        "activitySubtitle": f"Priority: {notification.priority.value.upper()}",
                        "text": notification.message,
                        "facts": [
                            {
                                "name": "Time",
                                "value": notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        ]
                    }
                ]
            }
            
            # Send to Teams
            response = requests.post(
                self.teams_webhook_url,
                json=teams_message,
                timeout=10
            )
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Error sending Teams notification: {e}")
            raise
    
    async def deliver_webhook_notification(self, notification: Notification):
        """Deliver webhook notification"""
        try:
            # Get user's webhook URLs
            webhook_urls = await self.get_user_webhooks(notification.user_id)
            
            payload = {
                "id": notification.id,
                "type": notification.type.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "timestamp": notification.created_at.isoformat()
            }
            
            for webhook_url in webhook_urls:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            raise
    
    def get_priority_color(self, priority: NotificationPriority) -> str:
        """Get color for notification priority"""
        colors = {
            NotificationPriority.LOW: "#36a2eb",
            NotificationPriority.MEDIUM: "#ffce56",
            NotificationPriority.HIGH: "#ff6384",
            NotificationPriority.CRITICAL: "#ff0000"
        }
        return colors.get(priority, "#36a2eb")
    
    async def get_user_device_tokens(self, user_id: str) -> List[str]:
        """Get user's device tokens for push notifications"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT token FROM device_tokens WHERE user_id = ?",
                (user_id,)
            )
            
            tokens = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return tokens
            
        except Exception as e:
            logger.error(f"Error getting device tokens: {e}")
            return []
    
    async def get_user_email(self, user_id: str) -> str:
        """Get user's email address"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT email FROM user_preferences WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else "user@example.com"
            
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return "user@example.com"
    
    async def get_user_phone(self, user_id: str) -> str:
        """Get user's phone number"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT phone FROM user_preferences WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else "+1234567890"
            
        except Exception as e:
            logger.error(f"Error getting user phone: {e}")
            return "+1234567890"
    
    async def get_user_webhooks(self, user_id: str) -> List[str]:
        """Get user's webhook URLs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT custom_webhooks FROM user_preferences WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0])
            return []
            
        except Exception as e:
            logger.error(f"Error getting user webhooks: {e}")
            return []
    
    async def update_notification_status(self, notification: Notification):
        """Update notification status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET delivered = ?, delivery_attempts = ?
                WHERE id = ?
            ''', (notification.delivered, notification.delivery_attempts, notification.id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating notification status: {e}")
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server"""
        try:
            logger.info(f"Starting WebSocket server on {host}:{port}")
            
            async with websockets.serve(
                self.register_websocket_client,
                host,
                port,
                ssl=None
            ):
                self.is_running = True
                logger.info("WebSocket server started successfully")
                await asyncio.Future()  # Run forever
                
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
    
    async def create_cost_spike_alert(self, user_id: str, current_cost: float, 
                                     previous_cost: float, timeframe: str = "24 hours"):
        """Create cost spike alert"""
        percentage = ((current_cost - previous_cost) / previous_cost) * 100
        
        notification = Notification(
            id=f"cost_spike_{datetime.now().timestamp()}",
            type=NotificationType.COST_SPIKE,
            priority=NotificationPriority.HIGH,
            title="🚨 Cost Spike Alert",
            message=f"AWS costs increased by {percentage:.1f}% in the last {timeframe}. Current cost: ${current_cost:,.2f}, Previous: ${previous_cost:,.2f}",
            user_id=user_id,
            channels=[NotificationChannel.WEBSOCKET, NotificationChannel.PUSH, 
                     NotificationChannel.EMAIL, NotificationChannel.SLACK],
            data={
                "current_cost": current_cost,
                "previous_cost": previous_cost,
                "percentage": percentage,
                "timeframe": timeframe
            },
            created_at=datetime.now()
        )
        
        return await self.create_notification(notification)
    
    async def create_budget_exceeded_alert(self, user_id: str, current_spend: float, 
                                         budget: float):
        """Create budget exceeded alert"""
        percentage = ((current_spend - budget) / budget) * 100
        
        notification = Notification(
            id=f"budget_exceeded_{datetime.now().timestamp()}",
            type=NotificationType.BUDGET_EXCEEDED,
            priority=NotificationPriority.CRITICAL,
            title="💰 Budget Exceeded",
            message=f"Monthly budget exceeded by {percentage:.1f}%. Current spend: ${current_spend:,.2f}, Budget: ${budget:,.2f}",
            user_id=user_id,
            channels=[NotificationChannel.WEBSOCKET, NotificationChannel.PUSH, 
                     NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
            data={
                "current_spend": current_spend,
                "budget": budget,
                "percentage": percentage
            },
            created_at=datetime.now()
        )
        
        return await self.create_notification(notification)

async def main():
    """Main function to run real-time notification system"""
    notification_system = RealTimeNotificationSystem()
    
    # Start WebSocket server
    await notification_system.start_websocket_server()
    
    # Example usage
    await notification_system.create_cost_spike_alert(
        user_id="user123",
        current_cost=1500.0,
        previous_cost=1000.0,
        timeframe="24 hours"
    )

if __name__ == "__main__":
    asyncio.run(main())
