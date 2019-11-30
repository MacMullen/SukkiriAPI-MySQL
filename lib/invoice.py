from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
import datetime
from io import BytesIO


def generate_invoice(rma_cases, dist_company):
    # Source: https://stackoverflow.com/questions/48863462/writing-full-csv-table-to-pdf-in-python
    data = []
    data.append(["ID", "BRAND", "MODEL", "PROBLEM", "SERIAL NUMBER"])
    for rma_case in rma_cases:
        row_data = [rma_case.id, rma_case.brand, rma_case.model, rma_case.problem, rma_case.serial_number]
        data.append(row_data)

    elements = []

    # PDF Text
    # PDF Text - Styles
    styles = getSampleStyleSheet()
    styleNormal = styles['Normal']

    # PDF Text - Content
    line1 = '<font size=10><b>MY COMPANY NAME</b></font>'
    line2 = '<b>DATE: {}</b>'.format(datetime.datetime.now().strftime("%d-%m-%y"))
    line3 = 'RMA INVOICE - <b>{}</b>'.format(dist_company.upper())

    elements.append(Paragraph(line1, styleNormal))
    elements.append(Paragraph(line2, styleNormal))
    elements.append(Paragraph(line3, styleNormal))
    elements.append(Spacer(inch, .25 * inch))

    # PDF Table
    # PDF Table - Styles
    # [(start_column, start_row), (end_column, end_row)]
    all_cells = [(0, 0), (-1, -1)]
    header = [(0, 0), (-1, 0)]
    column0 = [(0, 0), (0, -1)]
    column1 = [(1, 0), (1, -1)]
    column2 = [(2, 0), (2, -1)]
    column3 = [(3, 0), (3, -1)]
    column4 = [(4, 0), (4, -1)]
    table_style = TableStyle([
        ('VALIGN', all_cells[0], all_cells[1], 'TOP'),
        ('FONTNAME', header[0], header[1], 'Courier-Bold'),
        ('LINEBELOW', header[0], header[1], 1.2, colors.black),
        ('ALIGN', column0[0], column0[1], 'CENTRE'),
        ('ALIGN', column1[0], column1[1], 'LEFT'),
        ('ALIGN', column2[0], column2[1], 'LEFT'),
        ('ALIGN', column3[0], column3[1], 'LEFT'),
        ('ALIGN', column4[0], column4[1], 'CENTRE'),
        ('ALIGN', header[0], header[1], 'CENTRE'),
        ('GRID', (0, 1), (-1, -1), 0.25, colors.black)
    ])

    # PDF Table - Column Widths
    colWidths = [
        1.5 * cm,  # Column 0
        3 * cm,  # Column 1
        4 * cm,  # Column 2
        12 * cm,  # Column 4
        6 * cm,  # Column 5
    ]

    # PDF Table - Strip '[]() and add word wrap to column 5
    # count = 0
    # for index, row in enumerate(data):
    #     count += 1
    #     for col, val in enumerate(row):
    #         data[index][col] = Paragraph(val, styles['Normal'])

    # Add table to elements
    t = Table(data, colWidths=colWidths)
    t.setStyle(table_style)
    elements.append(t)

    line4 = """<font size=12><b>Total: {}</b></font>""".format(len(data) - 1)

    elements.append(Spacer(inch, .30 * inch))
    elements.append(Paragraph(line4, styleNormal))
    elements.append(Spacer(inch, .30 * inch))

    # Botton part of the file.
    colWidths = [9.5 * cm, 9.5 * cm]
    rowHeights = [0.8 * cm, 1.2 * cm, 0.7 * cm, 0.7 * cm]
    deliver_header_line = Paragraph("""<font size=12><b>DELIVERS</b></font>""", styles['Normal'])
    pick_header_line = Paragraph("""<font size=12><b>RECEIVES</b></font>""", styles['Normal'])
    signature_line = Paragraph("""<b>SIGNATURE:</b>""", styles['Normal'])
    text_line = Paragraph("""<b>CLARIFICATION:</b>""", styles['Normal'])
    document_line = Paragraph("""<b>ID:</b>""", styles['Normal'])
    sign_table = [[pick_header_line, deliver_header_line], [signature_line, signature_line], [text_line, text_line],
                  [document_line, document_line]]
    bottom_table = Table(sign_table, colWidths=colWidths, rowHeights=rowHeights)
    bottom_table.setStyle((TableStyle([('ALIGN', (0, 1), (0, 1), 'RIGHT'),
                                       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                       ('GRID', (0, 1), (-1, -1), 0.25, colors.black)])))
    elements.append(bottom_table)

    lWidth, lHeight = A4

    pdf_buffer = BytesIO()

    # Generate PDF
    archivo_pdf = SimpleDocTemplate(
        pdf_buffer,
        pagesize=(lHeight, lWidth),
        rightMargin=20,
        leftMargin=20,
        topMargin=40,
        bottomMargin=28)
    archivo_pdf.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer
