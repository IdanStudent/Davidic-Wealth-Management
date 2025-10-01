from io import BytesIO
from base64 import b64encode
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.finance import Transaction, Category, CategoryType


def export_month_csv(db: Session, user_id: int, year: int, month: int):
    start = date(year, month, 1)
    end = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.date >= start, Transaction.date < end)
        .all()
    )
    out = ["date,amount,category,note"]
    for r in rows:
        cat = r.category.name if r.category else ""
        out.append(f"{r.date.isoformat()},{r.amount},{cat},{(r.note or '').replace(',', ';')}")
    content = "\n".join(out)
    filename = f"report_{year:04d}_{month:02d}.csv"
    return content, filename


def export_month_pdf(db: Session, user_id: int, year: int, month: int):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        # If reportlab is not installed, return placeholder
        content = b64encode(b"Install reportlab to generate PDFs").decode()
        return content, f"report_{year:04d}_{month:02d}.pdf"

    start = date(year, month, 1)
    end = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
    income = 0.0
    expenses = 0.0
    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.date >= start, Transaction.date < end)
        .all()
    )
    for r in rows:
        if r.category and r.category.type == CategoryType.INCOME:
            income += r.amount
        else:
            expenses += r.amount
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(72, 720, f"Monthly Report {year}-{month:02d}")
    c.drawString(72, 700, f"Income: {income:.2f}")
    c.drawString(72, 680, f"Expenses: {expenses:.2f}")
    c.drawString(72, 660, f"Savings: {income - expenses:.2f}")
    c.showPage()
    c.save()
    buf.seek(0)
    content_b64 = b64encode(buf.read()).decode()
    return content_b64, f"report_{year:04d}_{month:02d}.pdf"
