from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import io

def generate_fraud_report(prediction_data: dict) -> bytes:
    buffer = io.BytesIO()
    W, H = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    DARK      = colors.HexColor('#0d1b2e')
    NAVY      = colors.HexColor('#1a2744')
    BLUE      = colors.HexColor('#185FA5')
    RED       = colors.HexColor('#dc2626')
    GREEN     = colors.HexColor('#059669')
    ORANGE    = colors.HexColor('#f97316')
    LIGHT     = colors.HexColor('#f1f5f9')
    MID       = colors.HexColor('#e2e8f0')
    GRAY      = colors.HexColor('#64748b')
    TEXT      = colors.HexColor('#1e293b')
    WHITE     = colors.white

    is_fraud   = prediction_data['prediction'] == 'FRAUD'
    fraud_prob = prediction_data['fraud_probability']
    amount     = prediction_data.get('TransactionAmt', 0)
    alert      = prediction_data.get('alert_level', 'N/A')
    C1 = prediction_data.get('C1', 0)
    C2 = prediction_data.get('C2', 0)
    C4 = prediction_data.get('C4', 0)
    C5 = prediction_data.get('C5', 0)
    pid = prediction_data.get('prediction_id', 'N/A')
    now = datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
    VCOLOR = RED if is_fraud else GREEN
    VERDICT = 'FRAUDULENT TRANSACTION DETECTED' if is_fraud else 'LEGITIMATE TRANSACTION APPROVED'

    M = 28
    CW = W - 2*M

    # ── HEADER ────────────────────────────────────────────────
    hh = 58
    c.setFillColor(DARK)
    c.rect(0, H-hh, W, hh, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(M, H-22, 'FraudShield')
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#94a3b8'))
    c.drawString(M, H-36, 'AI Fraud Detection System  |  Compliance Report')
    c.setFont('Helvetica', 7.5)
    c.setFillColor(colors.HexColor('#94a3b8'))
    c.drawRightString(W-M, H-18, f'Report ID:  {pid}')
    c.drawRightString(W-M, H-30, f'Generated:  {now}')
    c.setFillColor(ORANGE)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawRightString(W-M, H-42, 'CONFIDENTIAL')
    c.setStrokeColor(BLUE)
    c.setLineWidth(2)
    c.line(0, H-hh, W, H-hh)

    y = H - hh - 14

    # ── VERDICT BANNER ────────────────────────────────────────
    bh = 36
    c.setFillColor(VCOLOR)
    c.rect(M, y-bh, CW, bh, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(W/2, y-bh+12, VERDICT)
    y -= bh + 14

    # ── METRICS ROW ───────────────────────────────────────────
    mh = 52
    mw = CW / 4
    labels = ['FRAUD PROBABILITY', 'TRANSACTION AMOUNT', 'ALERT LEVEL', 'VERDICT']
    alert_c = {'SAFE': GREEN, 'LOW RISK': BLUE, 'HIGH RISK': ORANGE, 'CRITICAL': RED}
    vals = [
        (f'{fraud_prob*100:.1f}%', RED if is_fraud else GREEN),
        (f'${amount:,.2f}', WHITE),
        (alert, alert_c.get(alert, BLUE)),
        ('BLOCK' if is_fraud else 'APPROVE', RED if is_fraud else GREEN),
    ]
    for i, (label, (val, vc)) in enumerate(zip(labels, vals)):
        bx = M + i*mw
        c.setFillColor(NAVY)
        c.rect(bx, y-mh, mw, mh, fill=1, stroke=0)
        if i > 0:
            c.setStrokeColor(colors.HexColor('#2d4a6e'))
            c.setLineWidth(0.5)
            c.line(bx, y-mh+6, bx, y-6)
        c.setFillColor(colors.HexColor('#94a3b8'))
        c.setFont('Helvetica', 7)
        c.drawCentredString(bx + mw/2, y-14, label)
        c.setFillColor(vc)
        c.setFont('Helvetica-Bold', 15)
        c.drawCentredString(bx + mw/2, y-34, val)
    y -= mh + 16

    # ── SECTION helper ────────────────────────────────────────
    def section(title, yy):
        c.setFillColor(NAVY)
        c.rect(M, yy-18, CW, 18, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(M+8, yy-13, title)
        return yy - 18

    # ── TRANSACTION DETAILS ───────────────────────────────────
    y = section('TRANSACTION DETAILS', y)
    y -= 4

    def badge(ok):
        return ('NORMAL', GREEN) if ok else ('SUSPICIOUS', RED)

    det_rows = [
        ('Transaction Amount',        f'${amount:,.2f}',          badge(amount < 1000)),
        ('Card Address Links (C1)',    str(int(C1)),               badge(C1 <= 3)),
        ('Card Usage Pattern (C2)',    str(int(C2)),               badge(C2 <= 4)),
        ('Phone Numbers Linked (C4)',  str(int(C4)),               badge(C4 <= 1)),
        ('Email Accounts (C5)',        str(int(C5)),               badge(C5 <= 2)),
        ('Fraud Probability',          f'{fraud_prob*100:.2f}%',  badge(not is_fraud)),
        ('Model Decision',             prediction_data['prediction'], (prediction_data['prediction'], VCOLOR)),
        ('Alert Level',                alert,                      (alert, alert_c.get(alert, BLUE))),
    ]

    row_h = 18
    for ri, (k, v, (badge_text, badge_color)) in enumerate(det_rows):
        bg = LIGHT if ri % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.rect(M, y-row_h, CW, row_h, fill=1, stroke=0)
        c.setStrokeColor(MID)
        c.setLineWidth(0.3)
        c.rect(M, y-row_h, CW, row_h, fill=0, stroke=1)
        c.setFillColor(TEXT)
        c.setFont('Helvetica', 8)
        c.drawString(M+6, y-row_h+6, k)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(M+220, y-row_h+6, str(v))
        c.setFillColor(badge_color)
        c.setFont('Helvetica-Bold', 7.5)
        c.drawString(M+360, y-row_h+6, badge_text)
        y -= row_h

    y -= 14

    # ── RISK SCORE BREAKDOWN ──────────────────────────────────
    y = section('RISK SCORE BREAKDOWN', y)
    y -= 4

    risk_items = [
        ('Transaction Amount',       min(amount/3000, 1.0)),
        ('Card Address Links (C1)',   min(C1/10, 1.0)),
        ('Card Usage Pattern (C2)',   min(C2/10, 1.0)),
        ('Phone Numbers (C4)',        min(C4/5,  1.0)),
        ('Email Accounts (C5)',       min(C5/5,  1.0)),
    ]

    bar_track_w = 160
    for ri, (factor, score) in enumerate(risk_items):
        bg = LIGHT if ri % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.rect(M, y-row_h, CW, row_h, fill=1, stroke=0)
        c.setStrokeColor(MID)
        c.setLineWidth(0.3)
        c.rect(M, y-row_h, CW, row_h, fill=0, stroke=1)
        c.setFillColor(TEXT)
        c.setFont('Helvetica', 8)
        c.drawString(M+6, y-row_h+6, factor)
        bx = M + 200
        c.setFillColor(colors.HexColor('#e2e8f0'))
        c.rect(bx, y-row_h+5, bar_track_w, 8, fill=1, stroke=0)
        fc = RED if score > 0.5 else GREEN
        c.setFillColor(fc)
        c.rect(bx, y-row_h+5, int(bar_track_w*score), 8, fill=1, stroke=0)
        c.setFillColor(TEXT)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(bx + bar_track_w + 8, y-row_h+6, f'{int(score*100)}%')
        level = 'HIGH' if score > 0.5 else 'LOW'
        lc = RED if score > 0.5 else GREEN
        c.setFillColor(lc)
        c.setFont('Helvetica-Bold', 7)
        c.drawRightString(W-M-4, y-row_h+6, level)
        y -= row_h

    y -= 14

    # ── DECISION SUMMARY ─────────────────────────────────────
    y = section('DECISION SUMMARY', y)
    y -= 6

    if is_fraud:
        reasons = []
        if C1 > 3:        reasons.append(f'Card linked to {int(C1)} addresses (normal: 1-3)')
        if C2 > 4:        reasons.append(f'High card usage pattern: {int(C2)} (normal: 1-4)')
        if C4 > 1:        reasons.append(f'Multiple phones linked: {int(C4)} (normal: 0-1)')
        if C5 > 2:        reasons.append(f'Multiple emails: {int(C5)} (normal: 0-2)')
        if amount > 1000: reasons.append(f'High transaction amount: ${amount:,.2f}')
        if not reasons:   reasons.append(f'Fraud probability {fraud_prob*100:.1f}% exceeds 50% threshold')
        action = 'RECOMMENDED ACTION:  Block transaction and notify cardholder immediately.'
        bg_box = colors.HexColor('#450a0a')
        border_c = RED
        text_c = colors.HexColor('#fca5a5')
        title_c = colors.HexColor('#f87171')
    else:
        reasons = [
            f'Fraud probability {fraud_prob*100:.1f}% is below 50% decision threshold',
            'All card activity metrics are within normal ranges',
            f'Amount ${amount:,.2f} is consistent with legitimate transaction patterns',
            'No suspicious behavioral signals detected',
        ]
        action = 'RECOMMENDED ACTION:  Approve transaction. No further action required.'
        bg_box = colors.HexColor('#064e3b')
        border_c = GREEN
        text_c = colors.HexColor('#6ee7b7')
        title_c = colors.HexColor('#34d399')

    box_h = 22 + len(reasons)*14 + 22
    c.setFillColor(bg_box)
    c.rect(M, y-box_h, CW, box_h, fill=1, stroke=0)
    c.setStrokeColor(border_c)
    c.setLineWidth(1.5)
    c.rect(M, y-box_h, CW, box_h, fill=0, stroke=1)
    c.setFillColor(title_c)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(M+10, y-16, 'FRAUD INDICATORS DETECTED' if is_fraud else 'NO FRAUD INDICATORS')
    c.setFont('Helvetica', 8)
    c.setFillColor(text_c)
    ry = y-30
    for r in reasons:
        c.drawString(M+10, ry, f'•  {r}')
        ry -= 13
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(M+10, ry-2, action)
    y -= box_h + 14

    # ── MODEL INFORMATION ─────────────────────────────────────
    y = section('MODEL INFORMATION', y)
    y -= 4

    model_rows = [
        ('Architecture',  'GraphSAGE GNN + Random Forest Classifier'),
        ('Dataset',       'IEEE-CIS Fraud Detection  (590,540 transactions)'),
        ('Performance',   'Accuracy: 84%   |   Fraud Recall: 67%   |   Legitimate Precision: 99%'),
        ('Features',      '31 behavioral features per transaction'),
        ('Graph',         '13,553 card nodes   |   590,540 transaction edges'),
        ('Threshold',     '50% fraud probability  →  FRAUD decision'),
    ]
    for ri, (k, v) in enumerate(model_rows):
        bg = LIGHT if ri % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.rect(M, y-row_h, CW, row_h, fill=1, stroke=0)
        c.setStrokeColor(MID)
        c.setLineWidth(0.3)
        c.rect(M, y-row_h, CW, row_h, fill=0, stroke=1)
        c.setFillColor(GRAY)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(M+6, y-12, k)
        c.setFillColor(TEXT)
        c.setFont('Helvetica', 8)
        c.drawString(M+160, y-12, v)
        y -= row_h

    # ── FOOTER ────────────────────────────────────────────────
    fh = 28
    c.setFillColor(DARK)
    c.rect(0, 0, W, fh, fill=1, stroke=0)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.line(0, fh, W, fh)
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 6.5)
    c.drawCentredString(W/2, fh-10,
        'FraudShield AI Detection System   |   CONFIDENTIAL — For Authorized Personnel Only   |   Decisions must be reviewed by a qualified compliance officer')
    c.drawCentredString(W/2, fh-20, f'Report ID: {pid}   |   Generated: {now}')

    c.save()
    buffer.seek(0)
    return buffer.getvalue()