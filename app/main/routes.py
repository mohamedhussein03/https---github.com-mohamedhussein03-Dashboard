from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import SocialResponse, NewsResponse



from app.models import AuthorityItem
from app.models import CallItem
from app.models import EmailItem
from app.models import WeatherItem
from app.models import LiveMonitorText
from app.models import SituationalStatus, ActionItem
from app.models import TaskTimer



import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app.models import MapItem





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

@main_bp.route("/")
@login_required
def dashboard():
    scenario = Scenario.query.filter_by(status="ACTIVE").first()

    if not scenario:
        return "No active scenario configured", 500

    social_items = SocialItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(SocialItem.created_at.desc()).all()

    news_items = NewsItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(NewsItem.created_at.desc()).all()

    latest_calls = (
        CallItem.query
        .filter_by(scenario_id=scenario.id)
        .order_by(CallItem.created_at.desc())
        .limit(5)
        .all()
    )

    authorities = AuthorityItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(AuthorityItem.created_at.desc()).all()

    timeline = TimelineEvent.query.filter_by(
        scenario_id=scenario.id
    ).order_by(TimelineEvent.created_at.asc()).all()

    breaking_items = (
        SocialItem.query
        .filter_by(scenario_id=scenario.id, urgency="HIGH")
        .order_by(SocialItem.created_at.desc())
        .limit(10)
        .all()
    )

    emails = EmailItem.query.filter_by(
        scenario_id=scenario.id
    ).order_by(EmailItem.created_at.desc()).all()

    rumors_count = SocialItem.query.filter_by(
        scenario_id=scenario.id,
        classification="rumor"
    ).count()

    weather_items = (
        WeatherItem.query
        .filter_by(scenario_id=scenario.id)
        .order_by(WeatherItem.created_at.desc())
        .all()
    )

    map_items = (
        MapItem.query
        .filter_by(scenario_id=scenario.id)
        .order_by(MapItem.created_at.desc())
        .all()
    )

    situational_items = (
        SituationalStatus.query
        .filter_by(scenario_id=scenario.id)
        .order_by(SituationalStatus.created_at.desc())
        .all()
    )


  


    action_items = (
        ActionItem.query
        .filter_by(scenario_id=scenario.id)
        .order_by(ActionItem.created_at.desc())
        .all()
    )

    task_timer = TaskTimer.query.filter_by(
        scenario_id=scenario.id
    ).first()

    calls_count = CallItem.query.filter_by(
        scenario_id=scenario.id
    ).count()

    counts = {
        "social": len(social_items),
        "news": len(news_items),
        "calls": calls_count,
        "emails": len(emails),
        "authority": len(authorities),
        "rumors": rumors_count
    }
    


    live_monitor_text = LiveMonitorText.query.filter_by(
        scenario_id=scenario.id
    ).first()

    return render_template(
        "dashboard/home.html",
        scenario=scenario,
        counts=counts,
        social_items=social_items,
        news_items=news_items,
        latest_calls=latest_calls,
        authorities=authorities,
        timeline=timeline,
        breaking_items=breaking_items,
        weather_items=weather_items,
        map_items=map_items,
        situational_items=situational_items,
        action_items=action_items,
        task_timer=task_timer,
        live_monitor_text=live_monitor_text,
        datetime=datetime,
        is_admin=(current_user.role == "admin")
    )



@main_bp.route("/authority")
@login_required
def authority():
    scenario = Scenario.query.filter_by(status="ACTIVE").first()

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
    scenario = Scenario.query.filter_by(status="ACTIVE").first()

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
    scenario = Scenario.query.filter_by(status="ACTIVE").first()

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
    active = Scenario.query.filter_by(status="ACTIVE").first()
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

    scenario = Scenario.query.filter_by(status="ACTIVE").first()

    item = SocialItem(
        scenario_id=scenario.id,
        channel=request.form.get("channel"),
        region=request.form.get("region"),
        classification=request.form.get("classification"),
        urgency=request.form.get("urgency"),
        source=request.form.get("source"),
        title=request.form.get("title"),
        text=request.form.get("text"),
        image_url=request.form.get("image_url"),   # CHANGED
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

    scenario = Scenario.query.filter_by(status="ACTIVE").first()

    item = NewsItem(
        scenario_id=scenario.id,
        source=request.form.get("source"),
        title=request.form.get("title"),
        text=request.form.get("text"),
        image_url=request.form.get("image_url"),   # CHANGED
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

    scenario = Scenario.query.filter_by(status="ACTIVE").first()


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

    scenario = Scenario.query.filter_by(status="ACTIVE").first()

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

    scenario = Scenario.query.filter_by(status="ACTIVE").first()

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

    # Archive all existing incidents
    Scenario.query.update({Scenario.status: "ARCHIVED"})
    db.session.commit()

    # Create new ACTIVE incident
    incident = Scenario(
        title=request.form.get("title"),
        location=request.form.get("location"),
        sector=request.form.get("sector"),
        timezone=request.form.get("timezone"),
        window=request.form.get("window"),
        description=request.form.get("description"),
        status="ACTIVE"
    )

    db.session.add(incident)
    db.session.commit()

    return redirect(url_for("main.incidents"))



@main_bp.route("/incidents/remove", methods=["POST"])
@login_required
def remove_incident():
    if current_user.role != "admin":
        return redirect(url_for("main.incidents"))

    active = Scenario.query.filter_by(status="ACTIVE").first()
    if active:
        db.session.delete(active)
        db.session.commit()

    return redirect(url_for("main.incidents"))




def _allowed_image(filename: str) -> bool:
    if not filename:
        return False
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_IMAGE_EXTENSIONS", set())


def _save_image(file_storage, subdir: str) -> str | None:
    if not file_storage:
        return None

    filename = file_storage.filename or ""
    if filename.strip() == "":
        return None

    if not _allowed_image(filename):
        return None

    safe_name = secure_filename(filename)
    uid = uuid.uuid4().hex
    final_name = f"{uid}_{safe_name}"

    upload_root = current_app.config["UPLOAD_FOLDER"]
    target_dir = os.path.join(upload_root, subdir)
    os.makedirs(target_dir, exist_ok=True)

    abs_path = os.path.join(target_dir, final_name)
    file_storage.save(abs_path)

    return f"uploads/{subdir}/{final_name}"


def _delete_image(rel_path: str | None) -> None:
    if not rel_path:
        return
    if not rel_path.startswith("uploads/"):
        return

    abs_path = os.path.join(current_app.root_path, "static", rel_path)
    try:
        if os.path.exists(abs_path):
            os.remove(abs_path)
    except OSError:
        pass


@main_bp.route("/social/<int:item_id>/edit", methods=["POST"])
@login_required
def edit_social(item_id: int):
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    item = SocialItem.query.get_or_404(item_id)

    item.channel = request.form.get("channel")
    item.region = request.form.get("region")
    item.classification = request.form.get("classification")
    item.urgency = request.form.get("urgency")
    item.source = request.form.get("source")
    item.title = request.form.get("title")
    item.text = request.form.get("text")
    item.tags = request.form.get("tags")

    new_image = request.files.get("image")
    if new_image and (new_image.filename or "").strip() != "":
        old = item.image_path
        image_rel = _save_image(new_image, "social")
        if image_rel:
            item.image_path = image_rel
            _delete_image(old)

    db.session.commit()
    return redirect(url_for("main.dashboard"))


@main_bp.route("/news/<int:item_id>/edit", methods=["POST"])
@login_required
def edit_news(item_id: int):
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    item = NewsItem.query.get_or_404(item_id)

    item.source = request.form.get("source")
    item.title = request.form.get("title")
    item.text = request.form.get("text")

    new_image = request.files.get("image")
    if new_image and (new_image.filename or "").strip() != "":
        old = item.image_path
        image_rel = _save_image(new_image, "news")
        if image_rel:
            item.image_path = image_rel
            _delete_image(old)

    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main_bp.route("/weather/add", methods=["POST"])
@login_required
def add_weather():
    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    weather = WeatherItem(
        scenario_id=scenario.id,
        temperature_c=float(request.form.get("temperature_c")),
        feels_like_c=float(request.form.get("feels_like_c")) if request.form.get("feels_like_c") else None,
        humidity=int(request.form.get("humidity")) if request.form.get("humidity") else None,
        air_quality=request.form.get("air_quality"),
    )

    db.session.add(weather)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/media")
@login_required
def media():
    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return "No active scenario", 500

    social_items = (
        SocialItem.query
        .filter_by(scenario_id=scenario.id)
        .order_by(SocialItem.created_at.desc())
        .all()
    )

    news_items = (
        NewsItem.query
        .filter_by(scenario_id=scenario.id)
        .order_by(NewsItem.created_at.desc())
        .all()
    )
    news_responses = NewsResponse.query.filter_by(
        scenario_id=scenario.id
    ).order_by(NewsResponse.created_at.desc()).all()

    social_responses = SocialResponse.query.filter_by(
        scenario_id=scenario.id
    ).order_by(SocialResponse.created_at.desc()).all()

    counts = {
        "social": len(social_items),
        "news": len(news_items)
    }

    return render_template(
        "dashboard/media.html",
        social_items=social_items,
        news_items=news_items,
        counts=counts,
        social_responses=social_responses,
        news_responses=news_responses,
        is_admin=(current_user.role == "admin")
    )

@main_bp.route("/map/add", methods=["POST"])
@login_required
def add_map():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    item = MapItem(
        scenario_id=scenario.id,
        image_url=request.form.get("image_url"),
        description=request.form.get("description")
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/live-monitor/save", methods=["POST"])
@login_required
def save_live_monitor():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    text = request.form.get("text", "").strip()
    if not text:
        return redirect(url_for("main.dashboard"))

    existing = LiveMonitorText.query.filter_by(scenario_id=scenario.id).first()

    if existing:
        existing.text = text
    else:
        db.session.add(
            LiveMonitorText(
                scenario_id=scenario.id,
                text=text
            )
        )

    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main_bp.route("/situational/add", methods=["POST"])
@login_required
def add_situational_status():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    title = request.form.get("title", "").strip()
    text = request.form.get("text", "").strip()

    if not title or not text:
        return redirect(url_for("main.dashboard"))

    item = SituationalStatus(
        scenario_id=scenario.id,
        title=title,
        text=text
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))


@main_bp.route("/situational/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_situational_status(item_id):
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    item = SituationalStatus.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/actions/add", methods=["POST"])
@login_required
def add_action_item():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    action = request.form.get("action", "").strip()
    description = request.form.get("description", "").strip()
    owner = request.form.get("owner", "").strip()
    stakeholder = request.form.get("stakeholder", "").strip()
    status = request.form.get("status", "none")

    if not action or not description or not owner or not stakeholder:
        return redirect(url_for("main.dashboard"))

    item = ActionItem(
        scenario_id=scenario.id,
        action=action,
        description=description,
        owner=owner,
        stakeholder=stakeholder,
        status=status
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/actions/<int:item_id>/edit", methods=["POST"])
@login_required
def edit_action_item(item_id):
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    item = ActionItem.query.get_or_404(item_id)

    item.action = request.form.get("action", item.action)
    item.description = request.form.get("description", item.description)
    item.owner = request.form.get("owner", item.owner)
    item.stakeholder = request.form.get("stakeholder", item.stakeholder)
    item.status = request.form.get("status", item.status)

    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/actions/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_action_item(item_id):
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    item = ActionItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/map/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_map_item(item_id):
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    item = MapItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/timer/create", methods=["POST"])
@login_required
def create_task_timer():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    title = request.form.get("title", "").strip()
    minutes = request.form.get("minutes", type=int)

    attendees = request.form.get("attendees", "").strip()
    next_meeting = request.form.get("next_meeting", "").strip()
    location = request.form.get("location", "").strip()

    if not title or not minutes:
        return redirect(url_for("main.dashboard"))

    existing = TaskTimer.query.filter_by(scenario_id=scenario.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    end_time = datetime.utcnow() + timedelta(minutes=minutes)

    timer = TaskTimer(
        scenario_id=scenario.id,
        title=title,
        end_time=end_time,
        attendees=attendees,
        next_meeting=next_meeting,
        location=location
    )

    db.session.add(timer)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/timer/clear", methods=["POST"])
@login_required
def clear_task_timer():
    if current_user.role != "admin":
        return redirect(url_for("main.dashboard"))

    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.dashboard"))

    timer = TaskTimer.query.filter_by(scenario_id=scenario.id).first()
    if timer:
        db.session.delete(timer)
        db.session.commit()

    return redirect(url_for("main.dashboard"))

@main_bp.route("/social-response/add", methods=["POST"])
def add_social_response():
    scenario = Scenario.query.filter_by(status="ACTIVE").first()

    item = SocialResponse(
        scenario_id=scenario.id,
        title=request.form.get("title"),
        text=request.form.get("text")
    )

    db.session.add(item)
    db.session.commit()

    return redirect(request.referrer or url_for("main.media"))


@main_bp.route("/social-response/<int:item_id>/delete", methods=["POST"])
def delete_social_response(item_id):
    item = SocialResponse.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.commit()

    return redirect(request.referrer or url_for("main.media"))



@main_bp.route("/news-response/add", methods=["POST"])
@login_required
def add_news_response():
    scenario = Scenario.query.filter_by(status="ACTIVE").first()
    if not scenario:
        return redirect(url_for("main.media"))

    item = NewsResponse(
        scenario_id=scenario.id,
        title=request.form["title"],
        text=request.form["text"]
    )

    db.session.add(item)
    db.session.commit()

    return redirect(request.referrer or url_for("main.media"))



@main_bp.route("/news-response/<int:item_id>/delete", methods=["POST"])
def delete_news_response(item_id):
    item = NewsResponse.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.commit()

    return redirect(request.referrer or url_for("main.media"))

