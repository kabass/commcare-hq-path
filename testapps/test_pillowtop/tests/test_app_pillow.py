import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase

from pillowtop.feed.couch import get_current_seq

from corehq.apps.app_manager.models import Application
from corehq.apps.app_manager.tasks import (
    autogenerate_build,
    prune_auto_generated_builds,
)
from corehq.apps.app_manager.tests.app_factory import AppFactory
from corehq.apps.change_feed import topics
from corehq.apps.change_feed.consumer.feed import (
    change_meta_from_kafka_message,
)
from corehq.apps.change_feed.pillow import get_application_db_kafka_pillow
from corehq.apps.change_feed.tests.utils import get_test_kafka_consumer
from corehq.apps.change_feed.topics import get_topic_offset
from corehq.apps.es import AppES
from corehq.apps.es.apps import app_adapter
from corehq.apps.es.client import manager
from corehq.apps.es.tests.utils import es_test
from corehq.form_processor.tests.utils import FormProcessorTestUtils
from corehq.pillows.application import get_app_to_elasticsearch_pillow
from corehq.util.test_utils import flaky_slow


@es_test(requires=[app_adapter])
class AppPillowTest(TestCase):

    domain = 'app-pillowtest-domain'

    def setUp(self):
        super(AppPillowTest, self).setUp()
        FormProcessorTestUtils.delete_all_cases()

    def tearDown(self):
        super(AppPillowTest, self).tearDown()

    @flaky_slow
    def test_app_pillow_kafka(self):
        consumer = get_test_kafka_consumer(topics.APP)
        # have to get the seq id before the change is processed
        kafka_seq = get_topic_offset(topics.APP)
        couch_seq = get_current_seq(Application.get_db())

        app_name = 'app-{}'.format(uuid.uuid4().hex)
        app = self._create_app(app_name)

        app_db_pillow = get_application_db_kafka_pillow('test_app_db_pillow')
        app_db_pillow.process_changes(couch_seq, forever=False)

        # confirm change made it to kafka
        message = next(consumer)
        change_meta = change_meta_from_kafka_message(message.value)
        self.assertEqual(app._id, change_meta.document_id)
        self.assertEqual(self.domain, change_meta.domain)

        # send to elasticsearch
        app_pillow = get_app_to_elasticsearch_pillow()
        app_pillow.process_changes(since=kafka_seq, forever=False)
        manager.index_refresh(app_adapter.index_name)

        # confirm change made it to elasticserach
        results = AppES().run()
        self.assertEqual(1, results.total)
        app_doc = results.hits[0]
        self.assertEqual(self.domain, app_doc['domain'])
        self.assertEqual(app['_id'], app_doc['_id'])
        self.assertEqual(app_name, app_doc['name'])

    def _create_app(self, name, cleanup=True):
        factory = AppFactory(domain=self.domain, name=name, build_version='2.11.0')
        module1, form1 = factory.new_basic_module('open_case', 'house')
        factory.form_opens_case(form1)
        app = factory.app
        app.save()
        if cleanup:
            self.addCleanup(app.delete)
        return app

    def refresh_elasticsearch(self, kafka_seq, couch_seq):
        app_db_pillow = get_application_db_kafka_pillow('test_app_db_pillow')
        app_db_pillow.process_changes(couch_seq, forever=False)
        app_pillow = get_app_to_elasticsearch_pillow()
        app_pillow.process_changes(since=kafka_seq, forever=False)
        manager.index_refresh(app_adapter.index_name)

    @flaky_slow
    @patch.object(Application, 'validate_app', list)
    @patch.object(Application, 'create_build_files', MagicMock())
    def test_prune_autogenerated_builds(self):
        kafka_seq = get_topic_offset(topics.APP)
        couch_seq = get_current_seq(Application.get_db())
        # Build #1, manually generated
        app = self._create_app('test-prune-app')
        build1 = app.make_build()
        build1.save()
        self.assertFalse(build1.is_auto_generated)

        # Build #2, auto-generated
        app.save()
        autogenerate_build(app, 'username')

        # Build #3, manually generated
        app.save()
        build3 = app.make_build()
        build3.save()

        # All 3 builds should show up in ES
        self.refresh_elasticsearch(kafka_seq, couch_seq)
        build_ids_in_es = AppES().domain(self.domain).is_build().values_list('_id', flat=True)
        self.assertEqual(len(build_ids_in_es), 3)

        # prune, which should delete the autogenerated build
        prune_auto_generated_builds(self.domain, app.id)

        # Build2 should no longer be in ES
        self.refresh_elasticsearch(kafka_seq, couch_seq)
        build_ids_in_es = AppES().domain(self.domain).is_build().values_list('_id', flat=True)
        self.assertItemsEqual(build_ids_in_es, [build1._id, build3._id])

    def test_hard_delete_app(self):
        consumer = get_test_kafka_consumer(topics.APP)
        # have to get the seq id before the change is processed
        kafka_seq = get_topic_offset(topics.APP)
        couch_seq = get_current_seq(Application.get_db())

        app = self._create_app('test_hard_deleted_app', cleanup=False)
        app_db_pillow = get_application_db_kafka_pillow('test_app_db_pillow')
        app_db_pillow.process_changes(couch_seq, forever=False)

        # confirm change made it to kafka
        message = next(consumer)
        change_meta = change_meta_from_kafka_message(message.value)
        self.assertEqual(app._id, change_meta.document_id)
        self.assertEqual(self.domain, change_meta.domain)

        # send to elasticsearch
        app_pillow = get_app_to_elasticsearch_pillow()
        app_pillow.process_changes(since=kafka_seq, forever=False)
        manager.index_refresh(app_adapter.index_name)

        # confirm change made it to elasticserach
        results = AppES().run()
        self.assertEqual(1, results.total)

        couch_seq = get_current_seq(Application.get_db())
        kafka_seq = get_topic_offset(topics.APP)

        app.delete()
        app_db_pillow.process_changes(couch_seq, forever=False)

        # confirm change made it to kafka. Would raise StopIteration otherwise
        next(consumer)

        # send to elasticsearch
        app_pillow = get_app_to_elasticsearch_pillow()
        app_pillow.process_changes(since=kafka_seq, forever=False)
        manager.index_refresh(app_adapter.index_name)

        # confirm deletion made it to elasticserach
        results = AppES().run()
        self.assertEqual(0, results.total)