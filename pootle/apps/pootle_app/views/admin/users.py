#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL2
# license. See the LICENSE file for a copy of the license and the AUTHORS file
# for copyright and authorship information.

__all__ = ('UserAdminView', 'UserAPIView')

from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from pootle.core.views import APIView, SuperuserRequiredMixin
from pootle_app.forms import UserForm


class UserAdminView(SuperuserRequiredMixin, TemplateView):
    template_name = 'admin/users.html'


class UserAPIView(SuperuserRequiredMixin, APIView):
    model = get_user_model()
    base_queryset = get_user_model().objects.hide_permission_users() \
                                            .order_by('-id')
    add_form_class = UserForm
    edit_form_class = UserForm
    page_size = 10
    search_fields = ('username', 'full_name', 'email')
