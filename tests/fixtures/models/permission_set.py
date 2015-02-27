#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL2
# license. See the LICENSE file for a copy of the license and the AUTHORS file
# for copyright and authorship information.

import pytest


def _require_permission_set(user, directory, positive_permissions=None,
                            negative_permissions=None):
    """Helper to get/create a new PermissionSet."""
    from pootle_app.models.permissions import PermissionSet

    criteria = {
        'user': user,
        'directory': directory,
    }
    permission_set, created = PermissionSet.objects.get_or_create(**criteria)
    if positive_permissions is not None:
        permission_set.positive_permissions = positive_permissions
    if negative_permissions is not None:
        permission_set.negative_permissions = negative_permissions

    permission_set.save()

    return permission_set


@pytest.fixture
def nobody_ps(nobody, root, view, suggest):
    """Require permission sets at the root for the `nobody` user."""
    return _require_permission_set(nobody, root, [view, suggest])


@pytest.fixture
def default_ps(default, root, view, suggest, translate):
    """Require permission sets at the root for the `default` user."""
    return _require_permission_set(default, root, [view, suggest, translate])
