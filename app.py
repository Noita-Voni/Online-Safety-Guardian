from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, render_template_string
import pandas as pd
import re
from colorama import Fore  # Only for console output, not used in web
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
import json
from collections import Counter
import numpy as np
import uuid
import hashlib
import time
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps

# Initialize NLTK and download the lexicon if necessary
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Enhanced Flask configuration for better session security
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

# =============================================================================
# ADMIN AUTHENTICATION SYSTEM
# =============================================================================

# Admin credentials (CHANGE THESE FOR PRODUCTION!)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ThreatSense2025!')  # Change this!

def admin_required(f):
    """Enhanced decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in as admin
        if not session.get('admin_logged_in'):
            flash('Access denied. Please log in as administrator.', 'error')
            return redirect(url_for('admin_login'))
        
        # Optional: Check if admin user exists and is valid
        admin_user = session.get('admin_user')
        if not admin_user or admin_user != ADMIN_USERNAME:
            session.clear()  # Clear invalid session
            flash('Invalid admin session. Please log in again.', 'error')
            return redirect(url_for('admin_login'))
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            
            # Log successful admin login
            audit_logger.log_event(
                event_type=EventType.USER_SESSION,
                severity=EventSeverity.MEDIUM,
                action="Admin login successful",
                resource="admin_panel",
                user_id=f"admin_{username}",
                details={'login_method': 'password_auth'}
            )
            
            flash('Successfully logged in as administrator', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            # Log failed login attempt
            audit_logger.log_event(
                event_type=EventType.ERROR_OCCURRED,
                severity=EventSeverity.HIGH,
                action="Failed admin login attempt",
                resource="admin_panel",
                outcome="error",
                details={
                    'attempted_username': username,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'unknown')
                }
            )
            
            flash('Invalid username or password', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Admin Access - ThreatSense Analytics</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Arial', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
            max-width: 400px;
            width: 100%;
        }
        .login-header {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .login-body {
            padding: 30px 20px;
        }
        .form-group label {
            font-weight: 600;
            color: #333;
        }
        .form-control {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            padding: 12px 15px;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #007bff;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }
        .btn-login {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4);
        }
        .alert {
            border-radius: 8px;
            border: none;
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #6c757d;
            text-decoration: none;
            font-size: 0.9rem;
        }
        .back-link a:hover {
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h2><i class="fas fa-shield-alt"></i> Admin Access</h2>
            <p class="mb-0">ThreatSense Analytics Control Panel</p>
        </div>
        <div class="login-body">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                            <i class="fas fa-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' }}"></i>
                            {{ message }}
                            <button type="button" class="close" data-dismiss="alert">
                                <span>&times;</span>
                            </button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="post">
                <div class="form-group">
                    <label for="username">
                        <i class="fas fa-user"></i> Username
                    </label>
                    <input type="text" 
                           class="form-control" 
                           id="username" 
                           name="username" 
                           required 
                           autocomplete="username"
                           placeholder="Enter admin username">
                </div>
                
                <div class="form-group">
                    <label for="password">
                        <i class="fas fa-lock"></i> Password
                    </label>
                    <input type="password" 
                           class="form-control" 
                           id="password" 
                           name="password" 
                           required 
                           autocomplete="current-password"
                           placeholder="Enter admin password">
                </div>
                
                <button type="submit" class="btn btn-primary btn-login btn-block">
                    <i class="fas fa-sign-in-alt"></i> Secure Login
                </button>
            </form>
            
            <div class="back-link">
                <a href="{{ url_for('index') }}">
                    <i class="fas fa-arrow-left"></i> Back to Threat Analysis
                </a>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    admin_user = session.get('admin_user', 'unknown')
    
    # Log admin logout
    audit_logger.log_event(
        event_type=EventType.USER_SESSION,
        severity=EventSeverity.LOW,
        action="Admin logout",
        resource="admin_panel",
        user_id=f"admin_{admin_user}",
        details={'logout_method': 'manual'}
    )
    
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))

# Debug and utility routes
@app.route('/admin/force-logout')
def force_logout():
    """Force logout - clears all session data"""
    session.clear()
    flash('All sessions cleared', 'success')
    return redirect(url_for('index'))

@app.route('/debug/session')
def debug_session():
    """Debug session status - REMOVE IN PRODUCTION"""
    return jsonify({
        'admin_logged_in': session.get('admin_logged_in', False),
        'admin_user': session.get('admin_user', 'None'),
        'session_id': session.get('session_id', 'None'),
        'all_session_data': dict(session)
    })

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with overview"""
    try:
        # Get recent audit statistics
        log_file = audit_logger.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        total_events = 0
        threat_events = 0
        error_events = 0
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        total_events += 1
                        if log_entry.get('event_type') == 'threat_detected':
                            threat_events += 1
                        elif log_entry.get('event_type') == 'error_occurred':
                            error_events += 1
                    except json.JSONDecodeError:
                        continue
        
        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Admin Dashboard - ThreatSense Analytics</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background: #f8f9fa; font-family: Arial, sans-serif; }
        .header { background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 20px 0; margin-bottom: 30px; }
        .stat-card { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .stat-number { font-size: 2rem; font-weight: bold; }
        .btn-custom { margin: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1><i class="fas fa-shield-alt"></i> Admin Dashboard</h1>
            <p class="mb-0">ThreatSense Analytics Control Panel</p>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <i class="fas fa-file-alt fa-2x text-primary mb-2"></i>
                    <div class="stat-number text-primary">{{ total_events }}</div>
                    <div>Total Events Today</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                    <div class="stat-number text-warning">{{ threat_events }}</div>
                    <div>Threats Detected</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <i class="fas fa-users fa-2x text-success mb-2"></i>
                    <div class="stat-number text-success">{{ active_sessions }}</div>
                    <div>Active Sessions</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <i class="fas fa-times-circle fa-2x text-danger mb-2"></i>
                    <div class="stat-number text-danger">{{ error_events }}</div>
                    <div>System Errors</div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="stat-card">
                    <h3><i class="fas fa-tools"></i> Admin Tools</h3>
                    <div class="row">
                        <div class="col-md-6">
                            <a href="/admin/audit-logs" class="btn btn-primary btn-block btn-custom" target="_blank">
                                <i class="fas fa-file-text"></i> View Audit Logs
                            </a>
                            <a href="/admin/session-info" class="btn btn-info btn-block btn-custom" target="_blank">
                                <i class="fas fa-users"></i> Active Sessions
                            </a>
                        </div>
                        <div class="col-md-6">
                            <a href="{{ url_for('index') }}" class="btn btn-secondary btn-block btn-custom">
                                <i class="fas fa-chart-line"></i> Back to Analysis
                            </a>
                            <a href="/admin/logout" class="btn btn-outline-danger btn-block btn-custom">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        ''', 
        total_events=total_events,
        threat_events=threat_events,
        error_events=error_events,
        active_sessions=len(audit_logger.active_sessions)
        )
        
    except Exception as e:
        audit_logger.log_error("ADMIN_DASHBOARD_ERROR", str(e))
        return f"Dashboard error: {str(e)}", 500

# =============================================================================
# AUDIT LOGGING SYSTEM
# =============================================================================

class EventType(Enum):
    """Audit event types"""
    SYSTEM_START = "system_start"
    FILE_UPLOAD = "file_upload"
    ANALYSIS_START = "analysis_start"
    ANALYSIS_COMPLETE = "analysis_complete"
    THREAT_DETECTED = "threat_detected"
    THREAT_VIEWED = "threat_viewed"
    USER_SESSION = "user_session"
    ERROR_OCCURRED = "error_occurred"

class EventSeverity(Enum):
    """Event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Audit event structure"""
    event_id: str
    timestamp: str
    event_type: str
    severity: str
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    action: str
    resource: str
    outcome: str
    details: dict
    risk_score: float = None

class AuditLogger:
    """Enterprise audit logging system"""
    
    def __init__(self, log_dir="audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.setup_logger()
        self.active_sessions = {}
    
    def setup_logger(self):
        """Setup structured JSON logger"""
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create file handler
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False
    
    def get_request_context(self):
        """Extract request context safely"""
        try:
            return {
                'ip_address': request.remote_addr or 'unknown',
                'user_agent': request.headers.get('User-Agent', 'unknown'),
                'method': request.method,
                'endpoint': request.endpoint or 'unknown'
            }
        except RuntimeError:
            return {
                'ip_address': '127.0.0.1',
                'user_agent': 'system',
                'method': 'system',
                'endpoint': 'system'
            }
    
    def log_event(self, event_type, severity, action, resource, outcome="success", 
                  details=None, risk_score=None, user_id=None, session_id=None):
        """Log audit event"""
        context = self.get_request_context()
        
        # Get session info
        if not user_id:
            user_id = session.get('user_id', 'anonymous')
        if not session_id:
            session_id = session.get('session_id', str(uuid.uuid4()))
            session['session_id'] = session_id
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type.value if isinstance(event_type, EventType) else event_type,
            severity=severity.value if isinstance(severity, EventSeverity) else severity,
            user_id=user_id,
            session_id=session_id,
            ip_address=context['ip_address'],
            user_agent=context['user_agent'],
            action=action,
            resource=resource,
            outcome=outcome,
            details=details or {},
            risk_score=risk_score
        )
        
        # Log to file as JSON
        self.logger.info(json.dumps(asdict(event), ensure_ascii=False))
        
        # Update session tracking
        self.update_session_activity(session_id, event_type, user_id)
        
        return event.event_id
    
    def update_session_activity(self, session_id, event_type, user_id):
        """Track session activity"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                'user_id': user_id,
                'start_time': datetime.now(timezone.utc),
                'last_activity': datetime.now(timezone.utc),
                'event_count': 0,
                'events': []
            }
        
        session_data = self.active_sessions[session_id]
        session_data['last_activity'] = datetime.now(timezone.utc)
        session_data['event_count'] += 1
        session_data['events'].append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type.value if isinstance(event_type, EventType) else event_type
        })
        
        # Keep only last 10 events per session
        session_data['events'] = session_data['events'][-10:]
    
    def log_file_upload(self, filename, file_size, file_hash=None):
        """Log file upload event"""
        return self.log_event(
            event_type=EventType.FILE_UPLOAD,
            severity=EventSeverity.MEDIUM,
            action=f"File uploaded: {filename}",
            resource=f"file:{filename}",
            details={
                'filename': filename,
                'file_size': file_size,
                'file_hash': file_hash,
                'upload_timestamp': datetime.now().isoformat()
            }
        )
    
    def log_analysis_start(self, analysis_type, input_data):
        """Log analysis start"""
        return self.log_event(
            event_type=EventType.ANALYSIS_START,
            severity=EventSeverity.MEDIUM,
            action=f"Started {analysis_type} analysis",
            resource="threat_analysis_engine",
            details={
                'analysis_type': analysis_type,
                'input_records': input_data.get('record_count', 0),
                'data_source': input_data.get('source', 'unknown')
            }
        )
    
    def log_analysis_complete(self, results):
        """Log analysis completion"""
        severity = EventSeverity.HIGH if results.get('high_risk_count', 0) > 0 else EventSeverity.MEDIUM
        
        return self.log_event(
            event_type=EventType.ANALYSIS_COMPLETE,
            severity=severity,
            action="Analysis completed",
            resource="threat_analysis_engine",
            details={
                'total_messages': results.get('total_messages', 0),
                'flagged_messages': results.get('flagged_messages', 0),
                'high_risk_messages': results.get('high_risk_messages', 0),
                'processing_time': results.get('processing_time', 0),
                'threat_categories_detected': results.get('threat_categories', [])
            }
        )
    
    def log_threat_detection(self, message_id, threat_details, risk_score):
        """Log individual threat detection"""
        severity = (EventSeverity.CRITICAL if risk_score >= 70 else 
                   EventSeverity.HIGH if risk_score >= 50 else 
                   EventSeverity.MEDIUM)
        
        return self.log_event(
            event_type=EventType.THREAT_DETECTED,
            severity=severity,
            action=f"Threat detected in message {message_id}",
            resource=f"message:{message_id}",
            risk_score=risk_score,
            details={
                'message_id': message_id,
                'risk_level': threat_details.get('risk_level'),
                'threat_categories': threat_details.get('threat_categories', []),
                'pattern_matches': threat_details.get('pattern_matches', 0),
                'sentiment_score': threat_details.get('sentiment_score', 0)
            }
        )
    
    def log_threat_viewed(self, message_id, risk_score):
        """Log when user views threat details"""
        return self.log_event(
            event_type=EventType.THREAT_VIEWED,
            severity=EventSeverity.LOW,
            action=f"Viewed threat details for message {message_id}",
            resource=f"message:{message_id}",
            risk_score=risk_score,
            details={'message_id': message_id, 'view_type': 'detailed_modal'}
        )
    
    def log_error(self, error_type, error_message, stack_trace=None):
        """Log system errors"""
        return self.log_event(
            event_type=EventType.ERROR_OCCURRED,
            severity=EventSeverity.HIGH,
            action=f"System error: {error_type}",
            resource="system",
            outcome="error",
            details={
                'error_type': error_type,
                'error_message': error_message,
                'stack_trace': stack_trace
            }
        )

# Initialize audit logger
audit_logger = AuditLogger()

# Log system startup
audit_logger.log_event(
    event_type=EventType.SYSTEM_START,
    severity=EventSeverity.MEDIUM,
    action="ThreatSense Analytics system started",
    resource="application",
    user_id="system",
    session_id="system_startup",
    details={
        'startup_time': datetime.now().isoformat(),
        'version': '2.0.0',
        'features': ['threat_analysis', 'audit_logging', 'interactive_ui', 'admin_authentication']
    }
)

# =============================================================================
# THREAT ANALYSIS SYSTEM (Enhanced with Audit Logging)
# =============================================================================

class MessageRiskProfiler:
    """Advanced message risk profiling with multi-dimensional threat analysis"""
    
    def __init__(self):
        self.threat_categories = {
            'grooming': [
                r"you're\s+so\s+(mature|grown\s+up)",
                r"you're\s+so\s+beautiful\s+for\s+your\s+age",
                r"age.*doesn't matter",
                r"you're\s+special",
                r"trust\s+me"
            ],
            'isolation': [
                r"don'?t\s+tell",
                r"keep.*between\s+us",
                r"only\s+between\s+us",
                r"(secret|private|special)\s+(chat|talk)?",
                r"(just|only)\s+you\s+and\s+me"
            ],
            'coercion': [
                r"you\s+owe\s+me",
                r"if\s+you\s+tell\s+anyone",
                r"nobody\s+will\s+believe\s+you",
                r"you\s+have\s+to",
                r"you\s+must"
            ],
            'inappropriate_requests': [
                r"send\s+me\s+a\s+pic",
                r"show\s+me\s+what\s+you're\s+wearing",
                r"(undress|take.*clothes.*off|naked|nude)",
                r"what.*wearing",
                r"send.*(pic|photo|picture)"
            ],
            'meeting_requests': [
                r"(let'?s|lets)\s+meet.*alone",
                r"i\s+want\s+to\s+meet\s+you\s+in\s+person",
                r"come\s+over",
                r"alone.*(meet|see)",
                r"are\s+your\s+parents\s+(home|around)"
            ]
        }
    
    def analyze_message(self, message, message_id=None):
        """Perform comprehensive risk analysis on a message"""
        try:
            threat_scores = {}
            matched_patterns = {}
            
            # Analyze each threat category
            for category, patterns in self.threat_categories.items():
                category_matches = 0
                category_patterns = []
                
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        category_matches += 1
                        category_patterns.append(pattern)
                
                threat_scores[category] = category_matches
                matched_patterns[category] = category_patterns
            
            # Calculate overall threat level
            total_threats = sum(threat_scores.values())
            high_risk_categories = sum(1 for score in threat_scores.values() if score > 0)
            
            # Sentiment analysis
            sentiment = sia.polarity_scores(message)
            
            # Calculate risk score (0-100)
            risk_score = min(100, (total_threats * 15) + (high_risk_categories * 10) + 
                            (abs(sentiment['compound']) * 20))
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "Critical"
                risk_color = "#dc3545"
            elif risk_score >= 50:
                risk_level = "High"
                risk_color = "#fd7e14"
            elif risk_score >= 30:
                risk_level = "Medium"
                risk_color = "#ffc107"
            elif risk_score >= 15:
                risk_level = "Low"
                risk_color = "#17a2b8"
            else:
                risk_level = "Minimal"
                risk_color = "#28a745"
            
            # Generate AI-like explanation
            explanation = self._generate_explanation(threat_scores, sentiment, risk_score)
            
            profile = {
                'risk_score': round(risk_score, 1),
                'risk_level': risk_level,
                'risk_color': risk_color,
                'threat_scores': threat_scores,
                'matched_patterns': matched_patterns,
                'sentiment': sentiment,
                'explanation': explanation,
                'threat_indicators': total_threats,
                'affected_categories': high_risk_categories
            }
            
            # Log threat detection if significant risk found
            if risk_score >= 30 and message_id:
                audit_logger.log_threat_detection(
                    message_id=message_id,
                    threat_details={
                        'risk_level': risk_level,
                        'threat_categories': [cat for cat, score in threat_scores.items() if score > 0],
                        'pattern_matches': total_threats,
                        'sentiment_score': sentiment['compound']
                    },
                    risk_score=risk_score
                )
            
            return profile
            
        except Exception as e:
            audit_logger.log_error(
                error_type="THREAT_ANALYSIS_ERROR",
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
            raise
    
    def _generate_explanation(self, threat_scores, sentiment, risk_score):
        """Generate human-readable explanation of the risk assessment"""
        explanations = []
        
        # Analyze threat categories
        high_threat_cats = [cat for cat, score in threat_scores.items() if score > 0]
        
        if high_threat_cats:
            explanations.append(f"Detected suspicious patterns in: {', '.join(high_threat_cats).replace('_', ' ')}")
        
        # Sentiment analysis
        if sentiment['compound'] <= -0.5:
            explanations.append("Message shows highly negative emotional tone")
        elif sentiment['compound'] <= -0.2:
            explanations.append("Message contains negative sentiment")
        
        # Risk level explanation
        if risk_score >= 70:
            explanations.append("IMMEDIATE ATTENTION REQUIRED: Multiple high-risk indicators present")
        elif risk_score >= 50:
            explanations.append("HIGH PRIORITY: Strong predatory behavior patterns detected")
        elif risk_score >= 30:
            explanations.append("CAUTION: Some concerning elements identified")
        elif risk_score >= 15:
            explanations.append("LOW CONCERN: Minor suspicious indicators")
        else:
            explanations.append("Message appears safe with minimal risk indicators")
        
        return ". ".join(explanations) if explanations else "No significant risk factors detected."

# Initialize the advanced profiler
risk_profiler = MessageRiskProfiler()

# Define suspicious regex patterns
suspicious_patterns = [
    r"don'?t\s+tell", r"keep.*between\s+us", r"only\s+between\s+us",
    r"(secret|private|special)\s+(chat|talk)?", r"(just|only)\s+you\s+and\s+me",
    r"don't\s+share\s+this\s+with\s+anyone", r"it's\s+our\s+little\s+secret",
    r"you're\s+so\s+(mature|grown\s+up)", r"you're\s+so\s+beautiful\s+for\s+your\s+age",
    r"(let'?s|lets)\s+meet.*alone", r"i\s+want\s+to\s+meet\s+you\s+in\s+person",
    r"are\s+your\s+parents\s+(home|around)", r"let'?s\s+hang\s+out\s+just\s+us",
    r"tell\s+me\s+more\s+about\s+your\s+family", r"send\s+me\s+a\s+pic",
    r"i\s+can\s+keep\s+secrets", r"show\s+me\s+what\s+you're\s+wearing",
    r"you\s+owe\s+me\s+(something|a\s+favor)", r"just\s+trust\s+me",
    r"you\s+don't\s+have\s+to\s+tell\s+anyone", r"it\s+won'?t\s+hurt",
    r"if\s+you\s+tell\s+anyone\s+we\s+can'?t\s+talk\s+anymore",
    r"i\s+won'?t\s+tell\s+anyone\s+promise", r"this\s+is\s+our\s+secret\s+to\s+keep",
    r"secret", r"don't tell anyone", r"just between us", r"you're so mature",
    r"send.*(pic|photo|picture)", r"what.*wearing", r"come over", r"alone.*(meet|see)",
    r"i won.t tell", r"you can trust me", r"age.*doesn't matter", r"it.*our.*secret",
    r"if.*tell.*anyone", r"i.*like.*you.*(so much|a lot)", r"nobody will know",
    r"this.*is.*between.*us", r"promise.*won't.*tell", r"(i|we).*won.t.*get.*caught",
    r"(touch|touching)", r"(kiss|kissing)", r"(undress|take.*clothes.*off|naked|nude)"
]

def get_severity_level(message):
    """Get severity level using pattern matches and sentiment analysis"""
    match_count = 0
    for pattern in suspicious_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            match_count += 1

    sentiment = sia.polarity_scores(message)
    compound = sentiment['compound']

    if match_count >= 2:
        return "High Risk", match_count
    elif match_count == 1 or compound <= -0.5:
        return "Suspicious", match_count
    else:
        return "Safe", match_count

def process_messages(df):
    """Process DataFrame of messages with audit logging"""
    start_time = time.time()
    
    try:
        # Log analysis start
        audit_logger.log_analysis_start(
            analysis_type="threat_message_analysis",
            input_data={
                'record_count': len(df),
                'source': 'csv_file',
                'columns': list(df.columns)
            }
        )
        
        # Process messages
        df['match_count'] = df['message'].apply(lambda msg: get_severity_level(msg)[1])
        df['severity'] = df['message'].apply(lambda msg: get_severity_level(msg)[0])
        df['flagged'] = df['severity'] != "Safe"
        flagged = df[df['flagged'] == True]
        
        # Add sentiment compound score
        flagged['compound'] = flagged['message'].apply(lambda msg: sia.polarity_scores(msg)['compound'])
        
        # Calculate analysis results
        processing_time = time.time() - start_time
        high_risk_count = len(flagged[flagged['severity'] == 'High Risk'])
        threat_categories = []
        
        # Log analysis completion
        audit_logger.log_analysis_complete({
            'total_messages': len(df),
            'flagged_messages': len(flagged),
            'high_risk_messages': high_risk_count,
            'processing_time': processing_time,
            'threat_categories': threat_categories
        })
        
        return flagged
        
    except Exception as e:
        audit_logger.log_error(
            error_type="MESSAGE_PROCESSING_ERROR",
            error_message=str(e),
            stack_trace=traceback.format_exc()
        )
        raise

# =============================================================================
# FLASK ROUTES WITH AUDIT LOGGING
# =============================================================================

@app.before_request
def before_request():
    """Initialize session and audit logging for each request"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['user_id'] = f"user_{session['session_id'][:8]}"

@app.route('/api/threat-viewed/<message_id>')
def log_threat_view(message_id):
    """API endpoint to log when user views threat details"""
    try:
        # This would typically get risk score from database
        # For now, we'll use a placeholder
        risk_score = request.args.get('risk_score', 50, type=float)
        
        audit_logger.log_threat_viewed(message_id, risk_score)
        
        return jsonify({'status': 'logged', 'message_id': message_id})
    except Exception as e:
        audit_logger.log_error("API_ERROR", str(e))
        return jsonify({'error': 'Failed to log threat view'}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main application route with comprehensive audit logging"""
    try:
        if request.method == 'POST':
            # Handle file upload
            file = request.files.get('file')
            filename = None
            file_size = 0
            file_hash = None
            
            if file and file.filename:
                # Save uploaded file
                filename = file.filename
                file_path = os.path.join("uploads", filename)
                os.makedirs("uploads", exist_ok=True)
                file.save(file_path)
                
                # Calculate file stats
                file_size = os.path.getsize(file_path)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Log file upload
                audit_logger.log_file_upload(filename, file_size, file_hash)
                
                # Load data
                df = pd.read_csv(file_path)
            else:
                # Use default file
                df = pd.read_csv("sample_chats.csv")
                filename = "sample_chats.csv"
            
            # Process messages with audit logging
            flagged = process_messages(df)
            
            # Enhanced profiling for flagged messages
            enhanced_profiles = []
            for _, row in flagged.iterrows():
                profile = risk_profiler.analyze_message(row['message'], row['id'])
                enhanced_profiles.append({
                    'id': row['id'],
                    'message': row['message'],
                    'profile': profile
                })
            
            # Prepare chart data
            risk_counts = df['severity'].value_counts().to_dict()
            risk_data = [
                risk_counts.get('High Risk', 0),
                risk_counts.get('Suspicious', 0),
                risk_counts.get('Safe', 0)
            ]
            
            # Threat category analysis
            threat_category_counts = {'grooming': 0, 'isolation': 0, 'coercion': 0, 
                                     'inappropriate_requests': 0, 'meeting_requests': 0}
            for profile in enhanced_profiles:
                for category, score in profile['profile']['threat_scores'].items():
                    if score > 0:
                        threat_category_counts[category] += score
            
            # Pattern detection frequency
            pattern_matches = []
            for _, row in df.iterrows():
                message = row['message']
                for pattern in suspicious_patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        pattern_name = pattern.replace('r"', '').replace('"', '')
                        pattern_name = pattern_name[:15] + '...' if len(pattern_name) > 15 else pattern_name
                        pattern_matches.append(pattern_name)
            
            pattern_counter = Counter(pattern_matches)
            top_patterns = pattern_counter.most_common(5)
            pattern_labels = [p[0] for p in top_patterns]
            pattern_counts = [p[1] for p in top_patterns]
            
            # Sentiment distribution
            sentiment_ranges = {
                'Very Negative': (-1.0, -0.6),
                'Negative': (-0.6, -0.2),
                'Neutral': (-0.2, 0.2),
                'Positive': (0.2, 0.6),
                'Very Positive': (0.6, 1.0)
            }
            
            sentiment_counts = {k: 0 for k in sentiment_ranges.keys()}
            for _, row in df.iterrows():
                compound = sia.polarity_scores(row['message'])['compound']
                for label, (min_val, max_val) in sentiment_ranges.items():
                    if min_val <= compound < max_val:
                        sentiment_counts[label] += 1
            
            sentiment_data = list(sentiment_counts.values())
            
            # Match count distribution
            match_count_data = [0, 0, 0, 0]  # 0, 1, 2, 3+
            for count in df['match_count']:
                if count >= 3:
                    match_count_data[3] += 1
                else:
                    match_count_data[count] += 1
            
            # Convert flagged messages to HTML table
            flagged_html = flagged.to_html(classes="table table-striped", index=False)
            
            return render_template(
                "index.html", 
                flagged_html=flagged_html,
                enhanced_profiles=enhanced_profiles,
                risk_counts=json.dumps(risk_data),
                threat_categories=json.dumps(list(threat_category_counts.values())),
                threat_category_labels=json.dumps(list(threat_category_counts.keys())),
                pattern_labels=json.dumps(pattern_labels),
                pattern_counts=json.dumps(pattern_counts),
                sentiment_counts=json.dumps(sentiment_data),
                match_counts=json.dumps(match_count_data)
            )
        
        # GET request - render upload form
        return render_template("index.html", flagged_html=None)
        
    except Exception as e:
        # Log any application errors
        audit_logger.log_error(
            error_type="APPLICATION_ERROR",
            error_message=str(e),
            stack_trace=traceback.format_exc()
        )
        
        # Return error page or message
        return render_template("index.html", 
                             flagged_html=None, 
                             error_message="An error occurred during analysis. Please try again.")

@app.route('/admin/audit-logs')
@admin_required
def view_audit_logs():
    """Admin endpoint to view recent audit logs - PROTECTED"""
    try:
        # Read recent audit logs (last 50 entries)
        log_file = audit_logger.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        logs = []
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-50:]:  # Last 50 entries
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        
        return jsonify({
            'logs': logs,
            'total_entries': len(logs),
            'active_sessions': len(audit_logger.active_sessions),
            'admin_user': session.get('admin_user', 'unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/session-info')
@admin_required
def session_info():
    """Admin endpoint to view active session information - PROTECTED"""
    try:
        sessions_info = {}
        for session_id, session_data in audit_logger.active_sessions.items():
            sessions_info[session_id] = {
                'user_id': session_data['user_id'],
                'start_time': session_data['start_time'].isoformat(),
                'last_activity': session_data['last_activity'].isoformat(),
                'event_count': session_data['event_count'],
                'recent_events': session_data['events'][-5:]  # Last 5 events
            }
        
        return jsonify({
            'active_sessions': sessions_info,
            'total_sessions': len(sessions_info),
            'admin_user': session.get('admin_user', 'unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# SETTINGS API ENDPOINTS
# =============================================================================

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Handle settings API requests"""
    try:
        if request.method == 'POST':
            # Save settings
            settings_data = request.get_json()
            
            if not settings_data:
                return jsonify({'error': 'No settings data provided'}), 400
            
            # Store in session for now (could be database later)
            session['user_settings'] = settings_data
            
            # Log settings change
            audit_logger.log_event(
                event_type=EventType.USER_SESSION,
                severity=EventSeverity.LOW,
                action="User settings updated",
                resource="user_settings",
                details={
                    'settings_categories': list(settings_data.keys()),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return jsonify({
                'status': 'success',
                'message': 'Settings saved successfully',
                'timestamp': datetime.now().isoformat()
            })
        
        else:
            # Get settings
            user_settings = session.get('user_settings', {})
            return jsonify({
                'status': 'success',
                'settings': user_settings,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        audit_logger.log_error("SETTINGS_API_ERROR", str(e))
        return jsonify({'error': 'Failed to process settings request'}), 500

@app.route('/settings')
def settings_page():
    """Serve the settings configuration page"""
    try:
        # Get current user settings from session
        user_settings = session.get('user_settings', {})
        
        # Log page access
        audit_logger.log_event(
            event_type=EventType.USER_SESSION,
            severity=EventSeverity.LOW,
            action="Settings page accessed",
            resource="settings_page",
            details={'timestamp': datetime.now().isoformat()}
        )
        
        return render_template('settings.html', current_settings=user_settings)
        
    except Exception as e:
        audit_logger.log_error("SETTINGS_PAGE_ERROR", str(e))
        flash('Error loading settings page', 'error')
        return redirect(url_for('index'))

@app.route('/api/log-event', methods=['POST'])
def log_custom_event():
    """Log custom events from frontend"""
    try:
        event_data = request.get_json()
        
        if not event_data or 'action' not in event_data:
            return jsonify({'error': 'Invalid event data'}), 400
        
        # Log the frontend event
        audit_logger.log_event(
            event_type=EventType.USER_SESSION,
            severity=EventSeverity.LOW,
            action=event_data['action'],
            resource="frontend_interaction",
            details=event_data.get('details', {})
        )
        
        return jsonify({'status': 'logged', 'action': event_data['action']})
        
    except Exception as e:
        audit_logger.log_error("EVENT_LOGGING_ERROR", str(e))
        return jsonify({'error': 'Failed to log event'}), 500

if __name__ == '__main__':
    try:
        # Get port from environment variable (for Railway/Heroku deployment)
        port = int(os.environ.get('PORT', 5000))
        # Determine if we're in production
        is_production = os.environ.get('FLASK_ENV') != 'development'
        
        app.run(
            debug=not is_production,
            host='0.0.0.0',
            port=port
        )
    except Exception as e:
        audit_logger.log_error(
            error_type="SYSTEM_STARTUP_ERROR",
            error_message=str(e),
            stack_trace=traceback.format_exc()
        )
        raise