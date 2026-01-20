import os
import imghdr
from uuid import uuid4

from flask import Blueprint, render_template, request, redirect, url_for, current_app, abort
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from app.models import AuthorityItem
from app.models import CallItem
from app.models import EmailItem



from app.extensions import db
from app.models import (
    Scenario,
    SocialItem,
    NewsItem,
    CallItem,
    AuthorityItem,
    TimelineEvent
)

main_bp = Blueprint("main", __name__)


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_IMAGE_MIMETYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


def _is_allowed_image_upload(file_storage) -> bool:
    if not file_storage or not getattr(file_storage, "filename", ""):
        return False

    filename = secure_filename(file_storage.filename or "")
    if "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False

    mimetype = (file_storage.mimetype or "").lower()
    if mimetype not in ALLOWED_IMAGE_MIMETYPES:
        return False

    # Verify content is actually an image by signature (best-effort)
    head = file_storage.stream.read(512)
    file_storage.stream.seek(0)
    kind = imghdr.what(None, h=head)
    if kind is None:
        return False

    # imghdr returns 'jpeg' for jpg/jpeg; normalize webp/gif/png already match
    if kind == "jpeg":
        kind_ext = "jpg"
    else:
        kind_ext = kind

    if kind_ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False

    return True


def _save_uploaded_image(file_storage) -> str:
    """
    Saves a validated image upload under app/static/uploads and returns the
    URL path like /static/uploads/<filename>
    """
    if not _is_allowed_image_upload(file_storage):
        abort(400, description="Invalid image upload")

    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    if not upload_folder:
        abort(500, description="UPLOAD_FOLDER not configured")

    os.makedirs(upload_folder, exist_ok=True)

    safe_name = secure_filename(file_storage.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    final_name = f"{uuid4().hex}.{ext}"

    save_path = os.path.join(upload_folder, final_name)
    file_storage.save(save_path)

    return f"/static/uploads/{final_name}"

@main_bp.route("/")
@login_required
def dashboard():
    scenario = Scenario.query.filter_by(is_active=True).first()

    if not scenario:
        return "No active scenario configured", 500

    social_items = SocialItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(SocialItem.created_at.desc()).all()

    news_items = NewsItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(NewsItem.created_at.desc()).all()

    calls = CallItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(CallItem.created_at.desc()).all()

    authorities = AuthorityItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(AuthorityItem.created_at.desc()).all()

    timeline = TimelineEvent.query.filter_by(
        scenario_id=scenario.id
    ).order_by(TimelineEvent.created_at.asc()).all()

    ticker_items = [t.description for t in timeline[-3:]]

    counts = {
        "social": len(social_items),
        "news": len(news_items),
        "calls": len(calls),
        "emails": 0,
        "authority": len(authorities),
        "rumors": 0
    }

    return render_template(
        "dashboard/home.html",
        scenario=scenario,
        counts=counts,
        social_items=social_items,
        news_items=news_items,
        calls=calls,
        authorities=authorities,
        timeline=timeline,
        ticker_items=ticker_items,
        is_admin=(current_user.role == "admin")
    )


@main_bp.route("/authority")
@login_required
def authority():
    scenario = Scenario.query.filter_by(is_active=True).first()

    authorities = AuthorityItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(AuthorityItem.created_at.desc()).all()

    return render_template(
        "dashboard/authority.html",
        authorities=authorities,
        is_admin=(current_user.role == "admin")
    )




@main_bp.route("/calls")
@login_required
def calls():
    scenario = Scenario.query.filter_by(is_active=True).first()
    if not scenario:
        return "No active scenario", 500

    call_items = CallItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(CallItem.created_at.desc()).all()

    return render_template(
        "dashboard/calls.html",
        calls=call_items,
        is_admin=(current_user.role == "admin")
    )



@main_bp.route("/emails")
@login_required
def emails():
    scenario = Scenario.query.filter_by(is_active=True).first()

    if not scenario:
        return "No active scenario", 200

    emails = EmailItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(EmailItem.created_at.desc()).all()

    return render_template(
        "dashboard/emails.html",
        scenario=scenario,
        emails=emails,
        is_admin=(current_user.role == "admin")
    )



@main_bp.route("/incidents")
@login_required
def incidents():
    active = Scenario.query.filter_by(is_active=True).first()
    return render_template(
        "dashboard/incidents.html",
        incident=active,
        is_admin=(current_user.role == "admin")
    )


@main_bp.route("/social/add", methods=["POST"])
@login_required
def add_social():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(is_active=True).first()

    uploaded = request.files.get("image_file")
    uploaded_url = None
    if uploaded and uploaded.filename:
        uploaded_url = _save_uploaded_image(uploaded)

    image_url = uploaded_url or request.form.get("image_url")

    item = SocialItem(
        scenario_id=scenario.id,
        channel=request.form.get("channel"),
        region=request.form.get("region"),
        classification=request.form.get("classification"),
        urgency=request.form.get("urgency"),
        source=request.form.get("source"),
        title=request.form.get("title"),
        text=request.form.get("text"),
        image_url=image_url,
        tags=request.form.get("tags"),
        created_at=datetime.utcnow()
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))


@main_bp.route("/news/add", methods=["POST"])
@login_required
def add_news():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(is_active=True).first()

    uploaded = request.files.get("image_file")
    uploaded_url = None
    if uploaded and uploaded.filename:
        uploaded_url = _save_uploaded_image(uploaded)

    image_url = uploaded_url or request.form.get("image_url")

    item = NewsItem(
        scenario_id=scenario.id,
        source=request.form.get("source"),
        title=request.form.get("title"),
        text=request.form.get("text"),
        image_url=image_url,
        created_at=datetime.utcnow()
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))


@main_bp.route("/calls/add", methods=["POST"])
@login_required
def add_call():
    if current_user.role != "admin":
        return redirect(url_for("main.calls"))

    scenario = Scenario.query.filter_by(is_active=True).first()

    item = CallItem(
    scenario_id=scenario.id,
    caller=request.form.get("caller"),
    summary=request.form.get("summary"),
    urgency=request.form.get("urgency"),
    is_media=bool(request.form.get("is_media")),
    is_local=bool(request.form.get("is_local")),
    is_inbound=bool(request.form.get("is_inbound")),
    created_at=datetime.utcnow()
    )   

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.calls"))


@main_bp.route("/authority/add", methods=["POST"])
@login_required
def add_authority():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(is_active=True).first()

    item = AuthorityItem(
        scenario_id=scenario.id,
        authority_name=request.form.get("authority"),
        action=request.form.get("action"),
        status=request.form.get("status"),
        created_at=datetime.utcnow()
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/emails/add", methods=["POST"])
@login_required
def add_email():
    if current_user.role != "admin":
        return redirect(url_for("main.emails"))

    scenario = Scenario.query.filter_by(is_active=True).first()

    item = EmailItem(
        scenario_id=scenario.id,
        sender=request.form.get("sender"),
        subject=request.form.get("subject"),
        body=request.form.get("body"),
        urgency=request.form.get("urgency"),
        created_at=datetime.utcnow()
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.emails"))

@main_bp.route("/incidents/add", methods=["POST"])
@login_required
def add_incident():
    if current_user.role != "admin":
        return redirect(url_for("main.incidents"))

    Scenario.query.update({Scenario.is_active: False})

    incident = Scenario(
        title=request.form.get("title"),
        location=request.form.get("location"),
        sector=request.form.get("sector"),
        timezone=request.form.get("timezone"),
        status="ACTIVE",
        window=request.form.get("window"),
        description=request.form.get("description"),
        is_active=True
    )

    db.session.add(incident)
    db.session.commit()

    return redirect(url_for("main.incidents"))


@main_bp.route("/incidents/remove", methods=["POST"])
@login_required
def remove_incident():
    if current_user.role != "admin":
        return redirect(url_for("main.incidents"))

    active = Scenario.query.filter_by(is_active=True).first()
    if active:
        db.session.delete(active)
        db.session.commit()

    return redirect(url_for("main.incidents"))

