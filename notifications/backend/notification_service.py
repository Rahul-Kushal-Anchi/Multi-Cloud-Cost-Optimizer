#!/usr/bin/env python3
"""
AWS Cost Optimizer - Real-time Notification Service
Handles push notifications, email alerts, and multi-channel delivery
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import boto3
import requests
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import websockets
import ssl

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
class NotificationTemplate:
    """Notification template"""
    type: NotificationType
    title_template: str
    message_template: str
    channels: List[NotificationChannel]
    priority: NotificationPriority

class NotificationService:
    """Real-time notification service"""
    
    def __init__(self):
        """Initialize notification service"""
        self.sns_client = boto3.client('sns')
        self.ses_client = boto3.client('ses')
        self.websocket_clients = set()
        
        # External service configurations
        self.twilio_client = None
        self.slack_webhook_url = None
        self.teams_webhook_url = None
        
        # Load configurations
        self._load_configurations()
        
        # Notification templates
        self.templates = self._load_notification_templates()
    
    def _load_configurations(self):
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
    
    def _load_notification_templates(self) -> Dict[NotificationType, NotificationTemplate]:
        """Load notification templates"""
        return {
            NotificationType.COST_SPIKE: NotificationTemplate(
                type=NotificationType.COST_SPIKE,
                title_template="🚨 Cost Spike Alert",
                message_template="AWS costs increased by {percentage}% in the last {timeframe}. Current cost: ${current_cost}, Previous: ${previous_cost}",
                channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL, NotificationChannel.SLACK],
                priority=NotificationPriority.HIGH
            ),
            NotificationType.BUDGET_EXCEEDED: NotificationTemplate(
                type=NotificationType.BUDGET_EXCEEDED,
                title_template="💰 Budget Exceeded",
                message_template="Monthly budget exceeded by {percentage}%. Current spend: ${current_spend}, Budget: ${budget}",
                channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
                priority=NotificationPriority.CRITICAL
            ),
            NotificationType.ANOMALY_DETECTED: NotificationTemplate(
                type=NotificationType.ANOMALY_DETECTED,
                title_template="🔍 Anomaly Detected",
                message_template="Unusual cost pattern detected for {service}. Anomaly score: {score}",
                channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL],
                priority=NotificationPriority.MEDIUM
            ),
            NotificationType.OPTIMIZATION_OPPORTUNITY: NotificationTemplate(
                type=NotificationType.OPTIMIZATION_OPPORTUNITY,
                title_template="💡 Optimization Opportunity",
                message_template="Potential savings of ${savings} identified for {service}. Recommendation: {recommendation}",
                channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL],
                priority=NotificationPriority.LOW
            ),
            NotificationType.DAILY_REPORT: NotificationTemplate(
                type=NotificationType.DAILY_REPORT,
                title_template="📊 Daily Cost Report",
                message_template="Daily AWS cost: ${cost}. Top services: {top_services}",
                channels=[NotificationChannel.EMAIL],
                priority=NotificationPriority.LOW
            )
        }
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification through specified channels"""
        try:
            success = True
            
            for channel in notification.channels:
                try:
                    if channel == NotificationChannel.PUSH:
                        await self._send_push_notification(notification)
                    elif channel == NotificationChannel.EMAIL:
                        await self._send_email_notification(notification)
                    elif channel == NotificationChannel.SMS:
                        await self._send_sms_notification(notification)
                    elif channel == NotificationChannel.SLACK:
                        await self._send_slack_notification(notification)
                    elif channel == NotificationChannel.TEAMS:
                        await self._send_teams_notification(notification)
                    elif channel == NotificationChannel.WEBHOOK:
                        await self._send_webhook_notification(notification)
                    
                    logger.info(f"Notification sent via {channel.value}")
                    
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.value}: {e}")
                    success = False
            
            # Update delivery status
            notification.delivered = success
            notification.delivery_attempts += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _send_push_notification(self, notification: Notification):
        """Send push notification via SNS"""
        try:
            # Get user's device tokens
            device_tokens = await self._get_user_device_tokens(notification.user_id)
            
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
    
    async def _send_email_notification(self, notification: Notification):
        """Send email notification via SES"""
        try:
            # Get user email
            user_email = await self._get_user_email(notification.user_id)
            
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
    
    async def _send_sms_notification(self, notification: Notification):
        """Send SMS notification via Twilio"""
        try:
            if not self.twilio_client:
                logger.warning("Twilio not configured, skipping SMS")
                return
            
            # Get user phone number
            user_phone = await self._get_user_phone(notification.user_id)
            
            # Send SMS
            self.twilio_client.messages.create(
                body=f"AWS Cost Alert: {notification.message}",
                from_='+1234567890',  # Your Twilio number
                to=user_phone
            )
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            raise
    
    async def _send_slack_notification(self, notification: Notification):
        """Send Slack notification via webhook"""
        try:
            if not self.slack_webhook_url:
                logger.warning("Slack webhook not configured")
                return
            
            # Create Slack message
            color = self._get_priority_color(notification.priority)
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
    
    async def _send_teams_notification(self, notification: Notification):
        """Send Teams notification via webhook"""
        try:
            if not self.teams_webhook_url:
                logger.warning("Teams webhook not configured")
                return
            
            # Create Teams message
            teams_message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": self._get_priority_color(notification.priority),
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
    
    async def _send_webhook_notification(self, notification: Notification):
        """Send webhook notification"""
        try:
            # Get user's webhook URLs
            webhook_urls = await self._get_user_webhooks(notification.user_id)
            
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
    
    def _get_priority_color(self, priority: NotificationPriority) -> str:
        """Get color for notification priority"""
        colors = {
            NotificationPriority.LOW: "#36a2eb",
            NotificationPriority.MEDIUM: "#ffce56",
            NotificationPriority.HIGH: "#ff6384",
            NotificationPriority.CRITICAL: "#ff0000"
        }
        return colors.get(priority, "#36a2eb")
    
    async def _get_user_device_tokens(self, user_id: str) -> List[str]:
        """Get user's device tokens for push notifications"""
        # Mock implementation - in real app, fetch from database
        return ["arn:aws:sns:us-east-1:123456789012:endpoint/GCM/MyApp/12345678-1234-1234-1234-123456789012"]
    
    async def _get_user_email(self, user_id: str) -> str:
        """Get user's email address"""
        # Mock implementation - in real app, fetch from database
        return "user@example.com"
    
    async def _get_user_phone(self, user_id: str) -> str:
        """Get user's phone number"""
        # Mock implementation - in real app, fetch from database
        return "+1234567890"
    
    async def _get_user_webhooks(self, user_id: str) -> List[str]:
        """Get user's webhook URLs"""
        # Mock implementation - in real app, fetch from database
        return ["https://user-webhook.example.com/notifications"]
    
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
            channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL, NotificationChannel.SLACK],
            data={
                "current_cost": current_cost,
                "previous_cost": previous_cost,
                "percentage": percentage,
                "timeframe": timeframe
            },
            created_at=datetime.now()
        )
        
        return await self.send_notification(notification)
    
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
            channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
            data={
                "current_spend": current_spend,
                "budget": budget,
                "percentage": percentage
            },
            created_at=datetime.now()
        )
        
        return await self.send_notification(notification)
    
    async def create_optimization_opportunity(self, user_id: str, service: str, 
                                            savings: float, recommendation: str):
        """Create optimization opportunity notification"""
        notification = Notification(
            id=f"optimization_{datetime.now().timestamp()}",
            type=NotificationType.OPTIMIZATION_OPPORTUNITY,
            priority=NotificationPriority.LOW,
            title="💡 Optimization Opportunity",
            message=f"Potential savings of ${savings:,.2f} identified for {service}. Recommendation: {recommendation}",
            user_id=user_id,
            channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL],
            data={
                "service": service,
                "savings": savings,
                "recommendation": recommendation
            },
            created_at=datetime.now()
        )
        
        return await self.send_notification(notification)

# WebSocket server for real-time notifications
class NotificationWebSocketServer:
    """WebSocket server for real-time notifications"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.clients = set()
    
    async def register_client(self, websocket, path):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Handle subscription to specific notification types
                pass
            elif message_type == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({'error': 'Invalid JSON'}))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def broadcast_notification(self, notification: Notification):
        """Broadcast notification to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps({
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
        })
        
        # Send to all connected clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected

async def main():
    """Main function to run notification service"""
    notification_service = NotificationService()
    websocket_server = NotificationWebSocketServer(notification_service)
    
    # Start WebSocket server
    start_server = websockets.serve(
        websocket_server.register_client,
        "localhost",
        8765,
        ssl=None
    )
    
    logger.info("Notification service started on ws://localhost:8765")
    
    # Example usage
    await notification_service.create_cost_spike_alert(
        user_id="user123",
        current_cost=1500.0,
        previous_cost=1000.0,
        timeframe="24 hours"
    )
    
    await start_server

if __name__ == "__main__":
    asyncio.run(main())
