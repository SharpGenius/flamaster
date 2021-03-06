from __future__ import absolute_import
import trafaret as t
from flask.ext.security import roles_required

from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource

from . import bp
from .models import FlatPage


@api_resource(bp, 'pages', {'id': None})
class FlatPageResource(ModelResource):

    validation = t.Dict({'name': t.String,
                         'content': t.String}).ignore_extra('*')
    model = FlatPage
    method_decorators = {'post': roles_required('admin'),
                         'put': roles_required('admin'),
                         'delete': roles_required('admin')}
