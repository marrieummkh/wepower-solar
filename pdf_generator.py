# pdf_generator.py - Enhanced with Complete Branding

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
    PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BRAND CONFIGURATION - Centralized Brand Settings
# ============================================================
class BrandConfig:
    """Centralized brand configuration for We Power Solar Solutions"""
    
    # Primary Brand Colors
    PRIMARY = colors.HexColor("#1A2B4C")      # Navy Blue - Main brand color
    SECONDARY = colors.HexColor("#2C3E50")    # Dark Gray - Secondary color
    ACCENT = colors.HexColor("#1A4D2E")       # Dark Green - Accent color
    ACCENT_LIGHT = colors.HexColor("#F5B041") # Light Orange - Hover/Highlight
    LIGHT_BG = colors.HexColor("#F8FAFC")     # Light Gray - Section backgrounds
    BORDER = colors.HexColor("#CBD5E1")       # Border color
    TEXT_DARK = colors.HexColor("#1A202C")    # Dark text
    TEXT_GRAY = colors.HexColor("#4A5568")    # Medium gray text
    TEXT_LIGHT = colors.HexColor("#718096")   # Light gray text
    WHITE = colors.HexColor("#FFFFFF")
    SUCCESS = colors.HexColor("#48BB78")      # Green for success indicators
    WARNING = colors.HexColor("#ED8936")      # Orange for warnings
    
    # Font Settings
    FONT_HEADING = "Helvetica-Bold"
    FONT_BODY = "Helvetica"
    FONT_LIGHT = "Helvetica-Light"
    
    # Company Details
    COMPANY_NAME = "WEPOWER"
    COMPANY_TAGLINE = "SOLAR SOLUTIONS"
    COMPANY_FULL_NAME = "WePower Solar Solutions"
    COMPANY_ADDRESS = "Office # 3GF, Plaza 179, Intellectual Village, Spring North Bahria Town"
    COMPANY_PHONE = "+92-331-5110474"
    COMPANY_EMAIL = "wepowersolarsolutions@gmail.com"
    # COMPANY_WEBSITE = "www.wepowersolar.com"  # removed per user request
    COMPANY_CNIC = "08310108890286"
    # Path to logo image (generated)
    COMPANY_LOGO = r"D:\wepower\wepower logo.jpeg"
    
    # Document Settings
    DOCUMENT_TITLE = "PROJECT PROPOSAL"
   # DOCUMENT_SUBTITLE = "Solar Energy Solution"
    
    # Page Settings
    PAGE_WIDTH, PAGE_HEIGHT = letter
    MARGIN_LEFT = 36
    MARGIN_RIGHT = 36
    MARGIN_TOP = 45
    MARGIN_BOTTOM = 36
    
    @classmethod
    def get_color(cls, name):
        """Get color by name"""
        return getattr(cls, name.upper(), cls.PRIMARY)


# ============================================================
# CUSTOM CANVAS WITH BRANDING
# ============================================================
class BrandedNumberedCanvas(canvas.Canvas):
    """Enhanced canvas with full brand styling on every page"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.brand = BrandConfig
        
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        """Draw brand elements on every page"""
        self.saveState()
        
        # ====== HEADER (Page 2+) ======
        if self._pageNumber > 1:
            # Brand bar at top - raised slightly for more header room
            self.setFillColor(self.brand.PRIMARY)
            self.rect(36, 775, 540, 3, stroke=0, fill=1)
            
            # Company logo in header (replacing text)
            try:
                self.drawImage(
                    self.brand.COMPANY_LOGO,
                    36, 740, width=100, height=42,
                    preserveAspectRatio=True, mask='auto'
                )
            except Exception:
                # Fallback to text if logo unavailable
                self.setFont(self.brand.FONT_HEADING, 10)
                self.setFillColor(self.brand.PRIMARY)
                self.drawString(36, 758, self.brand.COMPANY_NAME)
                self.setFont(self.brand.FONT_BODY, 8)
                self.setFillColor(self.brand.ACCENT)
                self.drawString(105, 758, self.brand.COMPANY_TAGLINE)
            
            # Document title in header
            self.setFont(self.brand.FONT_HEADING, 9)
            self.setFillColor(self.brand.PRIMARY)
            self.drawRightString(570, 758, self.brand.DOCUMENT_TITLE)
            
            # Divider line
            self.setStrokeColor(self.brand.BORDER)
            self.setLineWidth(0.5)
            self.line(36, 735, 570, 735)

        # ====== FOOTER (All Pages) ======
        # Brand line above footer
        self.setStrokeColor(self.brand.ACCENT)
        self.setLineWidth(1.5)
        self.line(36, 45, 570, 45)
        
        # Footer text with brand colors
        self.setFont(self.brand.FONT_BODY, 7)
        self.setFillColor(self.brand.TEXT_GRAY)
        
        # Left side - Company name
        # Draw company logo instead of text
        self.drawImage(self.brand.COMPANY_LOGO, 36, 20, width=80, height=20, preserveAspectRatio=True, mask='auto')
        
        # Center - Address and contact
        address_text = f"{self.brand.COMPANY_ADDRESS} | Tel: {self.brand.COMPANY_PHONE}"
        self.drawCentredString(303, 30, address_text)
        
        # Right side - Page number with brand accent
        self.setFillColor(self.brand.ACCENT)
        self.setFont(self.brand.FONT_HEADING, 8)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(570, 30, page_text)
        
        # Small brand line at very bottom
        self.setStrokeColor(self.brand.PRIMARY)
        self.setLineWidth(0.5)
        self.line(36, 20, 570, 20)
        
        # Footer website and email removed (per user request)
        
        self.restoreState()


# ============================================================
# STYLE BUILDER
# ============================================================
class StyleBuilder:
    """Builds styled elements with brand consistency"""
    
    def __init__(self):
        self.brand = BrandConfig
        self.styles = getSampleStyleSheet()
        self._build_styles()
    
    def _build_styles(self):
        """Build all paragraph styles with brand colors"""
        
        # ====== Brand Title Style ======
        self.brand_title = ParagraphStyle(
            'BrandTitle',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=18,
            leading=22,
            textColor=self.brand.PRIMARY,
            alignment=0  # Left align
        )
        
        # ====== Brand Subtitle Style ======
        self.brand_subtitle = ParagraphStyle(
            'BrandSubtitle',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=10,
            leading=14,
            textColor=self.brand.ACCENT,
            alignment=0
        )
        
        # ====== Document Title Style ======
        self.doc_title = ParagraphStyle(
            'DocTitle',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=20,
            leading=24,
            textColor=self.brand.PRIMARY,
            alignment=1,  # Center
            spaceAfter=2
        )
        
        # ====== Document Subtitle Style ======
        self.doc_subtitle = ParagraphStyle(
            'DocSubTitle',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=11,
            leading=14,
            textColor=self.brand.ACCENT,
            alignment=1
        )
        
        # ====== Section Header Style ======
        self.section_header = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=11,
            leading=14,
            textColor=self.brand.PRIMARY,
            spaceBefore=8,
            spaceAfter=4
        )
        
        # ====== Body Text Style ======
        self.body_text = ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_BODY,
            fontSize=8,
            leading=11.5,
            textColor=self.brand.TEXT_DARK
        )
        
        # ====== Small Body Text ======
        self.body_small = ParagraphStyle(
            'BodySmall',
            parent=self.body_text,
            fontSize=7,
            leading=10,
            textColor=self.brand.TEXT_GRAY
        )
        
        # ====== Table Header Style ======
        self.table_header = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=8,
            leading=10,
            textColor=self.brand.WHITE,
            alignment=1  # Center
        )
        
        # ====== Table Cell Style ======
        self.table_cell = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_BODY,
            fontSize=7.5,
            leading=10.5,
            textColor=self.brand.TEXT_DARK
        )
        
        # ====== Table Cell Center ======
        self.table_cell_center = ParagraphStyle(
            'TableCellCenter',
            parent=self.table_cell,
            alignment=1
        )
        
        # ====== Table Cell Right ======
        self.table_cell_right = ParagraphStyle(
            'TableCellRight',
            parent=self.table_cell,
            alignment=2
        )
        
        # ====== Table Cell Bold ======
        self.table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=self.table_cell,
            fontName=self.brand.FONT_HEADING,
            textColor=self.brand.PRIMARY
        )
        
        # ====== Total Amount Style ======
        self.total_amount = ParagraphStyle(
            'TotalAmount',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=14,
            leading=18,
            textColor=self.brand.ACCENT,
            alignment=2  # Right align
        )
        
        # ====== Discount Style ======
        self.discount_text = ParagraphStyle(
            'DiscountText',
            parent=self.styles['Normal'],
            fontName=self.brand.FONT_HEADING,
            fontSize=11,
            leading=14,
            textColor=self.brand.WARNING,
            alignment=2
        )


# ============================================================
# PDF GENERATOR
# ============================================================
def create_wepower_pdf(data):
    """
    Generate a branded PDF quotation for We Power Solar Solutions
    
    Args:
        data (dict): Dictionary containing all quotation data
            Required keys:
                - client_name: str
                - client_phone: str
                - customer_id: str
                - cnic: str
                - timestamp: str
                - system_kw: float
                - system_type: str
                - inverter_desc: str
                - panel_rate: float
                - structure_type: str
                - structure_rate: float
                - installation_rate: float
                - inverter_price: float
                - battery_price: float
                - accessories_price: float
                - transport_price: float
                - discount: float
                - has_battery: bool
                - validity: int
                - payment_terms_text: str
    
    Returns:
        tuple: (bytes, final_amount)
    """
    from io import BytesIO
    
    buffer = BytesIO()
    brand = BrandConfig
    styles = StyleBuilder()
    
    # ====== Create Document ======
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(brand.PAGE_WIDTH, brand.PAGE_HEIGHT), # FIXED: Tuple instead of single float
        rightMargin=brand.MARGIN_RIGHT,
        leftMargin=brand.MARGIN_LEFT,
        topMargin=brand.MARGIN_TOP,
        bottomMargin=brand.MARGIN_BOTTOM
    )
    
    story = []
    
    # ============================================================
    # SECTION 1: HEADER BLOCK
    # ============================================================
    
    # Left: Company Logo Image (replacing text branding)
    logo_path = brand.COMPANY_LOGO
    try:
        header_logo = Image(logo_path, width=160, height=70)
        header_logo.hAlign = 'LEFT'
        header_left_cell = header_logo
    except Exception:
        # Fallback to text if logo not found
        header_left_text = f"""
            <font size='16' color='#1A2B4C'><b>{brand.COMPANY_NAME}</b></font>
            <br/>
            <font size='10' color='#1A4D2E'><b>{brand.COMPANY_TAGLINE}</b></font>
        """
        header_left_cell = Paragraph(header_left_text, styles.brand_title)
    
    # Center: Document Title with Accent
    header_center = f"""
        <font size='18' color='#1A2B4C'><b>{brand.DOCUMENT_TITLE}</b></font>
    """
    
    # Right: Contact Info
    header_right = f"""
        <font size='8' color='#1A2B4C'><b>Call Us</b></font>
        <br/>
        <font size='10' color='#1A4D2E'><b>{brand.COMPANY_PHONE}</b></font>
        <br/>
        <font size='7' color='#718096'>{brand.COMPANY_EMAIL}</font>
    """
    
    header_table = Table([
        [
            header_left_cell,
            Paragraph(header_center, styles.doc_title),
            Paragraph(header_right, styles.body_text)
        ]
    ], colWidths=[160, 240, 140])
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEBELOW', (0, 0), (-1, -1), 2.5, brand.ACCENT),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, brand.PRIMARY),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 8))
    
    # ============================================================
    # SECTION 2: INTRO & CUSTOMER DETAILS
    # ============================================================
    
    intro_text = f"""
        <font color='#1A2B4C'><b>{brand.COMPANY_FULL_NAME}</b></font> is a top solar system 
        installation company in Pakistan, providing renewable energy solutions to businesses 
        and individuals since its inception in 2021.
    """
    
    # Customer Details Box
    client_box_text = f"""
        <font color='#1A2B4C'><b>CUSTOMER DETAILS</b></font>
        <br/>
        <font size='9' color='#1A2B4C'><b>{data.get('client_name', 'VALUED CLIENT').upper()}</b></font>
        <br/>
        <font size='8' color='#4A5568'><b>Phone:</b> {data.get('client_phone', 'N/A')}</font>
    """
    
    # Meta Information Box
    meta_box_text = f"""
        <font color='#1A2B4C'><b>DOCUMENT INFO</b></font>
        <br/>
        <font size='8' color='#4A5568'><b>Date:</b> {data.get('timestamp', 'July 22, 2026').split()[0]}</font>
        <br/>
        <font size='8' color='#4A5568'><b>Customer ID:</b> {data.get('customer_id', 'N/A')}</font>
        <br/>
        <font size='8' color='#4A5568'><b>CNIC:</b> {data.get('cnic', 'N/A')}</font>
    """
    
    info_table = Table([
        [
            Paragraph(intro_text, styles.body_text),
            Paragraph(client_box_text, styles.body_text),
            Paragraph(meta_box_text, styles.body_text)
        ]
    ], colWidths=[210, 165, 165])
    
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), brand.LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, brand.BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, brand.BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        # Brand accent on left border
        ('LINELEFT', (0, 0), (0, -1), 3, brand.ACCENT),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 10))
    
    # ============================================================
    # SECTION 3: PROJECT DESCRIPTION
    # ============================================================
    
    sys_kw = data.get('system_kw', 0)
    sys_type = data.get('system_type', 'On-Grid System').upper()
    inv_info = data.get('inverter_desc', '10KW ONGRID INVERTER')
    
    # Project Description with brand styling
    project_desc = f"""
        <font color='#1A2B4C'><b>PROJECT DESCRIPTION</b></font>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <font color='#1A4D2E'><b>{sys_kw} KW {sys_type}</b></font>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <font color='#2C3E50'>WITH {inv_info}</font>
    """
    
    story.append(Paragraph(project_desc, styles.section_header))
    story.append(Spacer(1, 6))
    
    # ============================================================
    # SECTION 4: CALCULATIONS
    # ============================================================
    
    panel_rate = data.get('panel_rate', 0)
    structure_type = data.get('structure_type', 'Standard')
    structure_rate = data.get('structure_rate', 0)
    installation_rate = data.get('installation_rate', 0)
    
    watts = sys_kw * 1000
    
    panels_total = int(watts * panel_rate)
    structure_total = int(watts * structure_rate)
    installation_total = int(watts * installation_rate)
    
    inverter_price = int(data.get('inverter_price', 0))
    battery_price = int(data.get('battery_price', 0))
    accessories_price = int(data.get('accessories_price', 0))
    transport_price = int(data.get('transport_price', 0))
    discount = int(data.get('discount', 0))
    
    subtotal = inverter_price + battery_price + panels_total + structure_total + accessories_price + installation_total + transport_price
    final_amount = subtotal - discount
    
    # ============================================================
    # SECTION 5: ITEMS TABLE
    # ============================================================
    
    # Table headers with brand colors
    table_data = [
        [
            Paragraph("S.No", styles.table_header),
            Paragraph("Description", styles.table_header),
            Paragraph("UoM", styles.table_header),
            Paragraph("Qty", styles.table_header),
            Paragraph("Unit Price (PKR)", styles.table_header),
            Paragraph("Total (PKR)", styles.table_header)
        ]
    ]
    
    # Row 1: Inverter
    table_data.append([
        Paragraph("01", styles.table_cell_center),
        Paragraph(f"<b>{inv_info}</b><br/><font size='7' color='#4A5568'>Wapda Gen Sync Compliant, High Efficiency</font>", styles.table_cell),
        Paragraph("Set", styles.table_cell_center),
        Paragraph("1", styles.table_cell_center),
        Paragraph(f"{inverter_price:,}", styles.table_cell_right),
        Paragraph(f"{inverter_price:,}", styles.table_cell_right)
    ])
    
    # Row 2: Battery (if exists)
    if data.get('has_battery', False) and battery_price > 0:
        table_data.append([
            Paragraph("", styles.table_cell_center),
            Paragraph("Li-Ion Storage Battery Pack", styles.table_cell),
            Paragraph("Set", styles.table_cell_center),
            Paragraph("1", styles.table_cell_center),
            Paragraph(f"{battery_price:,}", styles.table_cell_right),
            Paragraph(f"{battery_price:,}", styles.table_cell_right)
        ])
    
    # Row 3: Solar Panels
    table_data.append([
        Paragraph("02", styles.table_cell_center),
        Paragraph("""<b>605-645W Solar Panel</b><br/>
        <font size='7' color='#4A5568'>JA / JINKO / LONGI / CANADIAN N-TYPE BI-FACIAL<br/>
        High Efficiency PV Cells with Nano Coating & Anti-PID Protection</font>""", 
        styles.table_cell),
        Paragraph("Watt", styles.table_cell_center),
        Paragraph(f"{int(watts)}", styles.table_cell_center),
        Paragraph(f"{panel_rate:,}", styles.table_cell_right),
        Paragraph(f"{panels_total:,}", styles.table_cell_right)
    ])
    
    # Row 4: Structure
    table_data.append([
        Paragraph("03", styles.table_cell_center),
        Paragraph(f"<b>{structure_type.upper()} STRUCTURE</b><br/><font size='7' color='#4A5568'>14 Gauge - L2 / L3 / L4 Structure for Solar Installation</font>", 
        styles.table_cell),
        Paragraph("Watt", styles.table_cell_center),
        Paragraph(f"{int(watts)}", styles.table_cell_center),
        Paragraph(f"{structure_rate:,}", styles.table_cell_right),
        Paragraph(f"{structure_total:,}", styles.table_cell_right)
    ])
    
    # Row 5: Accessories
    table_data.append([
        Paragraph("04", styles.table_cell_center),
        Paragraph("""<b>INSTALLATION ACCESSORIES & DB</b><br/>
        <font size='7' color='#4A5568'>Combiner Boxes, DC/AC Cables, u-PVC Conduits,<br/>
        3-Phase DB, Chint Breakers & Earthing System</font>""", 
        styles.table_cell),
        Paragraph("Set", styles.table_cell_center),
        Paragraph("1", styles.table_cell_center),
        Paragraph(f"{accessories_price:,}", styles.table_cell_right),
        Paragraph(f"{accessories_price:,}", styles.table_cell_right)
    ])
    
    # Row 6: Installation
    table_data.append([
        Paragraph("05", styles.table_cell_center),
        Paragraph("<b>Installation, Testing and Commissioning</b><br/><font size='7' color='#4A5568'>by PEC Accredited Engineers</font>", 
        styles.table_cell),
        Paragraph("Watt", styles.table_cell_center),
        Paragraph(f"{int(watts)}", styles.table_cell_center),
        Paragraph(f"{installation_rate:,}", styles.table_cell_right),
        Paragraph(f"{installation_total:,}", styles.table_cell_right)
    ])
    
    # Row 7: Transport
    table_data.append([
        Paragraph("06", styles.table_cell_center),
        Paragraph("<b>Transportation of Material to Site</b>", styles.table_cell),
        Paragraph("Job", styles.table_cell_center),
        Paragraph("1", styles.table_cell_center),
        Paragraph(f"{transport_price:,}", styles.table_cell_right),
        Paragraph(f"{transport_price:,}", styles.table_cell_right)
    ])
    
    # Create items table with brand styling
    items_table = Table(table_data, colWidths=[30, 214, 45, 45, 93, 93])
    items_table.setStyle(TableStyle([
        # Header background with brand primary color
        ('BACKGROUND', (0, 0), (-1, 0), brand.PRIMARY),
        # All rows
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, brand.BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Alternate row colors for better readability
        ('BACKGROUND', (0, 1), (-1, -1), brand.LIGHT_BG),
        ('BACKGROUND', (0, 2), (-1, 2), brand.WHITE),
        ('BACKGROUND', (0, 3), (-1, 3), brand.LIGHT_BG),
        ('BACKGROUND', (0, 4), (-1, 4), brand.WHITE),
        ('BACKGROUND', (0, 5), (-1, 5), brand.LIGHT_BG),
        ('BACKGROUND', (0, 6), (-1, 6), brand.WHITE),
        ('BACKGROUND', (0, 7), (-1, 7), brand.LIGHT_BG),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 10))
    
    # ============================================================
    # SECTION 6: NOTES & TOTALS
    # ============================================================
    
    validity = data.get('validity', 2)
    
    # Format numbers with commas
    subtotal_formatted = f"{subtotal:,}"
    final_formatted = f"{final_amount:,}"
    discount_formatted = f"{discount:,}"
    
    notes_html = f"""
        <font color='#1A2B4C'><b>SPECIAL NOTES & INSTRUCTIONS</b></font>
        <br/>
        <font color='#4A5568'>
        • This quote is valid for {validity} days (due to fluctuation in panels price).<br/>
        • Project Completion time = 7 Days (after Initial Payment).<br/>
        • Free After Sales Services = 2 Years.<br/>
        </font>
        <br/>
        <table width='100%' border='0'>
        <tr>
            <td><font size='9' color='#1A2B4C'><b>Subtotal:</b> PKR {subtotal_formatted}/-</font></td>
            <td align='right'><font size='9' color='#1A2B4C'><b>Discount:</b> PKR {discount_formatted}/-</font></td>
        </tr>
        <tr>
            <td colspan='2' align='right'>
                <font size='12' color='#1A4D2E'><b>DISCOUNTED PRICE: PKR {final_formatted}/-</b></font>
            </td>
        </tr>
        </table>
    """
    
    notes_table = Table([[Paragraph(notes_html, styles.body_text)]], colWidths=[540])
    notes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), brand.LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, brand.BORDER),
        # Accent border on left
        ('LINELEFT', (0, 0), (0, -1), 3, brand.ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(notes_table)
    story.append(Spacer(1, 10))
    
    # ============================================================
    # SECTION 7: DETAILED SECTIONS
    # ============================================================
    
    # Prepare payment terms with HTML line breaks (compatible with Python 3.11)
    payment_terms_raw = data.get(
        'payment_terms_text',
        '• 90% to be paid initially as 1st Payment | 10% to be paid upon completion.'
    )
    # Normalize line endings and replace them with <br/> tags for HTML rendering
    payment_terms_normalized = payment_terms_raw.replace('\r\n', '\n')
    payment_terms_formatted = payment_terms_normalized.replace('\n', '<br/>')

    
    # SECTION 7: DETAILED SECTIONS (including payment terms)
    sections_html = f"""
        <font color='#1A2B4C'><b>INTRODUCTION</b></font>
        <br/>
        <font color='#4A5568'>
        WePower Solar solutions has been installing solar systems all over Pakistan. Our products 
        and solutions are made to meet all kind of solar needs for domestic, commercial and 
        industrial consumers. We install and service solar systems in metro cities as well as 
        small regional towns. Our extensive network of PEC accredited solar panel installers and 
        electricians perform installation work according to PEC guidelines.
        </font>
        <br/><br/>
        <font color='#1A2B4C'><b>WARRANTY AND SERVICES</b></font>
        <br/>
        <font color='#4A5568'>
        We offer industry-leading warranties for all the components installed as a part of the solar system.
        <br/>
        <font color='#1A4D2E'>• Smart Inverter: 5 Years</font> &nbsp;|&nbsp; 
        <font color='#1A4D2E'>Structure Warranty: 10 Years</font> &nbsp;|&nbsp; 
        <font color='#1A4D2E'>Battery Warranty: 10 Years</font><br/>
        <font color='#1A2B4C'>• Solar Panel Grade-A Workmanship: 12 Years</font> &nbsp;|&nbsp; 
        <font color='#1A2B4C'>Performance: 25 Years</font><br/>
        <font size='7' color='#718096'>
        <i>Warranty period will commence from the date of System Commissioning. Issues due to natural 
        disasters will not be covered under company's warranty.</i>
        </font>
        <br/><br/>
        </font>
        <font color='#1A2B4C'><b>PAYMENT TERMS & BANK DETAILS</b></font>
        <br/>
        <font color='#4A5568'>
        The Payment of this project will be completed in parts, as discussed with our client 
        <b>{data.get('client_name', '').upper()}</b>. Mode of payment can be Cheque, Bank Transfer, or Cash.<br/>
        {payment_terms_formatted}
        </font>
        <br/><br/>
        <font color='#1A2B4C'><b>Bank Account Details:</b></font>
        <br/>
        <font color='#1A4D2E'><b>Meezan Bank | Title: We Power | Account: 08310108890286</b></font>
        <br/><br/>
        <font color='#1A2B4C'><b>ACKNOWLEDGEMENT</b></font>
        <br/>
        <font color='#4A5568'>
        I acknowledge and represent that I have read the terms and conditions of this proposal and 
        fully understand what is stated herein. I expressly agree to all terms and conditions set out herein.
        </font>
    """
    
    sections_table = Table([[Paragraph(sections_html, styles.body_text)]], colWidths=[540])
    sections_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), brand.LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, brand.BORDER),
        ('LINELEFT', (0, 0), (0, -1), 3, brand.ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(sections_table)
    story.append(Spacer(1, 12))
    
    # ============================================================
    # SECTION 8: SIGNATURE BLOCK
    # ============================================================
    
    sig_content_1 = f"""
        <font color='#1A2B4C'><b>CLIENT SIGNATURE</b></font>
        <br/><br/><br/>
        <font color='#1A2B4C'>___________________________</font>
        <br/>
        <font color='#4A5568'><b>Name:</b> {data.get('client_name', '')}</font>
        <br/>
        <font color='#4A5568'><b>Date:</b> _____________</font>
        <br/><br/>
        <font color='#718096' size='7'><i>I acknowledge receipt of this proposal</i></font>
    """
    
    sig_content_2 = f"""
        <font color='#1A2B4C'><b>APPROVED BY (WePower)</b></font>
        <br/><br/><br/>
        <font color='#1A2B4C'>___________________________</font>
        <br/>
        <font color='#4A5568'><b>Company:</b> WePower Solar Solutions</font>
        <br/>
        <font color='#4A5568'><b>Date:</b> {data.get('timestamp', '').split()[0]}</font>
        <br/><br/>
        <font color='#718096' size='7'><i>Authorized Signatory</i></font>
    """
    
    sig_table = Table([
        [
            Paragraph(sig_content_1, styles.body_text),
            Paragraph(sig_content_2, styles.body_text)
        ]
    ], colWidths=[270, 270])
    
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        # Brand accent on top
        ('LINEABOVE', (0, 0), (-1, -1), 2, BrandConfig.ACCENT),
        # Add a subtle background
        ('BACKGROUND', (0, 0), (-1, -1), BrandConfig.LIGHT_BG),
    ]))
    
    story.append(KeepTogether([sig_table]))
    
    # ============================================================
    # BUILD THE DOCUMENT
    # ============================================================
    
    try:
        doc.build(story, canvasmaker=BrandedNumberedCanvas)
        buffer.seek(0)
        logger.info("PDF generated successfully with full branding")
        return buffer.getvalue(), final_amount
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_quotation_pdf(data):
    """
    Wrapper function to generate PDF with error handling
    
    Args:
        data (dict): Quotation data
        
    Returns:
        tuple: (pdf_bytes, final_amount)
    """
    try:
        pdf_bytes, amount = create_wepower_pdf(data)
        return pdf_bytes, amount
    except Exception as e:
        logger.error(f"Failed to generate quotation PDF: {e}")
        raise

def get_brand_colors():
    """Return brand colors for use in other parts of the application"""
    return {
        'primary': '#1A2B4C',
        'secondary': '#2C3E50',
        'accent': '#1A4D2E',
        'accent_light': '#F5B041',
        'light_bg': '#F8FAFC',
        'border': '#CBD5E1',
        'text_dark': '#1A202C',
        'text_gray': '#4A5568',
        'text_light': '#718096',
        'white': '#FFFFFF',
        'success': '#48BB78',
        'warning': '#ED8936'
    }

# ============================================================
# TEST FUNCTION
# ============================================================

def test_pdf_generation():
    """Test the PDF generation with sample data"""
    sample_data = {
        'client_name': 'Mr. Iqtadar Saeed',
        'client_phone': '+92-300-1234567',
        'customer_id': 'CUST-2026-001',
        'cnic': 'XXXXX-XXXXXXX-X',
        'timestamp': '2026-08-01',
        'system_kw': 10,
        'system_type': 'On-Grid System',
        'inverter_desc': '10KW ONGRID INVERTER',
        'panel_rate': 45,
        'structure_type': 'Standard',
        'structure_rate': 15,
        'installation_rate': 12,
        'inverter_price': 250000,
        'battery_price': 720000,
        'accessories_price': 150000,
        'transport_price': 50000,
        'discount': 100000,
        'has_battery': True,
        'validity': 15,
        'payment_terms_text': '• 50% to be paid initially\n• 30% upon delivery\n• 20% upon completion'
    }
    
    try:
        pdf_bytes, total = generate_quotation_pdf(sample_data)
        
        # Save to file for testing
        with open('test_quotation.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"PDF generated successfully!")
        print(f"Total Amount: PKR {total:,}/-")
        print(f"Saved as: test_quotation.pdf")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    test_pdf_generation()