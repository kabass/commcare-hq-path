import json
from corehq.apps.sms.api import incoming as incoming_sms
from corehq.apps.sms.views import IncomingBackendView
from corehq.messaging.smsbackends.amazon_pinpoint.models import PinpointBackend
from django.http import HttpResponse

from corehq.util.public_only_requests.public_only_requests import get_public_only_session


class PinpointIncomingMessageView(IncomingBackendView):
    urlname = 'pinpoint_sms'

    @property
    def backend_class(self):
        return PinpointBackend

    def post(self, request, api_key, *args, **kwargs):
        request_body = json.loads(request.body)
        message = request_body.get('Message')
        subscribe_url = request_body.get('SubscribeURL')
        if subscribe_url:
            session = get_public_only_session(domain_name='n/a', src="pinpoint_sms")
            session.get(subscribe_url)
        elif message:
            message = json.loads(message)
            message_sid = message.get('inboundMessageId')
            from_ = message.get('originationNumber')
            body = message.get('messageBody')
            incoming_sms(
                from_,
                body,
                PinpointBackend.get_api_id(),
                backend_message_id=message_sid,
                domain_scope=self.domain,
                backend_id=self.backend_couch_id
            )
        return HttpResponse("")
