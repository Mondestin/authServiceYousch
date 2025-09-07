"""
Email service for the AuthService
Handles sending verification and password reset emails
"""

from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import get_settings
from app.core.logging import get_logger

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Email configuration
# For SSL connections (port 465), we should use SSL_TLS and disable STARTTLS
# to avoid conflicts
use_starttls = False  # Disable STARTTLS for SSL connections
use_ssl_tls = settings.mail_use_ssl  # Use SSL/TLS

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from_address or "noreply@authservice.com",
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_host,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=use_starttls,
    MAIL_SSL_TLS=use_ssl_tls,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False  # Disable certificate validation for FleetPay server
)

# Log email configuration (without password)
logger.info("Email configuration loaded", 
           server=settings.mail_host,
           port=settings.mail_port,
           username=settings.mail_username,
           from_email=settings.mail_from_address,
           from_name=settings.mail_from_name,
           config_use_tls=settings.mail_use_tls,
           config_use_ssl=settings.mail_use_ssl,
           fastapi_mail_starttls=use_starttls,
           fastapi_mail_ssl_tls=use_ssl_tls,
                       )

# Initialize FastMail
fastmail = FastMail(email_config)

# Jinja2 template environment
template_dir = Path(__file__).parent.parent / "templates" / "email"
jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)




class EmailService:
    """Service for sending emails to users"""
    
    @staticmethod
    async def send_email_verification(
        to_email: str,
        firstname: str,
        lastname: str,
        verification_token: str,
        user_id: str
    ) -> bool:
        """
        Send email verification email
        
        Args:
            to_email: Recipient email address
            firstname: User's first name
            lastname: User's last name
            verification_token: Email verification token
            user_id: User ID for logging
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            logger.info("Starting email verification send", 
                       user_id=user_id,
                       email=to_email,
                       firstname=firstname,
                       lastname=lastname)
            
            subject = "Vérifiez votre adresse e-mail"
            
            # Create verification URL
            verification_url = f"{settings.mail_verification_url}?token={verification_token}"
            logger.debug("Verification URL created", 
                        user_id=user_id,
                        verification_url=verification_url)
            
            # Email content
            html_content = EmailService._get_verification_email_template(
                firstname=firstname,
                lastname=lastname,
                verification_url=verification_url
            )
            logger.debug("Email template rendered", 
                        user_id=user_id,
                        content_length=len(html_content))
            
            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=html_content,
                subtype=MessageType.html
            )
            logger.debug("Message schema created", 
                        user_id=user_id,
                        subject=subject,
                        recipients=[to_email])
            
            # Send email
            logger.info("Attempting to send email", 
                       user_id=user_id,
                       email=to_email,
                       server=settings.mail_host,
                       port=settings.mail_port)
            
            await fastmail.send_message(message)
            
            logger.info("Email verification sent successfully", 
                       user_id=user_id,
                       email=to_email,
                       server=settings.mail_host)
            return True
            
        except Exception as e:
            logger.error("Failed to send email verification", 
                        user_id=user_id,
                        email=to_email,
                        error=str(e),
                        error_type=type(e).__name__,
                        server=settings.mail_host,
                        port=settings.mail_port)
            return False
    
    @staticmethod
    async def send_password_reset(
        to_email: str,
        firstname: str,
        lastname: str,
        reset_token: str,
        user_id: str
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: Recipient email address
            firstname: User's first name
            lastname: User's last name
            reset_token: Password reset token
            user_id: User ID for logging
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = "Réinitialisez votre mot de passe"
            
            # Create reset URL
            reset_url = f"{settings.mail_password_reset_url}?token={reset_token}"
            
            # Email content
            html_content = EmailService._get_password_reset_email_template(
                firstname=firstname,
                lastname=lastname,
                reset_url=reset_url
            )
            
            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=html_content,
                subtype=MessageType.html
            )
            
            # Send email
            await fastmail.send_message(message)
            
            logger.info("Password reset email sent successfully", 
                       user_id=user_id,
                       email=to_email)
            return True
            
        except Exception as e:
            logger.error("Failed to send password reset email", 
                       user_id=user_id,
                       email=to_email,
                       error=str(e))
            return False
    
    @staticmethod
    async def send_welcome_email(
        to_email: str,
        firstname: str,
        lastname: str,
        password: str,
        user_id: str
    ) -> bool:
        """
        Send welcome email with user credentials
        
        Args:
            to_email: Recipient email address
            firstname: User's first name
            lastname: User's last name
            password: User's password (plain text for first login)
            user_id: User ID for logging
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            logger.info("Starting welcome email send", 
                       user_id=user_id,
                       email=to_email,
                       firstname=firstname,
                       lastname=lastname)
            
            subject = "Bienvenue sur " + settings.app_name + " - Vos identifiants de connexion"
            
            # Create login URL
            login_url = settings.mail_login_url
            
            # Email content
            html_content = EmailService._get_welcome_email_template(
                firstname=firstname,
                lastname=lastname,
                email=to_email,
                password=password,
                login_url=login_url
            )
            
            logger.debug("Welcome email template rendered", 
                        user_id=user_id,
                        content_length=len(html_content))
            
            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=html_content,
                subtype=MessageType.html
            )
            
            logger.debug("Welcome message schema created", 
                        user_id=user_id,
                        subject=subject,
                        recipients=[to_email])
            
            # Send email
            logger.info("Attempting to send welcome email", 
                       user_id=user_id,
                       email=to_email,
                       server=settings.mail_host,
                       port=settings.mail_port)
            
            await fastmail.send_message(message)
            
            logger.info("Welcome email sent successfully", 
                       user_id=user_id,
                       email=to_email,
                       server=settings.mail_host)
            return True
            
        except Exception as e:
            logger.error("Failed to send welcome email", 
                       user_id=user_id,
                       email=to_email,
                       error=str(e),
                       error_type=type(e).__name__,
                       server=settings.mail_host,
                       port=settings.mail_port)
            return False
    
    @staticmethod
    def _get_verification_email_template(firstname: str, lastname: str, verification_url: str) -> str:
        """
        Get email verification email template
        
        Args:
            firstname: User's first name
            lastname: User's last name
            verification_url: Email verification URL
            
        Returns:
            str: HTML email content
        """
        try:
            template = jinja_env.get_template("verification.html")
            return template.render(
                firstname=firstname,
                lastname=lastname,
                verification_url=verification_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render verification email template, using default", error=str(e))
            return EmailService._get_default_verification_template(firstname, lastname, verification_url)
    
    @staticmethod
    def _get_password_reset_email_template(firstname: str, lastname: str, reset_url: str) -> str:
        """
        Get password reset email template
        
        Args:
            firstname: User's first name
            lastname: User's last name
            reset_url: Password reset URL
            
        Returns:
            str: HTML email content
        """
        try:
            template = jinja_env.get_template("password_reset.html")
            return template.render(
                firstname=firstname,
                lastname=lastname,
                reset_url=reset_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render password reset email template, using default", error=str(e))
            return EmailService._get_default_password_reset_template(firstname, lastname, reset_url)
    
    @staticmethod
    def _get_welcome_email_template(firstname: str, lastname: str, email: str, password: str, login_url: str) -> str:
        """
        Get welcome email template
        
        Args:
            firstname: User's first name
            lastname: User's last name
            email: User's email address
            password: User's password
            login_url: Login URL
            
        Returns:
            str: HTML email content
        """
        try:
            template = jinja_env.get_template("welcome.html")
            return template.render(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=password,
                login_url=login_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render welcome email template, using default", error=str(e))
            return EmailService._get_default_welcome_template(firstname, lastname, email, password, login_url)
    
    @staticmethod
    def _get_default_verification_template(firstname: str, lastname: str, verification_url: str) -> str:
        """Fallback email verification template if external template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vérifiez votre e-mail - {settings.app_name}</title>
        </head>
        <body>
            <h1>Bonjour {firstname} {lastname}!</h1>
            <p>Bienvenue sur {settings.app_name}! Veuillez vérifier votre adresse e-mail.</p>
            <p><a href="{verification_url}">Vérifier l'adresse e-mail</a></p>
            <p>Si le lien ne fonctionne pas, copiez et collez ceci dans votre navigateur : {verification_url}</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _get_default_password_reset_template(firstname: str, lastname: str, reset_url: str) -> str:
        """Fallback password reset template if external template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Réinitialisez votre mot de passe - {settings.app_name}</title>
        </head>
        <body>
            <h1>Bonjour {firstname} {lastname}!</h1>
            <p>Nous avons reçu une demande de réinitialisation de votre mot de passe pour votre compte {settings.app_name}.</p>
            <p><a href="{reset_url}">Réinitialiser le mot de passe</a></p>
            <p>Si le lien ne fonctionne pas, copiez et collez ceci dans votre navigateur : {reset_url}</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _get_default_welcome_template(firstname: str, lastname: str, email: str, password: str, login_url: str) -> str:
        """Fallback welcome template if external template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome to {settings.app_name} - Your Login Credentials</title>
        </head>
        <body>
            <h1>Welcome {firstname} {lastname}!</h1>
            <p>Your account on {settings.app_name} has been created successfully.</p>
            <h2>Your Login Credentials:</h2>
            <p><strong>Name:</strong> {firstname} {lastname}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Password:</strong> {password}</p>
            <p><a href="{login_url}">Login Now</a></p>
            <p><strong>Important:</strong> Keep these credentials safe and don't share them with anyone.</p>
        </body>
        </html>
        """
    
    @staticmethod
    async def send_password_changed(
        to_email: str,
        firstname: str,
        lastname: str,
        change_date: str,
        change_time: str,
        ip_address: str,
        device_info: str,
        user_id: str
    ) -> bool:
        """Send password changed notification email"""
        try:
            subject = "Mot de passe modifié avec succès"
            
            html_content = EmailService._get_password_changed_template(
                firstname=firstname,
                lastname=lastname,
                change_date=change_date,
                change_time=change_time,
                ip_address=ip_address,
                device_info=device_info
            )
            
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=html_content,
                subtype=MessageType.html
            )
            
            await fastmail.send_message(message)
            logger.info("Password changed email sent successfully", user_id=user_id, email=to_email)
            return True
            
        except Exception as e:
            logger.error("Failed to send password changed email", user_id=user_id, email=to_email, error=str(e))
            return False
    
    @staticmethod
    def _get_password_changed_template(firstname: str, lastname: str, change_date: str, change_time: str, ip_address: str, device_info: str) -> str:
        """Get password changed email template"""
        try:
            template = jinja_env.get_template("password_changed.html")
            return template.render(
                firstname=firstname,
                lastname=lastname,
                change_date=change_date,
                change_time=change_time,
                ip_address=ip_address,
                device_info=device_info,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render password changed template, using default", error=str(e))
            return f"<h1>Password Changed</h1><p>Hello {firstname} {lastname}, your password has been changed on {change_date} at {change_time}.</p>"
    
    @staticmethod
    async def send_account_locked(
        to_email: str,
        firstname: str,
        lastname: str,
        lock_reason: str,
        unlock_time: str,
        failed_attempts: int,
        support_url: str,
        user_id: str
    ) -> bool:
        """Send account locked notification email"""
        try:
            subject = "Alerte de sécurité du compte - Compte verrouillé"
            
            html_content = EmailService._get_account_locked_template(
                firstname=firstname,
                lastname=lastname,
                lock_reason=lock_reason,
                unlock_time=unlock_time,
                failed_attempts=failed_attempts,
                support_url=support_url
            )
            
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=html_content,
                subtype=MessageType.html
            )
            
            await fastmail.send_message(message)
            logger.info("Account locked email sent successfully", user_id=user_id, email=to_email)
            return True
            
        except Exception as e:
            logger.error("Failed to send account locked email", user_id=user_id, email=to_email, error=str(e))
            return False
    
    @staticmethod
    def _get_account_locked_template(firstname: str, lastname: str, lock_reason: str, unlock_time: str, failed_attempts: int, support_url: str) -> str:
        """Get account locked email template"""
        try:
            template = jinja_env.get_template("account_locked.html")
            return template.render(
                firstname=firstname,
                lastname=lastname,
                lock_reason=lock_reason,
                unlock_time=unlock_time,
                failed_attempts=failed_attempts,
                support_url=support_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render account locked template, using default", error=str(e))
            return f"<h1>Compte verrouillé</h1><p>Bonjour {firstname} {lastname}, votre compte a été verrouillé en raison de: {lock_reason}</p>"


# Convenience functions for easy access
async def send_email_verification(
    to_email: str,
    firstname: str,
    lastname: str,
    verification_token: str,
    user_id: str
) -> bool:
    """Send email verification email"""
    return await EmailService.send_email_verification(to_email, firstname, lastname, verification_token, user_id)


async def send_password_reset(
    to_email: str,
    firstname: str,
    lastname: str,
    reset_token: str,
    user_id: str
) -> bool:
    """Send password reset email"""
    return await EmailService.send_password_reset(to_email, firstname, lastname, reset_token, user_id)


async def send_welcome_email(
    to_email: str,
    firstname: str,
    lastname: str,
    password: str,
    user_id: str
) -> bool:
    """Send welcome email with user credentials"""
    return await EmailService.send_welcome_email(to_email, firstname, lastname, password, user_id)


async def send_password_changed(
    to_email: str,
    firstname: str,
    lastname: str,
    change_date: str,
    change_time: str,
    ip_address: str,
    device_info: str,
    user_id: str
) -> bool:
    """Send password changed notification email"""
    return await EmailService.send_password_changed(to_email, firstname, lastname, change_date, change_time, ip_address, device_info, user_id)


async def send_account_locked(
    to_email: str,
    firstname: str,
    lastname: str,
    lock_reason: str,
    unlock_time: str,
    failed_attempts: int,
    support_url: str,
    user_id: str
) -> bool:
    """Send account locked notification email"""
    return await EmailService.send_account_locked(to_email, firstname, lastname, lock_reason, unlock_time, failed_attempts, support_url, user_id)


async def send_login_alert(
    to_email: str,
    firstname: str,
    lastname: str,
    login_time: str,
    ip_address: str,
    location: str,
    device_info: str,
    browser_info: str,
    security_url: str,
    user_id: str
) -> bool:
    """Send new login alert email"""
    return await EmailService.send_login_alert(to_email, firstname, lastname, login_time, ip_address, location, device_info, browser_info, security_url, user_id)


async def send_email_changed(
    to_email: str,
    firstname: str,
    lastname: str,
    old_email: str,
    new_email: str,
    change_date: str,
    ip_address: str,
    user_id: str
) -> bool:
    """Send email changed notification"""
    return await EmailService.send_email_changed(to_email, firstname, lastname, old_email, new_email, change_date, ip_address, user_id)


async def send_account_deactivated(
    to_email: str,
    firstname: str,
    lastname: str,
    deactivation_date: str,
    deactivation_reason: str,
    deactivated_by: str,
    support_url: str,
    user_id: str
) -> bool:
    """Send account deactivated notification"""
    return await EmailService.send_account_deactivated(to_email, firstname, lastname, deactivation_date, deactivation_reason, deactivated_by, support_url, user_id)


async def send_token_expiring(
    to_email: str,
    firstname: str,
    lastname: str,
    token_type: str,
    expires_in: str,
    expiry_date: str,
    service_name: str,
    refresh_url: str,
    user_id: str
) -> bool:
    """Send token expiring warning email"""
    return await EmailService.send_token_expiring(to_email, firstname, lastname, token_type, expires_in, expiry_date, service_name, refresh_url, user_id)


 