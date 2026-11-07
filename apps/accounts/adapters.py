from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=""):
        # Drop allauth's chatty "Confirmation email sent…" flash.
        skip_templates = {
            "account/messages/email_confirmation_sent.txt",
            "account/messages/email_confirmed.txt",
            "account/messages/logged_in.txt",
        }
        if message_template in skip_templates:
            return
        super().add_message(request, level, message_template,
                            message_context, extra_tags)