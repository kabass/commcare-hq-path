import uuid
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import RequestFactory

from corehq.apps.domain.shortcuts import create_domain
from corehq.apps.reports.standard.sms import MessageLogReport
from corehq.apps.sms.models import SMS
from corehq.apps.sms.tests.data_generator import (
    make_simple_sms_for_test,
    make_case_rule_sms_for_test,
    make_survey_sms_for_test
)
from corehq.apps.users.models import WebUser
from corehq.util.test_utils import flag_enabled
from dimagi.utils.dates import DateSpan


@flag_enabled('SMS_LOG_CHANGES')
class MessageLogReportTest(TestCase):
    domain = uuid.uuid4().hex

    def test_basic_functionality(self):
        self.make_simple_sms('message 1')
        self.make_simple_sms('message 2')
        self.assertEqual(
            self.get_report_column('Message'),
            ['message 1', 'message 2'],
        )

    def test_event_column(self):
        self.make_simple_sms('message')
        self.make_case_rule_sms('Rule 2')
        # This sms tests this particular condition
        self.make_survey_sms('Rule 3')

        for report_value, rule_name in zip(
            self.get_report_column('Event'),
            ['-', 'Rule 2', 'Rule 3'],
        ):
            # The cell value should be a link to the rule
            self.assertIn(rule_name, report_value)

    def test_include_erroring_sms_status(self):
        self.make_simple_sms('message 1', error_message=SMS.ERROR_INVALID_DIRECTION)
        self.make_simple_sms('message 2')
        self.assertEqual(
            self.get_report_column('Status'),
            ['Error - Unknown message direction.', 'Sent'],
        )

    @classmethod
    def setUpClass(cls):
        super(MessageLogReportTest, cls).setUpClass()
        cls.domain_obj = create_domain(cls.domain)
        cls.factory = RequestFactory()
        cls.couch_user = WebUser.create(None, "phone_report_test", "foobar", None, None)
        cls.couch_user.add_domain_membership(cls.domain, is_admin=True)
        cls.couch_user.save()

    @classmethod
    def tearDownClass(cls):
        cls.couch_user.delete(cls.domain, deleted_by=None)
        cls.domain_obj.delete()
        super(MessageLogReportTest, cls).tearDownClass()

    def get_report_column(self, column_header):
        return [row[column_header] for row in self.get_report_rows()]

    def get_report_rows(self):
        request = self.factory.get('/')
        request.couch_user = self.couch_user
        request.datespan = DateSpan(
            startdate=datetime.utcnow() - timedelta(days=30),
            enddate=datetime.utcnow(),
        )
        report = MessageLogReport(request, domain=self.domain)
        headers = [h.html for h in report.headers.header]
        for row in report.export_rows:
            yield dict(zip(headers, row))

    def make_simple_sms(self, message, error_message=None):
        sms = make_simple_sms_for_test(self.domain, message, error_message)
        self.addCleanup(sms.delete)

    def make_case_rule_sms(self, rule_name):
        rule, event, sms = make_case_rule_sms_for_test(self.domain, rule_name)
        self.addCleanup(rule.delete)
        self.addCleanup(event.delete)  # cascades to subevent
        self.addCleanup(sms.delete)

    def make_survey_sms(self, rule_name):
        rule, xforms_session, event, sms = make_survey_sms_for_test(self.domain, rule_name)
        self.addCleanup(rule.delete)
        self.addCleanup(xforms_session.delete)
        self.addCleanup(event.delete)  # cascades to subevent
        self.addCleanup(sms.delete)
