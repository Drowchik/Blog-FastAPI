from email.message import EmailMessage
from src.app.core.config import settings
from pydantic import EmailStr

def create_confirmation_template(
    user: dict,
    email_to: EmailStr) -> EmailMessage:
    email = EmailMessage()
    
    email["Subject"] = "Подтверждение регистрации"
    email["From"] = settings.email
    email["To"] = email_to
    
    email.set_content(
        f"""
            <h1>Подтвердить регистрацию</h1>
             Вы зарегестрировались, {user["name"]} 
        """,
        subtype="html")
    return email