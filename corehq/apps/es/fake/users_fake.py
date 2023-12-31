from corehq.apps.es.fake.es_query_fake import HQESQueryFake
from corehq.apps.es.users import user_adapter


class UserESFake(HQESQueryFake):
    _all_docs = []

    def domain(self, domain):
        return self._filtered(
            lambda doc: (doc.get('domain') == domain
                         or domain in doc.get('domains', [])))

    def primary_location(self, location_id):
        return self.term('location_id', location_id)

    def location(self, location_id):
        return self.term('assigned_location_ids', location_id)

    def mobile_users(self):
        return self.term("doc_type", "CommCareUser")

    def user_ids(self, user_ids):
        return self.term('_id', user_ids)

    @staticmethod
    def transform_doc(doc):
        doc['username.exact'] = doc.get('username', '')
        return user_adapter.to_json(doc)

    def count(self):
        return len(self._result_docs)
