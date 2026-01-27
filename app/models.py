from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)


class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    sector = db.Column(db.String(100))
    timezone = db.Column(db.String(50))

    status = db.Column(db.String(20), default="ACTIVE")
    window = db.Column(db.String(100))
    description = db.Column(db.Text)

    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    social_items = db.relationship("SocialItem", backref="scenario", lazy=True)
    news_items = db.relationship("NewsItem", backref="scenario", lazy=True)
    calls = db.relationship("CallItem", backref="scenario", lazy=True)
    emails = db.relationship("EmailItem", backref="scenario", lazy=True)
    authorities = db.relationship("AuthorityItem", backref="scenario", lazy=True)
    timeline = db.relationship("TimelineEvent", backref="scenario", lazy=True)
    weather_items = db.relationship("WeatherItem", backref="scenario", lazy=True)
    map_items = db.relationship("MapItem", backref="scenario", lazy=True)




from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class SocialItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    channel = db.Column(db.String(50))
    region = db.Column(db.String(50))
    classification = db.Column(db.String(50))
    urgency = db.Column(db.String(50))
    source = db.Column(db.String(200))
    title = db.Column(db.String(200))
    text = db.Column(db.Text)

    image_path = db.Column(db.String(500))
    image_url = db.Column(db.Text) 
    tags = db.Column(db.String(300))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NewsItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    source = db.Column(db.String(200))
    title = db.Column(db.String(200))
    text = db.Column(db.Text)

    image_url = db.Column(db.Text)
    image_path = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class CallItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    caller = db.Column(db.String(200))
    summary = db.Column(db.Text)
    urgency = db.Column(db.String(20))

    is_media = db.Column(db.Boolean, default=False)
    is_local = db.Column(db.Boolean, default=False)
    is_inbound = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    sender = db.Column(db.String(200))
    subject = db.Column(db.String(300))
    body = db.Column(db.Text)
    urgency = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuthorityItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    authority_name = db.Column(db.String(200))
    action = db.Column(db.Text)
    status = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    time_label = db.Column(db.String(50))
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    temperature_c = db.Column(db.Float, nullable=False)
    feels_like_c = db.Column(db.Float)
    humidity = db.Column(db.Integer)
    air_quality = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MapItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LiveMonitorText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    text = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scenario = db.relationship("Scenario", backref=db.backref("live_monitor_text", uselist=False))

class SituationalStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scenario = db.relationship(
        "Scenario",
        backref=db.backref(
            "situational_statuses",
            lazy=True,
            order_by="desc(SituationalStatus.created_at)"
        )
    )

class ActionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    action = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner = db.Column(db.String(120), nullable=False)
    stakeholder = db.Column(db.String(120), nullable=False)

    status = db.Column(db.String(20), nullable=False, default="none")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scenario = db.relationship(
        "Scenario",
        backref=db.backref(
            "action_items",
            lazy=True,
            order_by="desc(ActionItem.created_at)"
        )
    )

class TaskTimer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    attendees = db.Column(db.Text)
    next_meeting = db.Column(db.Text)
    location = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scenario = db.relationship(
        "Scenario",
        backref=db.backref(
            "task_timer",
            uselist=False
        )
    )

class SocialResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(
        db.Integer,
        db.ForeignKey("scenario.id"),
        nullable=False
    )

    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class NewsResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(
        db.Integer,
        db.ForeignKey("scenario.id"),
        nullable=False
    )

    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
