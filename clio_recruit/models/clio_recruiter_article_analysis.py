"""
clio_recruiter_article_analysis.py
Analyscache per artikel x profil for clio-agent-job rekryterarläge.

En rad per (article_id, profile_id) — lagrar Claude-analysresultatet sa att
en ny profil kan analysera befintliga artiklar utan att redan analyserade
(artikel, profil)-par kör Claude pa nytt.
"""

from __future__ import annotations

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ClioRecruiterArticleAnalysis(models.Model):
    _name        = "clio.recruiter.article_analysis"
    _description = "Clio Recruit — Analyscache per artikel och profil"
    _order       = "analyzed_at desc"
    _rec_name    = "article_id"

    article_id = fields.Char(
        string   = "Article ID",
        required = True,
        index    = True,
        help     = "SHA256-hash av URL — samma nyckel som i clio.job.article.",
    )
    profile_id = fields.Many2one(
        comodel_name = "clio.recruiter.profile",
        string       = "Rekryterarprofil",
        required     = True,
        ondelete     = "cascade",
        index        = True,
    )
    match_score = fields.Integer(
        string  = "Score",
        default = 0,
        help    = "0-100 fran Claude-analysen.",
    )
    signal_type = fields.Char(
        string = "Signaltyp",
        help   = "t.ex. plattformsbyte, varsel, outsourcing.",
    )
    recommended_action = fields.Text(
        string = "Rekommenderad atgard",
        help   = "kontakta_nu / bevaka_3man / bevaka_6man / avsta.",
    )
    contact_hint = fields.Text(
        string = "Kontakttips",
    )
    analyzed_at = fields.Datetime(
        string = "Analyserad",
        index  = True,
    )

    _article_profile_uniq = models.Constraint(
        "UNIQUE(article_id, profile_id)",
        "Analyscache: kombination av artikel och profil maste vara unik.",
    )
