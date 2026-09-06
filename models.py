from db import db


class SeatInfo(db.Model):
    __tablename__ = "SeatInfo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    college_name = db.Column(db.Text, nullable=False)

    college_type = db.Column(
        db.Text,
        nullable=False
    )  # Allowed: GOVT, Private, S.F.I.

    branch = db.Column(db.Text, nullable=False)

    opening_rank = db.Column(db.Integer, nullable=False)
    closing_rank = db.Column(db.Integer, nullable=False)

    category = db.Column(
        db.Text,
        nullable=False
    )  # Allowed: UR, OBC, SC, ST

    gender = db.Column(
        db.Text,
        nullable=False
    )  # Allowed: M, F, OP

    domicile = db.Column(
        db.Text,
        nullable=False
    )  # Allowed: Y, N

    total_seats = db.Column(db.Integer, nullable=False)

    year = db.Column(db.Integer, nullable=False)

    # Database-level CHECK constraints and Performance Indexes
    __table_args__ = (
        db.CheckConstraint(
            "college_type IN ('GOVT', 'Private', 'S.F.I.')",
            name="check_college_type"
        ),
        db.CheckConstraint(
            "category IN ('UR', 'OBC', 'SC', 'ST')",
            name="check_category"
        ),
        db.CheckConstraint(
            "gender IN ('M', 'F', 'OP')",
            name="check_gender"
        ),
        db.CheckConstraint(
            "domicile IN ('Y', 'N')",
            name="check_domicile"
        ),
        db.Index('idx_seatinfo_search', 'year', 'category', 'domicile', 'closing_rank', 'gender'),
        db.Index('idx_seatinfo_college', 'college_name'),
        db.Index('idx_seatinfo_branch', 'branch'),
    )

    def __repr__(self):
        return (
            f"<SeatInfo {self.college_name} - {self.branch} "
            f"({self.category}, {self.year})>"
        )





class CgpaRankRange(db.Model):
    __tablename__ = "CgpaRankRange"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    cgpa = db.Column(db.Float, nullable=False)

    min_rank = db.Column(db.Integer, nullable=False)
    max_rank = db.Column(db.Integer, nullable=False)

    year = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.Index('idx_cgparank_year_cgpa', 'year', 'cgpa'),
    )

    def __repr__(self):
        return (
            f"<CgpaRankRange CGPA={self.cgpa}, "
            f"Rank={self.min_rank}-{self.max_rank}, "
            f"Year={self.year}>"
        )



class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    mobile_number = db.Column(db.String(15), nullable=True)
    polytechnic_college = db.Column(db.String(255), nullable=True)
    diploma_branch = db.Column(db.String(100), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(10), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    notify_counselling = db.Column(db.Integer, default=1)
    coupon_used = db.Column(db.String(50), nullable=True)
    referred_by_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=True)
    predictions_today = db.Column(db.Integer, default=0)
    last_prediction_date = db.Column(db.String(20), nullable=True)
    is_premium = db.Column(db.Boolean, default=False)
    coins = db.Column(db.Integer, default=0, nullable=False)
    current_session_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    shortlists = db.relationship("CloudShortlist", backref="user", lazy=True)
    referred_by = db.relationship("User", remote_side=[id], backref="referred_students")

    @property
    def has_unlimited_access(self):
        import os
        admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
        is_admin = (self.email.strip().lower() == admin_email)
        return is_admin or bool(self.is_premium)

    @property
    def daily_prediction_limit(self):
        if self.has_unlimited_access:
            return 99999
        limit = 5
        if self.referred_by_id is not None:
            limit += 5
        limit += len(self.referred_students) * 5
        return limit

    @property
    def remaining_predictions(self):
        if self.has_unlimited_access:
            return 99999
        return max(0, self.daily_prediction_limit - (self.predictions_today or 0))

    @property
    def coupon_details(self):
        if self.coupon_used and not self.referred_by_id:
            from models import Coupon
            return Coupon.query.filter_by(code=self.coupon_used).first()
        return None



class CloudShortlist(db.Model):
    __tablename__ = "CloudShortlist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    name = db.Column(db.String(120), default="My Shortlist")
    items_json = db.Column(db.Text, nullable=False, default="[]")
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class CollegeReview(db.Model):
    __tablename__ = "CollegeReview"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_name = db.Column(db.Text, nullable=False, index=True)
    author_name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=False)
    branch = db.Column(db.String(32), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating"),
    )


class ChoiceVault(db.Model):
    __tablename__ = "ChoiceVault"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.String(50), nullable=False)
    roll_no = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    focus = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class VisitorCount(db.Model):
    __tablename__ = "VisitorCount"

    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=0)


class Coupon(db.Model):
    __tablename__ = "Coupon"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_by = db.Column(db.String(100), default="admin")  # "admin" or referrer user ID
    for_whom = db.Column(db.String(100), nullable=True)  # Name/Description for whom/what code was made
    is_active = db.Column(db.Boolean, default=True)
    coins_reward = db.Column(db.Integer, default=50, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Coupon {self.code} (Active={self.is_active})>"


class RecommendationChoice(db.Model):
    __tablename__ = "RecommendationChoice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sn = db.Column(db.Integer, nullable=False)
    db_name = db.Column(db.Text, nullable=False)
    branch = db.Column(db.Text, nullable=False)
    display_name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<RecommendationChoice SN={self.sn} {self.display_name}>"


class SiteSetting(db.Model):
    __tablename__ = "SiteSetting"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)

    @classmethod
    def get(cls, key, default=""):
        try:
            setting = cls.query.filter_by(key=key).first()
            return setting.value if setting else str(default)
        except Exception:
            db.session.rollback()
            return str(default)

    @classmethod
    def set(cls, key, value):
        try:
            setting = cls.query.filter_by(key=key).first()
            if not setting:
                setting = cls(key=key, value=str(value))
                db.session.add(setting)
            else:
                setting.value = str(value)
            db.session.commit()
        except Exception:
            db.session.rollback()


def get_referral_coins():
    try:
        val = SiteSetting.get('referral_coins_reward', '50')
        return int(val)
    except Exception:
        return 50


def model_to_dict(model):
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }