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

    # Database-level CHECK constraints
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
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    shortlists = db.relationship("CloudShortlist", backref="user", lazy=True)


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
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating"),
    )


def model_to_dict(model):
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }