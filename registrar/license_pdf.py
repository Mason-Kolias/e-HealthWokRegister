from io import BytesIO
import os
from django.contrib.staticfiles import finders
from django.conf import settings

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import black, white, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# ============================================================
# HELPERS
# ============================================================

def _safe_text(value, fallback="Not Provided"):
    if value is None:
        return fallback

    value = str(value).strip()

    return value if value else fallback


def _display_choice(value):
    value = _safe_text(value)

    if value == "Not Provided":
        return value

    return value.replace("_", " ").title()


def _draw_fitted_text(
    pdf,
    text,
    x,
    y,
    max_width,
    font_name="Helvetica",
    font_size=9,
    min_font_size=6.5,
):
    """
    Draw text while automatically reducing the font size
    if the value is too wide for the available space.
    """

    text = _safe_text(text)

    current_size = font_size

    while current_size > min_font_size:
        width = pdf.stringWidth(
            text,
            font_name,
            current_size,
        )

        if width <= max_width:
            break

        current_size -= 0.25

    pdf.setFont(
        font_name,
        current_size,
    )

    pdf.drawString(
        x,
        y,
        text,
    )


def _draw_centred_fitted_text(
    pdf,
    text,
    centre_x,
    y,
    max_width,
    font_name="Helvetica-Bold",
    font_size=15,
    min_font_size=8,
):
    text = _safe_text(text)

    current_size = font_size

    while current_size > min_font_size:
        width = pdf.stringWidth(
            text,
            font_name,
            current_size,
        )

        if width <= max_width:
            break

        current_size -= 0.25

    pdf.setFont(
        font_name,
        current_size,
    )

    pdf.drawCentredString(
        centre_x,
        y,
        text,
    )


# ============================================================
# MEDICAL LICENSE PDF
# ============================================================

def generate_license_pdf(application, license_record):

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=A4,
    )

    page_width, page_height = A4

    # --------------------------------------------------------
    # COLOURS
    # --------------------------------------------------------

    BLACK = black
    DARK = HexColor("#181818")
    GREY = HexColor("#555555")
    LIGHT_GREY = HexColor("#D8D8D8")
    VERY_LIGHT_GREY = HexColor("#F5F5F5")
    WHITE = white

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    issue_date = license_record.issue_date
    expiry_date = license_record.expiry_date
    license_number = _safe_text(
        license_record.license_number
    )

    applicant_name = (
        application.full_name
        or application.applicant.get_full_name()
        or application.applicant.username
        or "Not Provided"
    )

    applicant_name = _safe_text(
        applicant_name
    )

    profession = _safe_text(
        application.profession
    )

    registration_number = _safe_text(
         license_record.license_number
  
    ) 

    application_number = _safe_text(
        application.application_number
    )

    specialization = _safe_text(
        application.specialization,
        "Not Specified",
    )

    qualification = _safe_text(
        application.qualification
    )

    institution = _safe_text(
        application.institution
    )

    province = _safe_text(
        application.province
    )

    profession_display = _display_choice(
        profession
    )

    specialization_display = _display_choice(
        specialization
    )

    # --------------------------------------------------------
    # WHITE BACKGROUND
    # --------------------------------------------------------

    pdf.setFillColor(WHITE)

    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0,
    )

    # ========================================================
    # NATIONAL CREST
    # ========================================================
    
    crest_path=finders.find("registrar/images/licence_crest1.png")
    if not crest_path:
        raise FileNotFoundError(
             "Could not find registrar/images/licence_crest1.png"
        )
        
    print("LICENSE CREST PATH:", crest_path)
    crest = ImageReader(crest_path)
    original_width, original_height = crest.getSize()
    print(
    "LICENSE CREST SIZE:",
    original_width,
    original_height,
)
   # Maximum area reserved for crest
    max_width=50*mm
    max_height=35*mm

# Preserve original aspect ratio
    scale =min(
    max_width / original_width,
    max_height / original_height,
)
    crest_width=original_width*scale
    crest_height = original_height*scale
    
    crest_x = (
        page_width - crest_width
    )/2
    
    crest_y=(
    page_height
    - 12 * mm
    - crest_height
)
    pdf.drawImage(
        crest,
    crest_x,
    crest_y,
    width=crest_width,
    height=crest_height,
    preserveAspectRatio=True,
    mask="auto",
        
    )
    
    print("CREST DRAWN ON LICENSE")



    # ========================================================
    # GOVERNMENT HEADER
    # ========================================================

    header_y = page_height - 51 * mm

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Bold",
        13,
    )

    pdf.drawCentredString(
        page_width / 2,
        header_y,
        "PAPUA NEW GUINEA",
    )

    pdf.setFont(
        "Helvetica-Bold",
        9,
    )

    pdf.drawCentredString(
        page_width / 2,
        header_y - 6 * mm,
        "MINISTRY OF HEALTH",
    )

    pdf.setFont(
        "Helvetica-Bold",
        10,
    )

    pdf.drawCentredString(
        page_width / 2,
        header_y - 12 * mm,
        "MEDICAL BOARD OF PAPUA NEW GUINEA",
    )

    # ========================================================
    # LICENSE TITLE
    # ========================================================

    title_y = page_height - 82 * mm

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Bold",
        22,
    )

    pdf.drawCentredString(
        page_width / 2,
        title_y,
        "MEDICAL PRACTICE LICENSE",
    )

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica",
        8,
    )

    pdf.drawCentredString(
        page_width / 2,
        title_y - 7 * mm,
        "PROFESSIONAL REGISTRATION CREDENTIAL",
    )

    # ========================================================
    # LICENSE NUMBER AND STATUS
    # ========================================================

    info_y = page_height - 104 * mm

    left_x = 30 * mm
    right_x = page_width - 30 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.5,
    )

    pdf.drawString(
        left_x,
        info_y,
        "LICENSE NUMBER",
    )

    pdf.drawRightString(
        right_x,
        info_y,
        "STATUS",
    )

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Bold",
        11,
    )

    pdf.drawString(
        left_x,
        info_y - 6 * mm,
        license_number,
    )

    pdf.drawRightString(
        right_x,
        info_y - 6 * mm,
        "ACTIVE",
    )
    
    """
    
    # ========================================================
    # LICENSED TO
    # ========================================================

    licensed_y = page_height - 128 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        7,
    )

    pdf.drawCentredString(
        page_width / 2,
        licensed_y,
        "LICENSED TO",
    )

    pdf.setFillColor(BLACK)

    _draw_centred_fitted_text(
        pdf=pdf,
        text=applicant_name.upper(),
        centre_x=page_width / 2,
        y=licensed_y - 10 * mm,
        max_width=150 * mm,
        font_name="Helvetica-Bold",
        font_size=18,
        min_font_size=11,
    )

    # ========================================================
    # PROFESSIONAL INFORMATION
    # ========================================================

    details_y = page_height - 154 * mm

    column_left = 30 * mm
    column_right = 112 * mm

    value_width = 68 * mm

    # Profession

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_left,
        details_y,
        "PROFESSION",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        profession_display,
        column_left,
        details_y - 5 * mm,
        value_width,
        "Helvetica",
        9,
    )

    # Professional Registration Number

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_right,
        details_y,
        "PROFESSIONAL REGISTRATION NO.",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        registration_number,
        column_right,
        details_y - 5 * mm,
        65 * mm,
        "Helvetica",
        9,
    )

    # Specialization

    second_row_y = details_y - 16 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_left,
        second_row_y,
        "SPECIALIZATION",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        specialization_display,
        column_left,
        second_row_y - 5 * mm,
        value_width,
        "Helvetica",
        9,
    )

    # Application number

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_right,
        second_row_y,
        "APPLICATION NUMBER",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        application_number,
        column_right,
        second_row_y - 5 * mm,
        65 * mm,
        "Helvetica",
        9,
    )

    # ========================================================
    # QUALIFICATION INFORMATION
    # ========================================================

    education_y = page_height - 192 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_left,
        education_y,
        "QUALIFICATION",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        qualification,
        column_left,
        education_y - 5 * mm,
        value_width,
        "Helvetica",
        8.5,
    )

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_right,
        education_y,
        "INSTITUTION",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        institution,
        column_right,
        education_y - 5 * mm,
        65 * mm,
        "Helvetica",
        8.5,
    )

    province_y = education_y - 16 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        column_left,
        province_y,
        "PROVINCE",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        province,
        column_left,
        province_y - 5 * mm,
        value_width,
        "Helvetica",
        8.5,
    )

    # ========================================================
    # VALIDITY
    # ========================================================

    validity_y = page_height - 226 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.5,
    )

    pdf.drawString(
        column_left,
        validity_y,
        "DATE OF ISSUE",
    )

    pdf.drawString(
        column_right,
        validity_y,
        "DATE OF EXPIRY",
    )

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Bold",
        9,
    )

    pdf.drawString(
        column_left,
        validity_y - 6 * mm,
        issue_date.strftime(
            "%d %B %Y"
        ),
    )

    pdf.drawString(
        column_right,
        validity_y - 6 * mm,
        expiry_date.strftime(
            "%d %B %Y"
        ),
    )

    # ========================================================
    # CERTIFICATION
    # ========================================================
    certification_y = licensed_y - 20 * mm
    pdf.setFillColor(DARK)
    pdf.setFont(
    "Helvetica",
    7.3,
)
    certification_lines = [
    "This license certifies that the above-named person is",
    "registered as a health professional and is authorized",
    "to practice within the scope of the professional",
    "registration granted by the Medical Board.",
]
    line_y = certification_y
    for line in certification_lines:
        pdf.drawCentredString(
        page_width / 2,
        line_y,
        line,
    )

    line_y -= 4 * mm

    # ========================================================
    # LOWER AUTHENTICATION AREA
    # ========================================================

    lower_y = 18 * mm

    # --------------------------------------------------------
    # REGISTRAR
    # --------------------------------------------------------

    registrar_x = 28 * mm

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica-Bold",
        6.3,
    )

    pdf.drawString(
        registrar_x,
        lower_y + 34 * mm,
        "REGISTRAR",
    )

    # Stylized signature

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Oblique",
        14,
    )

    pdf.drawString(
        registrar_x + 2 * mm,
        lower_y + 24 * mm,
        "Alphonse Tay",
    )

    # Small signature baseline only.
    # This is not a decorative certificate border.

    pdf.setStrokeColor(
        HexColor("#777777")
    )

    pdf.setLineWidth(0.45)

    pdf.line(
        registrar_x,
        lower_y + 21 * mm,
        registrar_x + 52 * mm,
        lower_y + 21 * mm,
    )

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Bold",
        7.5,
    )

    pdf.drawString(
        registrar_x,
        lower_y + 16 * mm,
        "Dr. Alphonse Tay",
    )

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica",
        6.3,
    )

    pdf.drawString(
        registrar_x,
        lower_y + 11 * mm,
        "Registrar",
    )

    pdf.drawString(
        registrar_x,
        lower_y + 7 * mm,
        "Medical Board of Papua New Guinea",
    )

    # ========================================================
    # MEDICAL BOARD SEAL
    # ========================================================
    stamp_path=finders.find("registrar/images/mb_stamp.png")
    if not stamp_path:
        raise FileNotFoundError(
            "Could not find"
            "registrar/images/mb_stamp.png"
        )
        
    print("MEDICAL BOARD STAMP PATH:", stamp_path)
    stamp = ImageReader(stamp_path)
    original_stamp_width, original_stamp_height = stamp.getSize()
    print(
          "MEDICAL BOARD STAMP SIZE:",
    original_stamp_width,
    original_stamp_height,
)
    max_stamp_width=34*mm
    max_stamp_height=34*mm
    
    stamp_scale = min(
          max_stamp_width / original_stamp_width,
    max_stamp_height / original_stamp_height,
)
    
    stamp_width=original_stamp_width*stamp_scale
    stamp_height=original_stamp_height * stamp_scale
    
    stamp_x= (
        page_width - stamp_width
    )/ 2
    
    stamp_y = lower_y + 7 * mm
    pdf.drawImage(
    stamp,
    stamp_x,
    stamp_y,
    width=stamp_width,
    height=stamp_height,
    preserveAspectRatio=True,
    mask="auto",
)
    print("MEDICAL BOARD STAMP DRAWN")
    
    
    
    
  

    # ========================================================
    # QR CODE
    # ========================================================

    qr_size = 25 * mm

    qr_x = (
        page_width
        - 28 * mm
        - qr_size
    )

    qr_y = lower_y + 10 * mm

    # No e-HealthWorkRegister branding in QR data.

    verification_data = (
        "Medical Practice License\n"
        f"License No: {license_number}\n"
        f"Name: {applicant_name}\n"
        f"Profession: {profession_display}\n"
        "Status: ACTIVE\n"
        f"Issue Date: "
        f"{issue_date.strftime('%d %B %Y')}\n"
        f"Expiry Date: "
        f"{expiry_date.strftime('%d %B %Y')}\n"
        f"Application No: {application_number}"
    )

    qr_code = qr.QrCodeWidget(
        verification_data
    )

    bounds = qr_code.getBounds()

    qr_width = (
        bounds[2] - bounds[0]
    )

    qr_height = (
        bounds[3] - bounds[1]
    )

    qr_drawing = Drawing(
        qr_size,
        qr_size,
        transform=[
            qr_size / qr_width,
            0,
            0,
            qr_size / qr_height,
            0,
            0,
        ],
    )

    qr_drawing.add(
        qr_code
    )

    renderPDF.draw(
        qr_drawing,
        pdf,
        qr_x,
        qr_y,
    )

    pdf.setFillColor(BLACK)

    pdf.setFont(
        "Helvetica-Bold",
        6,
    )

    pdf.drawCentredString(
        qr_x + (qr_size / 2),
        qr_y - 4 * mm,
        "SCAN TO VERIFY",
    )

    # ========================================================
    # LICENSE IDENTIFIER
    # ========================================================

    pdf.setFillColor(GREY)

    pdf.setFont(
        "Helvetica",
        5.5,
    )

    pdf.drawCentredString(
        page_width / 2,
        8 * mm,
        f"License ID: {license_number}",
    )

"""   


    # ========================================================
    # LICENSE HOLDER
    # ========================================================

    licensed_y = page_height - 124 * mm

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6.5)

    pdf.drawCentredString(
        page_width / 2,
        licensed_y,
        "LICENSED TO",
    )

    pdf.setFillColor(BLACK)

    _draw_centred_fitted_text(
        pdf=pdf,
        text=applicant_name.upper(),
        centre_x=page_width / 2,
        y=licensed_y - 8 * mm,
        max_width=145 * mm,
        font_name="Helvetica-Bold",
        font_size=17,
        min_font_size=10,
    )


    # ========================================================
    # CERTIFICATION STATEMENT
    # ========================================================

    certification_y = licensed_y - 17 * mm

    pdf.setFillColor(DARK)
    pdf.setFont("Helvetica", 6.8)

    certification_lines = [
        "This license certifies that the above-named person is registered as a health professional",
        "and is authorized to practice within the scope of the professional registration",
        "granted by the Medical Board of Papua New Guinea.",
    ]

    for line in certification_lines:
        pdf.drawCentredString(
            page_width / 2,
            certification_y,
            line,
        )
        certification_y -= 3.6 * mm


    # ========================================================
    # PROFESSIONAL INFORMATION
    # ========================================================

    column_left = 30 * mm
    column_right = 112 * mm

    left_value_width = 65 * mm
    right_value_width = 65 * mm

    details_y = page_height - 161 * mm


    # --------------------------------------------------------
    # ROW 1
    # Profession / Professional Registration Number
    # --------------------------------------------------------

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6.2)

    pdf.drawString(
        column_left,
        details_y,
        "PROFESSION",
    )

    pdf.drawString(
        column_right,
        details_y,
        "PROFESSIONAL REGISTRATION NO.",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        profession_display,
        column_left,
        details_y - 5 * mm,
        left_value_width,
        "Helvetica",
        8.5,
    )

    _draw_fitted_text(
        pdf,
        registration_number,
        column_right,
        details_y - 5 * mm,
        right_value_width,
        "Helvetica",
        8.5,
    )


    # --------------------------------------------------------
    # ROW 2
    # Specialization / Application Number
    # --------------------------------------------------------

    row_2_y = details_y - 16 * mm

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6.2)

    pdf.drawString(
        column_left,
        row_2_y,
        "SPECIALIZATION",
    )

    pdf.drawString(
        column_right,
        row_2_y,
        "APPLICATION NUMBER",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        specialization_display,
        column_left,
        row_2_y - 5 * mm,
        left_value_width,
        "Helvetica",
        8.5,
    )

    _draw_fitted_text(
        pdf,
        application_number,
        column_right,
        row_2_y - 5 * mm,
        right_value_width,
        "Helvetica",
        8.5,
    )


    # --------------------------------------------------------
    # ROW 3
    # Qualification / Institution
    # --------------------------------------------------------

    row_3_y = row_2_y - 16 * mm

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6.2)

    pdf.drawString(
        column_left,
        row_3_y,
        "QUALIFICATION",
    )

    pdf.drawString(
        column_right,
        row_3_y,
        "INSTITUTION",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        qualification,
        column_left,
        row_3_y - 5 * mm,
        left_value_width,
        "Helvetica",
        8.5,
    )

    _draw_fitted_text(
        pdf,
        institution,
        column_right,
        row_3_y - 5 * mm,
        right_value_width,
        "Helvetica",
        8.5,
    )


    # --------------------------------------------------------
    # ROW 4
    # Province
    # --------------------------------------------------------

    row_4_y = row_3_y - 16 * mm

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6.2)

    pdf.drawString(
        column_left,
        row_4_y,
        "PROVINCE",
    )

    pdf.setFillColor(DARK)

    _draw_fitted_text(
        pdf,
        province,
        column_left,
        row_4_y - 5 * mm,
        left_value_width,
        "Helvetica",
        8.5,
    )


    # ========================================================
    # LICENSE VALIDITY
    # ========================================================

    validity_y = row_4_y - 16 * mm

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6.2)

    pdf.drawString(
        column_left,
        validity_y,
        "DATE OF ISSUE",
    )

    pdf.drawString(
        column_right,
        validity_y,
        "DATE OF EXPIRY",
    )

    pdf.setFillColor(BLACK)
    pdf.setFont("Helvetica-Bold", 8.5)

    pdf.drawString(
        column_left,
        validity_y - 5 * mm,
        issue_date.strftime("%d %B %Y"),
    )

    pdf.drawString(
        column_right,
        validity_y - 5 * mm,
        expiry_date.strftime("%d %B %Y"),
    )


    # ========================================================
    # AUTHENTICATION AREA
    # ========================================================

    lower_y = 17 * mm


    # --------------------------------------------------------
    # REGISTRAR - LEFT
    # --------------------------------------------------------

    registrar_x = 28 * mm

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Bold", 6)

    pdf.drawString(
        registrar_x,
        lower_y + 32 * mm,
        "REGISTRAR",
    )

    # Signature
    pdf.setFillColor(BLACK)
    pdf.setFont("Helvetica-Oblique", 11.5)

    pdf.drawString(
        registrar_x + 2 * mm,
        lower_y + 23 * mm,
        "Alphonse Tay",
    )

    # Signature baseline
    pdf.setStrokeColor(HexColor("#777777"))
    pdf.setLineWidth(0.4)

    pdf.line(
        registrar_x,
        lower_y + 20 * mm,
        registrar_x + 45 * mm,
        lower_y + 20 * mm,
    )

    pdf.setFillColor(BLACK)
    pdf.setFont("Helvetica-Bold", 7)

    pdf.drawString(
        registrar_x,
        lower_y + 15 * mm,
        "Dr. Alphonse Tay",
    )

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 5.8)

    pdf.drawString(
        registrar_x,
        lower_y + 10.5 * mm,
        "Registrar",
    )

    pdf.drawString(
        registrar_x,
        lower_y + 6.5 * mm,
        "Medical Board of Papua New Guinea",
    )


    # ========================================================
    # MEDICAL BOARD STAMP - CENTRE
    # ========================================================

    stamp_path = finders.find(
        "registrar/images/mb_stamp.png"
    )

    if not stamp_path:
        raise FileNotFoundError(
            "Could not find registrar/images/mb_stamp.png"
        )

    stamp = ImageReader(stamp_path)

    original_stamp_width, original_stamp_height = (
        stamp.getSize()
    )

    # Smaller stamp for a cleaner authentication area
    max_stamp_width = 26 * mm
    max_stamp_height = 26 * mm

    stamp_scale = min(
        max_stamp_width / original_stamp_width,
        max_stamp_height / original_stamp_height,
    )

    stamp_width = (
        original_stamp_width * stamp_scale
    )

    stamp_height = (
        original_stamp_height * stamp_scale
    )

    stamp_x = (
        page_width - stamp_width
    ) / 2

    stamp_y = lower_y + 8 * mm

    pdf.drawImage(
        stamp,
        stamp_x,
        stamp_y,
        width=stamp_width,
        height=stamp_height,
        preserveAspectRatio=True,
        mask="auto",
    )


    # ========================================================
    # QR CODE - RIGHT
    # ========================================================

    qr_size = 22 * mm

    qr_x = (
        page_width
        - 28 * mm
        - qr_size
    )

    qr_y = lower_y + 10 * mm

    verification_data = (
        "Medical Practice License\n"
        f"License No: {license_number}\n"
        f"Name: {applicant_name}\n"
        f"Profession: {profession_display}\n"
        "Status: ACTIVE\n"
        f"Issue Date: {issue_date.strftime('%d %B %Y')}\n"
        f"Expiry Date: {expiry_date.strftime('%d %B %Y')}\n"
        f"Application No: {application_number}"
    )

    qr_code = qr.QrCodeWidget(
        verification_data
    )

    bounds = qr_code.getBounds()

    qr_width = (
        bounds[2] - bounds[0]
    )

    qr_height = (
        bounds[3] - bounds[1]
    )

    qr_drawing = Drawing(
        qr_size,
        qr_size,
        transform=[
            qr_size / qr_width,
            0,
            0,
            qr_size / qr_height,
            0,
            0,
        ],
    )

    qr_drawing.add(
        qr_code
    )

    renderPDF.draw(
        qr_drawing,
        pdf,
        qr_x,
        qr_y,
    )

    pdf.setFillColor(BLACK)
    pdf.setFont("Helvetica-Bold", 5.5)

    pdf.drawCentredString(
        qr_x + (qr_size / 2),
        qr_y - 3.5 * mm,
        "SCAN TO VERIFY",
    )
    
    # ========================================================
    # FINISH PDF
    # ========================================================

    pdf.showPage()
    pdf.save()

    pdf_buffer.seek(0)

    return pdf_buffer