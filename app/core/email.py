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
        username: str,
        verification_token: str,
        user_id: str
    ) -> bool:
        """
        Send email verification email
        
        Args:
            to_email: Recipient email address
            username: Username of the user
            verification_token: Email verification token
            user_id: User ID for logging
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            logger.info("Starting email verification send", 
                       user_id=user_id,
                       email=to_email,
                       username=username)
            
            subject = "Vérifiez votre adresse e-mail"
            
            # Create verification URL
            verification_url = f"{settings.mail_verification_url}?token={verification_token}"
            logger.debug("Verification URL created", 
                        user_id=user_id,
                        verification_url=verification_url)
            
            # Email content
            html_content = EmailService._get_verification_email_template(
                username=username,
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
        username: str,
        reset_token: str,
        user_id: str
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: Recipient email address
            username: Username of the user
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
                username=username,
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
        username: str,
        password: str,
        user_id: str
    ) -> bool:
        """
        Send welcome email with user credentials
        
        Args:
            to_email: Recipient email address
            username: Username of the user
            password: User's password (plain text for first login)
            user_id: User ID for logging
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            logger.info("Starting welcome email send", 
                       user_id=user_id,
                       email=to_email,
                       username=username)
            
            subject = "Bienvenue sur " + settings.app_name + " - Vos identifiants de connexion"
            
            # Create login URL
            login_url = settings.mail_login_url
            
            # Email content
            html_content = EmailService._get_welcome_email_template(
                username=username,
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
    def _get_verification_email_template(username: str, verification_url: str) -> str:
        """
        Get email verification email template
        
        Args:
            username: Username of the user
            verification_url: Email verification URL
            
        Returns:
            str: HTML email content
        """
        try:
            template = jinja_env.get_template("verification.html")
            return template.render(
                username=username,
                verification_url=verification_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render verification email template, using default", error=str(e))
            return EmailService._get_default_verification_template(username, verification_url)
    
    @staticmethod
    def _get_password_reset_email_template(username: str, reset_url: str) -> str:
        """
        Get password reset email template
        
        Args:
            username: Username of the user
            reset_url: Password reset URL
            
        Returns:
            str: HTML email content
        """
        try:
            template = jinja_env.get_template("password_reset.html")
            return template.render(
                username=username,
                reset_url=reset_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render password reset email template, using default", error=str(e))
            return EmailService._get_default_password_reset_template(username, reset_url)
    
    @staticmethod
    def _get_welcome_email_template(username: str, email: str, password: str, login_url: str) -> str:
        """
        Get welcome email template
        
        Args:
            username: Username of the user
            email: User's email address
            password: User's password
            login_url: Login URL
            
        Returns:
            str: HTML email content
        """
        try:
            template = jinja_env.get_template("welcome.html")
            return template.render(
                username=username,
                email=email,
                password=password,
                login_url=login_url,
                app_name=settings.app_name
            )
        except Exception as e:
            logger.warning("Failed to render welcome email template, using default", error=str(e))
            return EmailService._get_default_welcome_template(username, email, password, login_url)
    
    @staticmethod
    def _get_default_verification_template(username: str, verification_url: str) -> str:
        """Fallback email verification template if external template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vérifiez votre e-mail - {settings.app_name}</title>
        </head>
        <body>
            <h1>Bonjour {username}!</h1>
            <p>Bienvenue sur {settings.app_name}! Veuillez vérifier votre adresse e-mail.</p>
            <p><a href="{verification_url}">Vérifier l'adresse e-mail</a></p>
            <p>Si le lien ne fonctionne pas, copiez et collez ceci dans votre navigateur : {verification_url}</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _get_default_password_reset_template(username: str, reset_url: str) -> str:
        """Fallback password reset template if external template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Réinitialisez votre mot de passe - {settings.app_name}</title>
        </head>
        <body>
            <h1>Bonjour {username}!</h1>
            <p>Nous avons reçu une demande de réinitialisation de votre mot de passe pour votre compte {settings.app_name}.</p>
            <p><a href="{reset_url}">Réinitialiser le mot de passe</a></p>
            <p>Si le lien ne fonctionne pas, copiez et collez ceci dans votre navigateur : {reset_url}</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _get_default_welcome_template(username: str, email: str, password: str, login_url: str) -> str:
        """Fallback welcome template if external template fails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bienvenue sur {settings.app_name} - Vos identifiants de connexion</title>
        </head>
        <body>
            <h1>Bienvenue {username}!</h1>
            <p>Votre compte sur {settings.app_name} a été créé avec succès.</p>
            <h2>Vos identifiants de connexion :</h2>
            <p><strong>Nom d'utilisateur:</strong> {username}</p>
            <p><strong>Adresse e-mail:</strong> {email}</p>
            <p><strong>Mot de passe:</strong> {password}</p>
            <p><a href="{login_url}">Se connecter maintenant</a></p>
            <p><strong>Important:</strong> Conservez ces informations en lieu sûr et ne les partagez avec personne.</p>
        </body>
        </html>
        """


# Convenience functions for easy access
async def send_email_verification(
    to_email: str,
    username: str,
    verification_token: str,
    user_id: str
) -> bool:
    """Send email verification email"""
    return await EmailService.send_email_verification(to_email, username, verification_token, user_id)


async def send_password_reset(
    to_email: str,
    username: str,
    reset_token: str,
    user_id: str
) -> bool:
    """Send password reset email"""
    return await EmailService.send_password_reset(to_email, username, reset_token, user_id)


async def send_welcome_email(
    to_email: str,
    username: str,
    password: str,
    user_id: str
) -> bool:
    """Send welcome email with user credentials"""
    return await EmailService.send_welcome_email(to_email, username, password, user_id)


 