from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    try:
        v = validate_email(email)
        return v.normalized
    except EmailNotValidError as e:
        raise ValueError(str(e))
