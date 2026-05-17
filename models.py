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



def model_to_dict(model):
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }