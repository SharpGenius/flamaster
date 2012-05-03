# -*- coding: utf-8 -*-
import re
import hashlib
import types
import trafaret as t

from datetime import datetime

from trafaret.extras import KeysSubset

from flask import current_app, request, g
from flask.ext.mail import Message
from flask.helpers import json, _assert_have_json

from flamaster.app import mail

from sqlalchemy.orm import class_mapper
from flamaster.app import db

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:;]+')


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.ctime()
        return super(CustomEncoder, self).default(obj)


def jsonify(*args, **kwargs):
    status = 200
    if __debug__:
        _assert_have_json()
    if 'status' in kwargs:
        status = kwargs.pop('status', 200)
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
        indent=None if request.is_xhr else 2, cls=CustomEncoder),
        status=status, mimetype='application/json')


def slugify(date_time, text, delim='-', fallback=''):
    result = []
    for word in _punct_re.split(text.lower()):
        word = unicode(word)
        if word:
            result.append(word)
    slug = unicode(delim.join(result))
    if slug and isinstance(date_time, datetime):
        slug = delim.join((date_time.date().isoformat(), slug))
    else:
        slug = fallback
    print slug
    return slug


def get_hexdigest(salt, raw_password):
    """ Returns a string of the hexdigest of the given plaintext password and salt
        using the sha1 algorithm.
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    return hashlib.sha1(salt + raw_password).hexdigest()


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """ Returns a bytestring version of 's', encoded as specified in
        'encoding'. If strings_only is True, don't convert (some)
        non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def send_email(to, subject, body):
        recipients = isinstance(to, basestring) and [to] or to
        msg = Message(subject=subject, body=body, recipients=recipients)
        current_app.logger.debug(body)
        mail.send(msg)


def validate_password_change(data):

    def cmp_words(dikt):
        response = {'password': dikt['password']}
        if dikt['password_confirm'] != dikt['password']:
            response['password'] = t.DataError("Passwords don't match")
        return response

    valid_dict = t.Dict({KeysSubset('password', 'password_confirm'): cmp_words})
    return valid_dict.check(data)


def check_permission(name):
    return bool(g.user.role.permissions.filter_by(name=name).first())


class CRUDMixin(object):
    """ Basic CRUD mixin
    """

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get(cls, id):
        if id is not None:
            return cls.query.get(id)
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        commit and db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        commit and db.session.commit()

    def as_dict(self):
        """ method for building dictionary for model value-properties filled
            with data from mapped storage backend
        """
        omit_values = ['password']
        return dict((c.name, getattr(self, c.name))
              for c in class_mapper(self.__class__).mapped_table.c
              if c.name not in omit_values)
