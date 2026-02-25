import qrcode
import json
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from PIL import Image as PILImage, ImageFilter


def generate_event_pass_pdf(participant):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    event = participant.event_id

    # ================= CARD SIZE & POSITION (CENTERED) =================
    card_width = width - 100
    card_height = 280

    card_x = (width - card_width) / 2
    card_y = (height - card_height) / 2

    left_width = card_width * 0.65
    right_width = card_width * 0.35

    # ================= OUTER BORDER =================
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.2)
    c.roundRect(card_x, card_y, card_width, card_height, 15, stroke=1, fill=0)

    # ================= BACKGROUND IMAGE =================
    if event.image:
        try:
            original = PILImage.open(event.image.path)
            blurred = original.filter(ImageFilter.GaussianBlur(radius=6))

            img_buffer = BytesIO()
            blurred.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            bg_image = ImageReader(img_buffer)

            c.drawImage(
                bg_image,
                card_x,
                card_y,
                width=left_width,
                height=card_height,
                mask='auto'
            )
        except Exception as e:
            print("Image error:", e)

    # ================= DARK OVERLAY =================
    c.setFillColorRGB(0, 0, 0)
    c.setFillAlpha(0.45)
    c.roundRect(card_x, card_y, left_width, card_height, 15, stroke=0, fill=1)
    c.setFillAlpha(1)

    # ================= EVENT TEXT =================
    text_x = card_x + 25
    text_y = card_y + card_height - 50

    c.setFillColor(colors.white)

    # Event Name
    c.setFont("Helvetica-Bold", 22)
    c.drawString(text_x, text_y, event.event_name or "Event Name")

    # Date & Time
    c.setFont("Helvetica", 13)
    c.drawString(text_x, text_y - 35,
                 f"Date & Time: {event.event_date_time}")

    # Venue
    c.drawString(text_x, text_y - 60,
                 f"Venue: {event.venue}")

    # Participant Name
    c.setFont("Helvetica-Bold", 14)
    if participant.user_id:
        name = participant.user_id.full_name
    else:
        name = participant.full_name

    c.drawString(text_x, text_y - 100,
                f"Name: {name}")
    

    # ================= RIGHT SIDE (QR SECTION) =================
    if participant.user_id:
        # Registered User (RegUser)
        reg_user = participant.user_id

        qr_data = {
            "user_id": reg_user.user_id,
            "full_name": reg_user.full_name,
            "mobile_number": reg_user.phone,
            "email": reg_user.email,
        }

    else:
        # Guest User
        qr_data = {
            "user_id": None,
            "full_name": participant.full_name,
            "mobile_number": participant.phone,
            "email": participant.email,
        }

    qr = qrcode.make(json.dumps(qr_data))
    qr_buffer = BytesIO()  
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)

    qr_size = 2 * inch

    qr_x = card_x + left_width + (right_width - qr_size) / 2
    qr_y = card_y + (card_height - qr_size) / 2

    c.drawImage(qr_image, qr_x, qr_y,
                width=qr_size, height=qr_size)

    # QR Label
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(
        card_x + left_width + right_width / 2,
        qr_y - 20,
        "Scan for Entry"
    )

    # ================= FOOTER NOTE =================
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(
        width / 2,
        card_y - 15,
        "This pass is system generated and valid only with QR verification"
    )

    c.showPage()
    c.save()

    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"event_pass_{participant.id}.pdf")