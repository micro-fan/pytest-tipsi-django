import json
import os
from contextlib import contextmanager
from io import BytesIO
from pprint import pformat

from django.http.multipartparser import LazyStream, Parser


class APIError(Exception):
    def __init__(self, *args, resp, expected):
        super().__init__(*args)
        self.resp = resp
        self.expected = expected


class RequestVerbose:
    def __init__(self, request, pretty_json=True):
        func = request.function
        self.module = func.__module__
        self.test_name = func.__name__

        self.pretty_json = pretty_json
        self.verbose = True
        self.records = []
        self._silent = False

    def prettify_multipart(self, s):
        chunks = {}
        for (_type, meta, obj) in Parser(LazyStream(BytesIO(s)), b'BoUnDaRyStRiNg'):
            if _type.strip() == 'file':
                chunks[meta['content-disposition'][1]['name'].decode('utf8')] = '<BINARY_FILE>'
        msg = 'Multipart Binary:\n{}'.format(chunks)
        return msg

    def prettify(self, s):
        if isinstance(s, bytes):
            try:
                s = s.decode('utf8')
            except UnicodeDecodeError:
                if self.dj_request['CONTENT_TYPE'].startswith('multipart/'):
                    return self.prettify_multipart(s)
                raise

        if isinstance(s, str):
            try:
                return json.loads(s)
            except:
                if len(s) < 100:
                    return s
                return '{} ...'.format(s[:100])
        return pformat(s)

    def log(self, resp):
        request = resp.request
        self.dj_request = request
        if 'wsgi.input' in request:
            cnt = request['wsgi.input']._FakePayload__content
            cnt.seek(0)
            payload = self.prettify(cnt.read())
        else:
            payload = None

        rec = {
            'method': request['REQUEST_METHOD'],
            'path': request['PATH_INFO'],
            'query': request['QUERY_STRING'],
            'payload': payload,
            'status_code': resp.status_code,
            'status_text': resp.status_text,
            'response_full': resp.serialize().decode('utf8'),
            'response_headers': resp.serialize_headers().decode('utf8'),
            'response': self.prettify(resp.content),
        }
        self.record(rec)

    def record(self, log_record):
        if self._silent:
            return
        self.records.append(log_record)
        self.verbose_print(log_record)

    def verbose_print(self, log_record):
        if not self.verbose:
            return
        print('\n{method} {path} {query}'.format(**log_record))
        if log_record['payload']:
            print('Payload:\n{payload}'.format(**log_record))
        print('\nResponse Code: {status_code} Content:\n{response}\n'.format(**log_record))

    def finish(self):
        pass

    @contextmanager
    def silent(self):
        self._silent = True
        yield
        self._silent = False


class RequestLogger(RequestVerbose):
    def __init__(self, request, pretty_json=True):
        marker = request.get_closest_marker('docme')
        if not marker or 'path' not in marker.kwargs:
            raise Exception('You should mark test with @pytest.mark.docme(path="PATH")')

        super().__init__(request, pretty_json)

        self.doc_path = marker.kwargs['path']
        self.verbose = request.config.getoption('verbose')

    def finish(self):
        path = os.environ.get('DOCS_ROOT', './.doc')
        if not os.path.exists(path):
            os.mkdir(path)
        fname = os.path.join(path, '{}.{}.json'.format(self.module, self.doc_path))
        with open(fname, 'w') as f:
            json.dump(self.records, f)


class RequestLoggerStub:
    def __call__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self

    @contextmanager
    def silent(self):
        yield


request_logger = RequestLoggerStub()


class UserWrapper:
    """
    Wraps User object, add requests support
    """

    content_format = 'json'  # or multipart

    def __init__(self, user=None):
        from rest_framework.test import APIClient

        self.user = user
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        if self.user:
            self.client.force_login(self.user)

    def __getattr__(self, name):
        if self.user is None:
            raise AttributeError
        else:
            return getattr(self.user, name)

    @contextmanager
    def set_format(self, format):
        old_format = self.content_format
        try:
            self.content_format = format
            yield
        finally:
            self.content_format = old_format

    def _method(self, method, url, data):
        resp = getattr(self.client, method)(url, data, format=self.content_format)
        request_logger.log(resp)
        return resp

    def post(self, url, data):
        return self._method('post', url, data)

    def patch(self, url, data):
        return self._method('patch', url, data)

    def put(self, url, data):
        return self._method('put', url, data)

    def get(self, url, data=None):
        return self._method('get', url, data or {})

    def delete(self, url, data=None):
        return self._method('delete', url, data or {})

    def json_method(self, method, *args, **kwargs):
        with self.set_format('json'):
            return getattr(self, method)(*args, **kwargs)

    def check_code(self, resp, expected):
        if resp.status_code != expected:
            msg = '{} {}'.format(resp.status_code, resp.content)[:1000]
            raise APIError(msg, resp=resp, expected=expected)

    def get_json(self, *args, expected=200, **kwargs):
        r = self.json_method('get', *args, **kwargs)
        self.check_code(r, expected)
        return r.json()

    def get_results(self, *args, **kwargs):
        return self.get_json(*args, **kwargs)['results']

    def post_json(self, *args, expected=201, **kwargs):
        r = self.json_method('post', *args, **kwargs)
        self.check_code(r, expected)
        return r.json()

    def patch_json(self, *args, expected=200, **kwargs):
        r = self.json_method('patch', *args, **kwargs)
        self.check_code(r, expected)
        return r.json()

    def put_json(self, *args, expected=200, **kwargs):
        r = self.json_method('put', *args, **kwargs)
        self.check_code(r, expected)
        return r.json()

    def delete_json(self, *args, expected=204, **kwargs):
        r = self.json_method('delete', *args, **kwargs)
        self.check_code(r, expected)
        assert not r.content, r.content


def create_user(username, groups=(), permissions=(), **kwargs):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Permission, Group
    from django.contrib.contenttypes.models import ContentType

    User = get_user_model()
    exists = User.objects.filter(username=username).first()
    if exists:
        user = exists
    else:
        email = kwargs.pop('email', '%s@gettipsi.com' % username)
        password = kwargs.pop('password', username)
        user = User.objects.create_user(username, email, password, **kwargs)
        for name in groups:
            group = Group.objects.filter(name=name).first()
            if not group:
                group = Group.objects.create(name=name)
            user.groups.add(group)

        for model, codename in permissions:
            content_type = ContentType.objects.get_for_model(model)
            try:
                p = Permission.objects.get(codename=codename, content_type=content_type)
            except Permission.DoesNotExist:
                p = Permission.objects.create(codename=codename, content_type=content_type)
            user.user_permissions.add(p)
        user.refresh_from_db()
    return UserWrapper(user)
