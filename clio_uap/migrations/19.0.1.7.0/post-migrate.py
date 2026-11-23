import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Flytta afu_article_id (heltal) till relationen article_ids (Källdokument).

    afu_article_id lämnas orört för spårbarhet. Länkar till artiklar som inte
    längre finns hoppas över.
    """
    cr.execute("""
        INSERT INTO uap_encounter_article_rel (encounter_id, article_id)
        SELECT e.id, e.afu_article_id
          FROM uap_encounter e
          JOIN clio_media_article a ON a.id = e.afu_article_id
         WHERE COALESCE(e.afu_article_id, 0) > 0
        ON CONFLICT DO NOTHING
    """)
    _logger.info("clio_uap 19.0.1.7.0: %s AFU-länkar flyttade till article_ids", cr.rowcount)
