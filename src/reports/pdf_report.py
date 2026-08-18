"""
Official Amazon Prime Video Quality Control PDF Report Generator.
Generates broadcast-grade inspection certificates and rejection notices with detailed
explanations of failures and step-by-step NLE / FFmpeg corrective guidelines.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from ..engine.models import QCReportData
from ..core.constants import Severity, StreamType
from ..core.utils import format_bytes, seconds_to_timecode


class PDFReportExporter:
    """Generates official Amazon Prime Video Quality Control PDF Certificates."""

    @staticmethod
    def export(report: QCReportData, output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Typography & Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.white
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0ea5e9")
        )
        section_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0284c7")
        )
        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155")
        )
        bold_cell_style = ParagraphStyle(
            "BoldCell",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0f172a")
        )
        header_cell_style = ParagraphStyle(
            "HeaderCell",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.white
        )

        story = []

        # 1. Official Amazon Prime QC Header Banner
        header_table_data = [
            [
                Paragraph("<b>prime video</b><br/><font size='10' color='#cbd5e1'><b>QUALITY CONTROL INGESTION REPORT</b></font>", title_style),
                Paragraph(f"<b>DATA ANALISI:</b> {report.generated_at}<br/><b>PROFILO:</b> {report.profile_name}<br/><b>ENGINE:</b> PrimeQC Master v2.5", ParagraphStyle("H2", fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#94a3b8"), alignment=2))
            ]
        ]
        header_table = Table(header_table_data, colWidths=[280, 240])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # 2. Overall Ingestion Verdict Badge
        sev_rep_val = report.verdict.value if hasattr(report.verdict, "value") else str(report.verdict)
        if sev_rep_val == Severity.PASS.value:
            badge_bg = colors.HexColor("#059669")
            verdict_text = "APPROVATO (ACCEPTED) - CONFORME PER LA DISTRIBUZIONE SU AMAZON PRIME"
        elif sev_rep_val == Severity.WARNING.value:
            badge_bg = colors.HexColor("#d97706")
            verdict_text = "REVISIONE CONSIGLIATA (WARNING) - AVVISI RILEVATI"
        else:
            badge_bg = colors.HexColor("#dc2626")
            verdict_text = "RIGETTATO (REJECTED) - NON CONFORME AGLI STANDARD AMAZON PRIME"

        verdict_data = [
            [
                Paragraph(f"<b>ESITO: {verdict_text}</b>", ParagraphStyle("VText", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white)),
                Paragraph(f"<b>SCORE: {report.compliance_score:.1f}%</b>", ParagraphStyle("VScore", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white, alignment=2))
            ]
        ]
        verdict_table = Table(verdict_data, colWidths=[400, 120])
        verdict_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), badge_bg),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(verdict_table)
        story.append(Spacer(1, 12))

        # 3. Asset Technical Metadata Overview
        story.append(Paragraph("<b>1. SCHEDA TECNICA ASSET</b>", section_style))
        story.append(Spacer(1, 5))

        v_stream = report.video_streams[0] if report.video_streams else None
        v_res = f"{v_stream.width}x{v_stream.height}" if v_stream else "N/A"
        v_fps = f"{v_stream.fps:.3f} fps" if v_stream else "N/A"
        v_codec = f"{v_stream.codec_name} ({v_stream.profile})" if v_stream else "N/A"
        
        a_channels = sum(a.channels for a in report.audio_streams)
        loud_i = f"{report.loudness_data.get('integrated', -24.0):.1f} LUFS" if report.loudness_data else "N/A"
        true_p = f"{report.loudness_data.get('true_peak', -2.0):.2f} dBTP" if report.loudness_data else "N/A"

        overview_data = [
            [
                Paragraph("<b>Nome File:</b>", bold_cell_style), Paragraph(report.file_name, body_style),
                Paragraph("<b>Dimensione File:</b>", bold_cell_style), Paragraph(format_bytes(report.file_size_bytes), body_style)
            ],
            [
                Paragraph("<b>Container:</b>", bold_cell_style), Paragraph(report.container_info.get("format_name", "N/A").upper(), body_style),
                Paragraph("<b>Durata:</b>", bold_cell_style), Paragraph(f"{report.duration_sec:.2f}s ({seconds_to_timecode(report.duration_sec, v_stream.fps if v_stream else 24.0)})", body_style)
            ],
            [
                Paragraph("<b>Codec Video:</b>", bold_cell_style), Paragraph(v_codec, body_style),
                Paragraph("<b>Risoluzione / FPS:</b>", bold_cell_style), Paragraph(f"{v_res} @ {v_fps}", body_style)
            ],
            [
                Paragraph("<b>Scansione:</b>", bold_cell_style), Paragraph(v_stream.field_order.capitalize() if v_stream else "N/A", body_style),
                Paragraph("<b>Spazio Colore:</b>", bold_cell_style), Paragraph(v_stream.color_primaries.upper() if v_stream else "N/A", body_style)
            ],
            [
                Paragraph("<b>Tracce Audio:</b>", bold_cell_style), Paragraph(f"{a_channels} Canali ({len(report.audio_streams)} traccia/e)", body_style),
                Paragraph("<b>Loudness Integrata:</b>", bold_cell_style), Paragraph(f"{loud_i} (Target: -24.0 LKFS)", body_style)
            ],
            [
                Paragraph("<b>Max True Peak:</b>", bold_cell_style), Paragraph(f"{true_p} (Ceiling: -2.0 dBTP)", body_style),
                Paragraph("<b>Campionamento:</b>", bold_cell_style), Paragraph("48 kHz (48000 Hz) 24-bit" if report.audio_streams else "N/A", body_style)
            ]
        ]
        overview_table = Table(overview_data, colWidths=[95, 165, 95, 165])
        overview_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 12))

        # 4. Detailed Failure & Remediation Boxes (If any failures or warnings)
        failed_or_warn = [i for i in report.issues if (i.severity.value if hasattr(i.severity, "value") else str(i.severity)) in [Severity.FAIL.value, Severity.WARNING.value]]
        if failed_or_warn:
            story.append(Paragraph(f"<b>2. DETTAGLIO ERRORI BLOCCANTI E ISTRUZIONI DI CORREZIONE ({len(failed_or_warn)} ANOMALIE)</b>", section_style))
            story.append(Spacer(1, 6))

            for idx, issue in enumerate(failed_or_warn):
                is_fail = (issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity)) == Severity.FAIL.value
                box_bg = colors.HexColor("#fef2f2") if is_fail else colors.HexColor("#fffbeb")
                border_c = colors.HexColor("#dc2626") if is_fail else colors.HexColor("#d97706")
                badge_lbl = "<font color='#dc2626'><b>ERRORE BLOCCANTE (REJECTED)</b></font>" if is_fail else "<font color='#d97706'><b>AVVISO (WARNING)</b></font>"

                tc_text = f" | Timecode: <b>{issue.timecode}</b>" if issue.timecode and issue.timecode != "00:00:00:00" else ""

                card_data = [
                    [
                        Paragraph(f"<b>#{idx+1} | {issue.parameter} [{issue.id}]</b>{tc_text}", ParagraphStyle("C1", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=colors.HexColor("#0f172a"))),
                        Paragraph(badge_lbl, ParagraphStyle("C2", fontName="Helvetica", fontSize=8, leading=11, alignment=2))
                    ],
                    [
                        Paragraph(f"<b>Valore Rilevato:</b> <font color='#dc2626'>{issue.measured_value}</font><br/><b>Specifiche Amazon:</b> <font color='#059669'>{issue.expected_value}</font>", body_style),
                        Paragraph(f"<b>Perché Amazon rigetta:</b> {issue.description}", body_style)
                    ],
                    [
                        Paragraph(f"<b>🔧 Come correggerlo per passare il QC:</b> {issue.remediation_tip}", ParagraphStyle("Fix", fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#047857"))),
                        Paragraph("", body_style)
                    ]
                ]
                card_table = Table(card_data, colWidths=[260, 260])
                card_table.setStyle(TableStyle([
                    ("SPAN", (0, 2), (1, 2)),
                    ("BACKGROUND", (0, 0), (-1, -1), box_bg),
                    ("BOX", (0, 0), (-1, -1), 1, border_c),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(card_table)
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 8))

        # 5. Full Checkpoints Table
        story.append(Paragraph(f"<b>3. TABELLA COMPLETA CHECKPOINTS QC ({len(report.issues)} CONTROLLI)</b>", section_style))
        story.append(Spacer(1, 5))

        issues_data = [
            [
                Paragraph("STATO", header_cell_style),
                Paragraph("TIPO", header_cell_style),
                Paragraph("PARAMETRO", header_cell_style),
                Paragraph("TIMECODE", header_cell_style),
                Paragraph("VALORE RILEVATO", header_cell_style),
                Paragraph("SPECIFICA AMAZON", header_cell_style)
            ]
        ]

        for issue in report.issues:
            sev_val = issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity)
            stream_val = issue.stream_type.value if hasattr(issue.stream_type, "value") else str(issue.stream_type)

            if sev_val == Severity.FAIL.value:
                status_p = Paragraph(f"<font color='#dc2626'><b>FAIL</b></font>", bold_cell_style)
            elif sev_val == Severity.WARNING.value:
                status_p = Paragraph(f"<font color='#d97706'><b>WARN</b></font>", bold_cell_style)
            elif sev_val == Severity.NOTICE.value:
                status_p = Paragraph(f"<font color='#0284c7'><b>INFO</b></font>", bold_cell_style)
            else:
                status_p = Paragraph(f"<font color='#059669'><b>PASS</b></font>", bold_cell_style)

            issues_data.append([
                status_p,
                Paragraph(stream_val, body_style),
                Paragraph(f"<b>{issue.parameter}</b>", body_style),
                Paragraph(issue.timecode, body_style),
                Paragraph(issue.measured_value, body_style),
                Paragraph(issue.expected_value, body_style)
            ])

        issues_table = Table(issues_data, colWidths=[45, 55, 110, 60, 120, 130])
        issues_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 3.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
        ]))
        story.append(issues_table)
        story.append(Spacer(1, 10))

        # 6. Quality Control Sign-Off Block
        sign_data = [
            [
                Paragraph("<b>Motore di Verifica:</b> PrimeQC Master v2.5 (Broadcast Engine)", body_style),
                Paragraph("<b>Firma Operatore QC:</b> ________________________", body_style)
            ],
            [
                Paragraph(f"<b>Data Certificazione:</b> {report.generated_at}", body_style),
                Paragraph(f"<b>Stato Ingestione:</b> [{'X' if report.verdict == Severity.PASS else ' '}] Conforme  [{'X' if report.verdict == Severity.FAIL else ' '}] Non Conforme", body_style)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[260, 260])
        sign_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9"))
        ]))
        story.append(sign_table)

        # Build document
        doc.build(story)
        return output_path
