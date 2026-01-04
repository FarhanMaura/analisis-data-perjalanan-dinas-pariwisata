"""
Export utilities for Excel, CSV, and PDF
"""
import pandas as pd
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def export_hotel_to_excel(data, hotel_name, total_rooms):
    """Export hotel data to Excel"""
    if not data:
        return None
    
    # Prepare data
    rows = []
    total_guests = 0
    
    for item in data:
        occupied = item['occupied_rooms']
        guests = item['guest_count']
        percentage = (occupied / total_rooms * 100) if total_rooms > 0 else 0
        
        rows.append({
            'Tanggal': item['date'],
            'Jumlah Kamar Terisi': occupied,
            'Persentase (%)': f"{percentage:.1f}%",
            'Jumlah Tamu': guests
        })
        total_guests += guests
    
    # Add total row
    rows.append({
        'Tanggal': 'TOTAL',
        'Jumlah Kamar Terisi': '',
        'Persentase (%)': '',
        'Jumlah Tamu': total_guests
    })
    
    df = pd.DataFrame(rows)
    
    # Create Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=hotel_name[:30], index=False)
    
    output.seek(0)
    return output


def export_hotel_to_csv(data, hotel_name, total_rooms):
    """Export hotel data to CSV"""
    if not data:
        return None
    
    rows = []
    total_guests = 0
    
    for item in data:
        occupied = item['occupied_rooms']
        guests = item['guest_count']
        percentage = (occupied / total_rooms * 100) if total_rooms > 0 else 0
        
        rows.append({
            'Tanggal': item['date'],
            'Jumlah Kamar Terisi': occupied,
            'Persentase (%)': f"{percentage:.1f}%",
            'Jumlah Tamu': guests
        })
        total_guests += guests
    
    rows.append({
        'Tanggal': 'TOTAL',
        'Jumlah Kamar Terisi': '',
        'Persentase (%)': '',
        'Jumlah Tamu': total_guests
    })
    
    df = pd.DataFrame(rows)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return io.BytesIO(output.getvalue().encode('utf-8'))


def export_hotel_to_pdf(data, hotel_name, total_rooms):
    """Export hotel data to PDF"""
    if not data:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    title = Paragraph(f"Laporan Data Hotel: {hotel_name}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Info
    info_text = f"Total Kamar: {total_rooms}<br/>Tanggal Export: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    info = Paragraph(info_text, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))
    
    # Table data
    table_data = [['Tanggal', 'Kamar Terisi', 'Persentase (%)', 'Jumlah Tamu']]
    total_guests = 0
    
    for item in data:
        occupied = item['occupied_rooms']
        guests = item['guest_count']
        percentage = (occupied / total_rooms * 100) if total_rooms > 0 else 0
        
        table_data.append([
            item['date'],
            str(occupied),
            f"{percentage:.1f}%",
            str(guests)
        ])
        total_guests += guests
    
    # Total row
    table_data.append(['TOTAL', '', '', str(total_guests)])
    
    # Create table
    table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


def export_tourism_to_excel(data, username=None):
    """Export tourism data to Excel"""
    if not data:
        return None
    
    rows = []
    totals = {
        'total_visitors': 0,
        'male_adult': 0,
        'female_adult': 0,
        'male_child': 0,
        'female_child': 0
    }
    
    for item in data:
        rows.append({
            'Tanggal': item['date'],
            'Asal': item['origin'],
            'Total Pengunjung': item['total_visitors'],
            'Laki-laki Dewasa': item['male_adult'],
            'Perempuan Dewasa': item['female_adult'],
            'Anak Laki-laki': item['male_child'],
            'Anak Perempuan': item['female_child']
        })
        
        totals['total_visitors'] += item['total_visitors']
        totals['male_adult'] += item['male_adult']
        totals['female_adult'] += item['female_adult']
        totals['male_child'] += item['male_child']
        totals['female_child'] += item['female_child']
    
    # Add total row
    rows.append({
        'Tanggal': 'TOTAL',
        'Asal': '',
        'Total Pengunjung': totals['total_visitors'],
        'Laki-laki Dewasa': totals['male_adult'],
        'Perempuan Dewasa': totals['female_adult'],
        'Anak Laki-laki': totals['male_child'],
        'Anak Perempuan': totals['female_child']
    })
    
    df = pd.DataFrame(rows)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data Wisata', index=False)
    
    output.seek(0)
    return output


def export_tourism_to_csv(data, username=None):
    """Export tourism data to CSV"""
    if not data:
        return None
    
    rows = []
    totals = {
        'total_visitors': 0,
        'male_adult': 0,
        'female_adult': 0,
        'male_child': 0,
        'female_child': 0
    }
    
    for item in data:
        rows.append({
            'Tanggal': item['date'],
            'Asal': item['origin'],
            'Total Pengunjung': item['total_visitors'],
            'Laki-laki Dewasa': item['male_adult'],
            'Perempuan Dewasa': item['female_adult'],
            'Anak Laki-laki': item['male_child'],
            'Anak Perempuan': item['female_child']
        })
        
        totals['total_visitors'] += item['total_visitors']
        totals['male_adult'] += item['male_adult']
        totals['female_adult'] += item['female_adult']
        totals['male_child'] += item['male_child']
        totals['female_child'] += item['female_child']
    
    rows.append({
        'Tanggal': 'TOTAL',
        'Asal': '',
        'Total Pengunjung': totals['total_visitors'],
        'Laki-laki Dewasa': totals['male_adult'],
        'Perempuan Dewasa': totals['female_adult'],
        'Anak Laki-laki': totals['male_child'],
        'Anak Perempuan': totals['female_child']
    })
    
    df = pd.DataFrame(rows)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return io.BytesIO(output.getvalue().encode('utf-8'))


def export_tourism_to_pdf(data, username=None):
    """Export tourism data to PDF"""
    if not data:
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=1
    )
    
    title = Paragraph("Laporan Data Pengunjung Wisata", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    info_text = f"Tanggal Export: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    info = Paragraph(info_text, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))
    
    # Table data
    table_data = [['Tanggal', 'Asal', 'Total', 'L Dewasa', 'P Dewasa', 'L Anak', 'P Anak']]
    totals = {
        'total_visitors': 0,
        'male_adult': 0,
        'female_adult': 0,
        'male_child': 0,
        'female_child': 0
    }
    
    for item in data:
        table_data.append([
            item['date'],
            item['origin'][:15],  # Truncate long origins
            str(item['total_visitors']),
            str(item['male_adult']),
            str(item['female_adult']),
            str(item['male_child']),
            str(item['female_child'])
        ])
        
        totals['total_visitors'] += item['total_visitors']
        totals['male_adult'] += item['male_adult']
        totals['female_adult'] += item['female_adult']
        totals['male_child'] += item['male_child']
        totals['female_child'] += item['female_child']
    
    # Total row
    table_data.append([
        'TOTAL', '',
        str(totals['total_visitors']),
        str(totals['male_adult']),
        str(totals['female_adult']),
        str(totals['male_child']),
        str(totals['female_child'])
    ])
    
    table = Table(table_data, colWidths=[1*inch, 1*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
