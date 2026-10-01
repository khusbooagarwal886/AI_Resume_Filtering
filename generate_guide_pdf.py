"""
Generate a concise, beautifully formatted 2-page PDF guide explaining all pipeline steps, commands, and outputs.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

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
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 756, "AI Resume Screening & Ranking System — Architecture & Execution Guide")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(40, 750, 572, 750)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 24, page_str)
        self.drawString(40, 24, "SDE Intern (AI) Assignment — Kasparro")
        self.restoreState()


def build_pdf(filename="AI_Resume_Screening_System_Walkthrough.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=38,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e40af")
    )

    story = []

    # Title Block
    story.append(Paragraph("AI Resume Screening & Ranking System", title_style))
    story.append(Paragraph("Engineering Architecture, Pipeline Steps, and Execution Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=6))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview & Goals", h1_style))
    story.append(Paragraph(
        "A production-minded AI Resume Screening & Ranking System designed for evaluating candidates for an "
        "<b>SDE Intern (AI/Agentic Systems)</b> role. Prioritizing <b>engineering judgment, explainability, correctness, and speed</b>, "
        "it processes batches of resumes, applies strict rule-based eligibility filtering, enriches profiles with GitHub telemetry, "
        "and scores eligible candidates against a 100-point rubric with actionable reasoning.",
        body_style
    ))

    # Architecture Overview Table
    summary_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology / Implementation</b>", body_style), Paragraph("<b>Key Responsibility</b>", body_style)],
        [Paragraph("<b>Language & Runtime</b>", body_style), Paragraph("Python 3.12, Asyncio", body_style), Paragraph("High throughput, non-blocking concurrent batch execution", body_style)],
        [Paragraph("<b>PDF Parser</b>", body_style), Paragraph("pypdf (Multi-page)", body_style), Paragraph("Robust text & contact extraction, malformed error-tolerant", body_style)],
        [Paragraph("<b>Eligibility Filter</b>", body_style), Paragraph("Rule-Based Regex Engine", body_style), Paragraph("Zero-token pre-filter for Python & AI requirements", body_style)],
        [Paragraph("<b>GitHub Telemetry</b>", body_style), Paragraph("GitHub REST API + TTL Cache", body_style), Paragraph("Velocity & repo signals (0-10 pts), rate-limit tolerant", body_style)],
        [Paragraph("<b>Scoring Engine</b>", body_style), Paragraph("100-pt Rubric + Penalties", body_style), Paragraph("Deterministic baseline + Gemini structured output", body_style)],
        [Paragraph("<b>Interfaces</b>", body_style), Paragraph("CLI + FastAPI REST API", body_style), Paragraph("main.py CLI and interactive Swagger API endpoints", body_style)]
    ]
    t_summary = Table(summary_data, colWidths=[120, 150, 262])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 4))

    # Pipeline Steps
    story.append(Paragraph("2. Pipeline Execution Steps", h1_style))
    
    story.append(Paragraph("Step 1: Resume Ingestion & Normalization (<font name='Courier'>src/extractor.py</font>)", h2_style))
    story.append(Paragraph(
        "• Concurrently ingests all PDFs from the input directory.<br/>"
        "• Concatenates text across multi-page layouts and extracts candidate name (handling multi-column Canva layouts & merged lines), email, phone, GitHub profile, LinkedIn, and skills.<br/>"
        "• <i>Fault Tolerance:</i> Malformed or unreadable files are skipped cleanly without halting the batch run.",
        bullet_style
    ))

    story.append(Paragraph("Step 2: Hard Eligibility Rule-Based Filter (<font name='Courier'>src/filters.py</font>)", h2_style))
    story.append(Paragraph(
        "• <b>Python Evidence (Condition 1):</b> Requires explicit Python stack keywords (Python, FastAPI, Django, Flask, PyTorch, Pandas, Asyncio). Non-Python profiles are rejected.<br/>"
        "• <b>AI / Agentic Evidence (Condition 2):</b> Requires meaningful AI project exposure (LangChain, LangGraph, RAG, Vector Search, Tool-Calling, ChromaDB, LlamaIndex).<br/>"
        "• <b>Permissive Stack Policy:</b> JavaScript, React, or Next.js do <i>not</i> trigger rejection if Python + AI are satisfied.<br/>"
        "• <i>Efficiency:</i> Executes deterministically outside the LLM to eliminate token waste and prevent hallucinations.",
        bullet_style
    ))

    story.append(Paragraph("Step 3: GitHub Telemetry & In-Memory Caching (<font name='Courier'>src/github.py</font>)", h2_style))
    story.append(Paragraph(
        "• Queries GitHub REST API (<font name='Courier'>/users/{username}</font> & <font name='Courier'>/repos</font>) with TTL cache.<br/>"
        "• Scores activity up to 10 pts (0–5 pts for recent updates + 0–5 pts for maintained Python/AI repositories and stars).<br/>"
        "• <i>Graceful Fallback:</i> Rate limits (HTTP 403), missing profiles, or offline networks record a note without crashing.",
        bullet_style
    ))

    story.append(Paragraph("Step 4: 100-Point Candidate Scoring & Penalties (<font name='Courier'>src/scoring.py</font>)", h2_style))
    story.append(Paragraph(
        "• <b>AI Project Depth (40 pts):</b> Agents, LangGraph, RAG, embeddings, vector databases, tool-calling.<br/>"
        "• <b>Python & Backend (30 pts):</b> FastAPI, Asyncio, PostgreSQL, Redis, database modeling.<br/>"
        "• <b>Cloud & Full Stack (15 pts):</b> GCP, Docker containers, CI/CD, React/Next.js supporting frontend.<br/>"
        "• <b>GitHub Activity (10 pts):</b> Velocity and repository maintenance signals.<br/>"
        "• <b>Engineering Depth (5 pts):</b> Pytest automated testing, clean architecture, message queues, observability.<br/>"
        "• <b>Project Quality Penalties (-5 to -15 pts):</b> Deductions for shallow API wrappers (e.g. basic prompt + Streamlit) and tutorial clones.",
        bullet_style
    ))

    story.append(Paragraph("Step 5: Ranking & Explainable Output (<font name='Courier'>src/pipeline.py</font>)", h2_style))
    story.append(Paragraph(
        "• Eligible candidates are sorted descending by total score and assigned 1-indexed ranks (1, 2, 3...).<br/>"
        "• Rejected candidates receive rank <font name='Courier'>null</font> and explicit rejection reasons.<br/>"
        "• Produces structured JSON output, CSV spreadsheet export, and rich terminal summary table.",
        bullet_style
    ))

    story.append(PageBreak())

    # How to Run & CLI Commands
    story.append(Paragraph("3. How to Run & Output Commands", h1_style))
    story.append(Paragraph("The system provides both a high-performance CLI and an interactive FastAPI REST interface.", body_style))

    commands = [
        ("1. Standard Batch Screening (JSON Output)",
         "python main.py --input ./resumes --output ./output/results.json",
         "Ingests all resumes in `./resumes`, scores candidates, prints a formatted terminal summary table, and writes structured JSON to `./output/results.json`."),
        ("2. Dual Export (JSON + CSV Spreadsheet)",
         "python main.py --input ./resumes --output ./output/results.json --csv ./output/results.csv",
         "Generates both machine-readable JSON results and a clean spreadsheet CSV containing ranks, scores, and rejection reasons."),
        ("3. Pure Deterministic Offline Mode",
         "python main.py --input ./resumes --output ./output/results.json --no-llm",
         "Runs 100% locally with zero external API calls or token consumption."),
        ("4. Start FastAPI Web Service",
         "python main.py --serve --port 8000",
         "Boots the Uvicorn web server at `http://localhost:8000`. Interactive Swagger docs available at `http://localhost:8000/docs`."),
        ("5. Run Automated Test Suite",
         "pytest -v",
         "Runs all 19 unit and integration tests across extraction, filters, scoring, pipeline, and FastAPI endpoints.")
    ]

    for title, cmd, desc in commands:
        cmd_table = Table([
            [Paragraph(f"<b>{title}</b>", body_style)],
            [Paragraph(f"<font color='#1d4ed8'><b>{cmd}</b></font>", code_style)],
            [Paragraph(f"<i>{desc}</i>", body_style)]
        ], colWidths=[532])
        cmd_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(cmd_table)
        story.append(Spacer(1, 4))

    # Results on 50 Candidate Resumes
    story.append(Paragraph("4. Batch Results Summary (50 Resumes)", h1_style))

    batch_metrics = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Count</b>", body_style), Paragraph("<b>Percentage</b>", body_style), Paragraph("<b>Notes</b>", body_style)],
        [Paragraph("Total Ingested", body_style), Paragraph("50", body_style), Paragraph("100%", body_style), Paragraph("All PDF resumes processed in batch", body_style)],
        [Paragraph("Successfully Parsed", body_style), Paragraph("50", body_style), Paragraph("100%", body_style), Paragraph("Zero unreadable / crashed files", body_style)],
        [Paragraph("Passed Eligibility", body_style), Paragraph("34", body_style), Paragraph("68%", body_style), Paragraph("Satisfied Python + AI project conditions", body_style)],
        [Paragraph("Rejected Candidates", body_style), Paragraph("16", body_style), Paragraph("32%", body_style), Paragraph("Non-Python or non-AI stack profiles", body_style)]
    ]
    t_metrics = Table(batch_metrics, colWidths=[120, 55, 75, 282])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 6))

    # Top Ranked Table
    story.append(Paragraph("Top 6 Ranked Shortlisted Candidates:", h2_style))
    top_candidates = [
        [Paragraph("<b>Rank</b>", body_style), Paragraph("<b>Candidate</b>", body_style), Paragraph("<b>Score</b>", body_style), Paragraph("<b>AI</b>", body_style), Paragraph("<b>Py</b>", body_style), Paragraph("<b>Cld</b>", body_style), Paragraph("<b>GH</b>", body_style), Paragraph("<b>Eng</b>", body_style), Paragraph("<b>Source File</b>", body_style)],
        [Paragraph("1", body_style), Paragraph("V Sree Raghu Vardhan", body_style), Paragraph("<b>87.0</b>", body_style), Paragraph("40.0", body_style), Paragraph("30.0", body_style), Paragraph("13.0", body_style), Paragraph("2.0", body_style), Paragraph("2.0", body_style), Paragraph("candidate_30.pdf", body_style)],
        [Paragraph("2", body_style), Paragraph("Yash Maini", body_style), Paragraph("<b>85.0</b>", body_style), Paragraph("40.0", body_style), Paragraph("27.0", body_style), Paragraph("15.0", body_style), Paragraph("2.0", body_style), Paragraph("1.0", body_style), Paragraph("candidate_13.pdf", body_style)],
        [Paragraph("3", body_style), Paragraph("Hari Shanker Sharma", body_style), Paragraph("<b>85.0</b>", body_style), Paragraph("36.0", body_style), Paragraph("30.0", body_style), Paragraph("13.0", body_style), Paragraph("2.0", body_style), Paragraph("4.0", body_style), Paragraph("candidate_41.pdf", body_style)],
        [Paragraph("4", body_style), Paragraph("Arjun Kumar", body_style), Paragraph("<b>83.0</b>", body_style), Paragraph("40.0", body_style), Paragraph("27.0", body_style), Paragraph("13.0", body_style), Paragraph("2.0", body_style), Paragraph("1.0", body_style), Paragraph("candidate_08.pdf", body_style)],
        [Paragraph("5", body_style), Paragraph("Vaibhav Wakde", body_style), Paragraph("<b>82.0</b>", body_style), Paragraph("40.0", body_style), Paragraph("26.0", body_style), Paragraph("9.0", body_style), Paragraph("2.0", body_style), Paragraph("5.0", body_style), Paragraph("candidate_33.pdf", body_style)],
        [Paragraph("6", body_style), Paragraph("Arunima Saha", body_style), Paragraph("<b>81.0</b>", body_style), Paragraph("40.0", body_style), Paragraph("21.0", body_style), Paragraph("15.0", body_style), Paragraph("2.0", body_style), Paragraph("3.0", body_style), Paragraph("candidate_43.pdf", body_style)]
    ]
    t_top = Table(top_candidates, colWidths=[30, 140, 42, 38, 38, 38, 38, 38, 130])
    t_top.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_top)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {os.path.abspath(filename)}")


if __name__ == "__main__":
    build_pdf()
