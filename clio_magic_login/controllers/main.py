import logging
from urllib.parse import quote as url_quote, urlencode as url_encode

from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.home import ensure_db
from odoo.http import request

_logger = logging.getLogger(__name__)

MAGIC_LINK_EXPIRY_HOURS = 0.25  # 15 minutes


class MagicLoginController(AuthSignupHome):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()

        if request.httprequest.method == 'POST' and request.params.get('type') == 'magic_link':
            return self._magic_link_send(**kw)

        response = super().web_login(*args, **kw)

        qcontext = getattr(response, 'qcontext', None)
        if qcontext is not None and request.httprequest.method == 'GET' and not request.session.uid:
            qcontext['magic_link_sent'] = bool(request.params.get('magic_link_sent'))
            if request.params.get('magic_login_error'):
                qcontext['error'] = request.params.get('magic_login_error')
            new_response = request.render('clio_magic_login.login', qcontext)
            new_response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            new_response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
            return new_response

        return response

    @http.route('/web/magic_login/verify', type='http', auth='none', methods=['GET'], csrf=False)
    def magic_login_verify(self, token='', redirect='', **kw):
        ensure_db()

        try:
            partner = request.env['res.partner'].sudo()._get_partner_from_token(token)
        except Exception:
            partner = None

        if not partner:
            return self._magic_login_redirect_error(_("Inloggningslänken är ogiltig eller har redan använts."))

        if not partner.user_ids:
            return self._magic_login_redirect_error(_("Inget konto är kopplat till den här länken."))

        user = partner.user_ids[0]

        if user._is_internal():
            return self._magic_login_redirect_error(_("Interna användare loggar in med lösenord."))

        if not user.active:
            return self._magic_login_redirect_error(_("Kontot är inaktiverat."))

        partner.sudo().write({'signup_type': False})

        request.session['pre_login'] = user.login
        request.session['pre_uid'] = user.id
        request.session.finalize(request.env)
        request.update_env(user=user)

        _logger.info("Magic link login: user %s (%s) logged in from %s",
                     user.login, user.id, request.httprequest.remote_addr)

        if not (redirect and redirect.startswith('/') and not redirect.startswith('//')):
            redirect = '/odoo'
        return request.redirect(redirect)

    def _magic_link_send(self, login='', redirect='', **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext.update(self.get_auth_signup_config())

        login = login.strip().lower()
        if not login:
            qcontext['error'] = _("Ange din e-postadress.")
            new_response = request.render('clio_magic_login.login', qcontext)
            new_response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            return new_response

        User = request.env['res.users'].sudo()
        user = User.search([
            ('login', '=', login),
            ('active', '=', True),
            ('share', '=', True),  # portal/public users only
        ], limit=1)

        if user:
            try:
                self._send_magic_link_email(user, redirect)
                qcontext['magic_link_sent'] = True
            except Exception:
                _logger.exception("Failed to send magic link to %s", login)
                qcontext['error'] = _("Något gick fel vid mailutskicket. Försök igen om en stund.")
        else:
            # Unknown address — notify admin silently, don't reveal to visitor
            try:
                self._notify_admin_unknown_login(login)
            except Exception:
                _logger.exception("Failed to send admin notification for unknown login %s", login)
            qcontext['magic_link_sent'] = True  # security: don't reveal whether account exists

        new_response = request.render('clio_magic_login.login', qcontext)
        new_response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        new_response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return new_response

    def _send_magic_link_email(self, user, redirect=''):
        partner = user.partner_id.sudo()
        # signup_prepare is the correct Odoo 19 API — writes token to partner.signup_token
        partner.signup_prepare(signup_type='magic', expiration=MAGIC_LINK_EXPIRY_HOURS)
        token = partner.signup_token

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        verify_url = '%s/web/magic_login/verify?token=%s' % (base_url, token)
        if redirect:
            verify_url += '&redirect=%s' % url_quote(redirect)

        template = request.env.ref(
            'clio_magic_login.email_template_magic_link', raise_if_not_found=False
        )
        if not template:
            raise RuntimeError("Mail-template clio_magic_login.email_template_magic_link saknas")

        # Use company email as sender — generic, works in any database
        company = user.sudo().company_id
        email_from = (
            company.email
            or request.env['ir.config_parameter'].sudo().get_param('mail.default.from', '')
        )
        email_values = {'email_from': email_from} if email_from else {}

        template.sudo().with_context(verify_url=verify_url).send_mail(
            user.id, force_send=True, email_values=email_values
        )

    def _notify_admin_unknown_login(self, login):
        ICP = request.env['ir.config_parameter'].sudo()
        notify_email = ICP.get_param('clio_magic_login.admin_notify_email', '')
        company = request.env['res.company'].sudo().search([], limit=1, order='id asc')
        if not notify_email:
            notify_email = company.email if company else ''
        if not notify_email:
            _logger.warning(
                "clio_magic_login: ingen admin-epost konfigurerad "
                "(clio_magic_login.admin_notify_email), hoppar notis för %s", login
            )
            return

        company_name = company.name if company else request.env.cr.dbname
        from_email = company.email if company else ''

        request.env['mail.mail'].sudo().create({
            'subject': f'Magic login-försök — okänd e-post ({company_name})',
            'email_from': from_email,
            'email_to': notify_email,
            'body_html': (
                f'<p>En e-postadress som saknar portalkonto försökte logga in via magic link:</p>'
                f'<p><strong>{login}</strong></p>'
                f'<p>Databas: {request.env.cr.dbname} ({company_name})<br>'
                f'IP: {request.httprequest.remote_addr}</p>'
                f'<p>Vill du ge personen tillgång? Lägg till dem som portalanvändare i Odoo.</p>'
            ),
            'auto_delete': True,
        }).send()

    def _magic_login_redirect_error(self, message):
        url = '/web/login?%s' % url_encode({'magic_login_error': message})
        return request.redirect(url)
