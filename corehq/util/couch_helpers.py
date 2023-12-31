import base64
import hashlib
from copy import copy
from mimetypes import guess_type
from corehq.util.pagination import paginate_function, PaginationEventHandler, ArgsProvider


class CouchAttachmentsBuilder(object):
    """
    Helper for saving attachments on doc save rather than as a separate step.
    Example usage:

    Instead of the normal 1 + N request save where N is the # of attachments:

        foo = Foo()
        foo.save()
        foo.put_attachment(
            name=filename,
            content=content,
            content_type=mime_type
        )

    You can use the following to do a single-request save:

        foo = Foo()

        attachment_builder = CouchAttachmentsBuilder(foo._attachments)
        attachment_builder.add(
            name=filename,
            content=content,
            content_type=mime_type
        )
        foo._attachments = attachment_builder.to_json()

        foo.save(encode_attachments=False)


        # or bulk save
        Foo.get_db().bulk_save([foo, ...])

    NB: If you save without encode_attachments=False
    (here or later on down the line)
    then your attachment content will end up base64 encoded!
    That's a real thing that's happened in the past,
    so be careful who you're passing this object on to!
    (Think signals, etc. where you have no control over who uses it next
    and how/whether they call .save() on the object.)

    """

    def __init__(self, original=None):
        self._dict = original or {}

    @staticmethod
    def couch_style_digest(data):
        return 'md5-{}'.format(base64.b64encode(hashlib.md5(data).digest()))

    def no_change(self, name, data):
        return (
            self._dict.get(name) and
            self._dict[name].get('digest') == self.couch_style_digest(data)
        )

    def add(self, content, name=None, content_type=None):
        if hasattr(content, 'read'):
            if hasattr(content, 'seek'):
                content.seek(0)
            data = content.read()
        else:
            data = content
        if isinstance(data, str):
            data = data.encode('utf-8')
        if content_type is None:
            content_type = ';'.join(filter(None, guess_type(name)))
        # optimization alert:
        # don't make couch re-save attachment if there's no change in content
        if self.no_change(name, data):
            # just set the content_type in case it's different
            # don't know of any case where this matters
            # but seems semantically correct
            self._dict[name].update({
                'content_type': content_type,
            })
        else:
            self._dict[name] = {
                'data': base64.b64encode(data),
                'content_type': content_type,
            }

    def remove(self, name):
        """
        raises a `KeyError` if there's no attachment called `name`
        """
        del self._dict[name]

    def to_json(self):
        return copy(self._dict)


class NoSkipArgsProvider(ArgsProvider):
    """View pagination args provider that does not skip

    This handles an edge case where the last result in the previous page
    has been changed in a way that causes it to change position in or be
    removed from the view. In this case the typical strategy of skipping
    one result when loading the next page will cause a previously unseen
    document to be skipped.

    This more closely follows the pagination strategy outlined in the
    CouchDB docs (probably updated since the old skip 1 strategy was
    implemented--it mysteriously mentions using skip, but doesn't):
    https://docs.couchdb.org/en/stable/ddocs/views/pagination.html#paging-alternate-method
    """
    def __init__(self, initial_kwargs):
        self.initial_kwargs = initial_kwargs
        self.next_limit = initial_kwargs['limit'] + 1
        if self.next_limit < 2:
            raise ValueError("bad limit: {}".format(initial_kwargs['limit']))
        self._null = object()

    def get_initial_args(self):
        return [], self.initial_kwargs

    def adjust_results(self, results, args, kwargs):
        if results:
            last_seen_doc_id = kwargs.get("startkey_docid", self._null)
            if last_seen_doc_id == results[0]["id"]:
                # drop already processed result
                results = results[1:]
        return results

    def get_next_args(self, result, *last_args, **last_kwargs):
        if result:
            last_kwargs['startkey'] = result['key']
            last_kwargs['startkey_docid'] = result['id']
            last_kwargs['limit'] = self.next_limit
            return [], last_kwargs
        raise StopIteration


class PaginatedViewArgsProvider(ArgsProvider):
    def __init__(self, initial_view_kwargs):
        self.initial_view_kwargs = initial_view_kwargs

    def get_initial_args(self):
        return [], self.initial_view_kwargs

    def get_next_args(self, result, *last_args, **last_view_kwargs):
        if result:
            last_view_kwargs['startkey'] = result['key']
            last_view_kwargs['startkey_docid'] = result['id']
            last_view_kwargs['skip'] = 1
            return [], last_view_kwargs
        else:
            raise StopIteration


class MultiKeyViewArgsProvider(PaginatedViewArgsProvider):
    """Argument provider for iterating over a view using multiple keys.
    :param keys: Sequence of view keys to iterate over. Each key should be a list
    and all keys must have the same length.
    """
    def __init__(self, keys, include_docs=False, chunk_size=1000):
        self.keys = list(keys)
        first_key = self.keys[0]
        self.key_length = len(first_key)
        if isinstance(first_key, list):
            assert all(len(key) == self.key_length for key in self.keys), "All keys must be the same length"

        view_kwargs = {
            'limit': chunk_size,
            'include_docs': include_docs,
            'reduce': False,
        }
        view_kwargs.update(self._get_key_kwargs(first_key))
        super(MultiKeyViewArgsProvider, self).__init__(view_kwargs)

    def get_next_args(self, result, *last_args, **last_view_kwargs):
        try:
            return super(MultiKeyViewArgsProvider, self).get_next_args(
                result, *last_args, **last_view_kwargs
            )
        except StopIteration:
            # all docs for the current key have been processed
            # move on to the next key combo
            last_key = last_view_kwargs["startkey"]
            if isinstance(last_key, list):
                last_key = last_key[:self.key_length]
            key_index = self.keys.index(last_key) + 1
            self.keys = self.keys[key_index:]
            try:
                next_key = self.keys[0]
            except IndexError:
                raise StopIteration
            last_view_kwargs.pop('skip', None)
            last_view_kwargs.pop("startkey_docid", None)
            last_view_kwargs.update(self._get_key_kwargs(next_key))
        return last_args, last_view_kwargs

    def _get_key_kwargs(self, key):
        if isinstance(key, list):
            return {
                'startkey': key,
                'endkey': key + [{}]
            }
        else:
            return {
                'startkey': key,
                'endkey': key
            }


class MultiKwargViewArgsProvider(PaginatedViewArgsProvider):
    """Argument provider for iterating over a view using a list of kwargs each with 'startkey' and 'endkey'.
    :param keys: Sequence of view keys to iterate over. Each key should be a dict with 'startkey' and 'endkey'
    """
    def __init__(self, keys: dict, include_docs=False, chunk_size=1000):
        self.keys = list(keys)
        first_key = self.keys[0]
        assert all(isinstance(key, dict) for key in self.keys), "All keys must be dictionaries"
        expected_keys = {'startkey', 'endkey'}
        assert all(expected_keys == set(key) for key in keys), "All keys must have 'startkey' and 'endkey' only"

        view_kwargs = {
            'limit': chunk_size,
            'include_docs': include_docs,
            'reduce': False,
        }
        view_kwargs.update(first_key)
        super(MultiKwargViewArgsProvider, self).__init__(view_kwargs)

    def get_next_args(self, result, *last_args, **last_view_kwargs):
        try:
            return super(MultiKwargViewArgsProvider, self).get_next_args(
                result, *last_args, **last_view_kwargs
            )
        except StopIteration:
            last_end_key = last_view_kwargs['endkey']
            key_index = 0
            for key_index, key in enumerate(self.keys):
                if key['endkey'] == last_end_key:
                    break

            # all docs for the current key have been processed
            # move on to the next key combo
            self.keys = self.keys[key_index + 1:]
            try:
                next_key = self.keys[0]
            except IndexError:
                raise StopIteration
            last_view_kwargs.pop('skip', None)
            last_view_kwargs.pop("startkey_docid", None)
            last_view_kwargs.update(next_key)
        return last_args, last_view_kwargs


def paginate_view(db, view_name, chunk_size, event_handler=PaginationEventHandler(), **view_kwargs):
    """
    intended as a more performant drop-in replacement for

        iter(db.view(view_name, **kwargs))

    intended specifically to be more performant when dealing with
    large numbers of rows

    Note: If the contents of the couch view do not change over the duration of
    the paginate_view call, this is guaranteed to have the same results
    as a direct view call. If the view is updated, however,
    paginate_views may skip docs that were added/updated during this period
    or may include docs that were removed/updated during this period.
    For this reason, it's best to use this with views that update infrequently
    or that are sorted by date modified and/or add-only,
    or when exactness is not a strict requirement

    chunk_size is how many docs to fetch per request to couchdb

    """
    if view_kwargs.get('reduce', True):
        raise ValueError('paginate_view must be called with reduce=False')

    if 'limit' in view_kwargs:
        raise ValueError('paginate_view cannot be called with limit')

    if 'skip' in view_kwargs:
        raise ValueError('paginate_view cannot be called with skip')

    view_kwargs['limit'] = chunk_size

    def call_view(**view_kwargs):
        return db.view(view_name, **view_kwargs)

    args_provider = PaginatedViewArgsProvider(view_kwargs)

    for result in paginate_function(call_view, args_provider, event_handler):
        yield result
