from odoo import models


class MailMessage(models.Model):
    _inherit = "mail.message"

    def _get_forbidden_access(self, operation):
        # Odoo blockerar unlink på Python-nivå oavsett ACL/ir.rule:
        # unlink kräver skrivrätt på det relaterade dokumentet, och
        # meddelanden utan model/res_id (t.ex. köade mail) nekas alltid.
        # Gruppen nedan går förbi just den spärren — ACL gäller fortfarande.
        if operation == "unlink" and self.env.user.has_group(
            "odoo_message_delete.group_message_delete"
        ):
            return self.browse()
        return super()._get_forbidden_access(operation)
