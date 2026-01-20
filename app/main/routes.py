from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime

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

    item = SocialItem(
        scenario_id=scenario.id,
        channel=request.form.get("channel"),
        region=request.form.get("region"),
        classification=request.form.get("classification"),
        urgency=request.form.get("urgency"),
        source=request.form.get("source"),
        title=request.form.get("title"),
        text=request.form.get("text"),
        image_url=request.form.get("image_url"),
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

    item = NewsItem(
        scenario_id=scenario.id,
        source=request.form.get("source"),
        title=request.form.get("title"),
        text=request.form.get("text"),
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

