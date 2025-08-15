import os
import secrets
from PIL import Image
from flask import current_app


def save_picture(form_picture, folder):
    """Save uploaded picture with random filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
    
    # Resize image
    output_size = (800, 800)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_fn


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def log_audit_event(user_id, action, table_name, record_id, changes=None, ip_address=None, user_agent=None):
    """Log audit events"""
    from models.audit_log import AuditLog
    from models import db
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.session.add(audit_log)
    db.session.commit()