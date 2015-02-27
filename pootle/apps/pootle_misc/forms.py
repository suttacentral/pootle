#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL2
# license. See the LICENSE file for a copy of the license and the AUTHORS file
# for copyright and authorship information.

from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


class GroupedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, querysets, *args, **kwargs):
        super(GroupedModelChoiceField, self).__init__(*args, **kwargs)
        self.querysets = querysets

    def _get_choices(self):
        orig_queryset = self.queryset
        orig_empty_label = self.empty_label
        if self.empty_label is not None:
            yield (u"", self.empty_label)
            self.empty_label = None

        for title, queryset in self.querysets:
            self.queryset = queryset
            if title is None:
                for choice in super(GroupedModelChoiceField, self).choices:
                    yield choice
            else:
                yield (title, [choice for choice in
                               super(GroupedModelChoiceField, self).choices])

        self.queryset = orig_queryset
        self.empty_label = orig_empty_label
    choices = property(_get_choices, forms.ModelChoiceField._set_choices)


class LiberalModelChoiceField(forms.ModelChoiceField):
    """ModelChoiceField that doesn't complain about choices not present in the
    queryset.

    This is essentially a hack for admin pages. to be able to exclude currently
    used choices from dropdowns without failing validation.
    """

    def clean(self, value):
        if value in EMPTY_VALUES:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.model.objects.get(**{key: value})
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_choice'])
        return value


def make_search_form(*args, **kwargs):
    """Factory that instantiates one of the search forms below."""
    terminology = kwargs.pop('terminology', False)
    request = kwargs.pop('request', None)

    if request is not None:
        env = terminology and "terminology" or "editor"
        sparams_cookie = request.COOKIES.get("search-%s" % env)

        if sparams_cookie:
            import json
            import urllib

            initial_sparams = json.loads(urllib.unquote(sparams_cookie))
            if isinstance(initial_sparams, dict):
                if 'sfields' in initial_sparams:
                    kwargs.update({
                        'initial': initial_sparams,
                    })

    if terminology:
        return TermSearchForm(*args, **kwargs)

    return SearchForm(*args, **kwargs)


class SearchForm(forms.Form):
    """Normal search form for translation projects."""
    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'size': '15',
            'title': _("Search (Ctrl+Shift+S)<br/>Type and press Enter to "
                       "search"),
        }),
    )
    soptions = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(
            ('exact', _('Exact Match')),
        ),
    )
    sfields = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(
            ('source', _('Source Text')),
            ('target', _('Target Text')),
            ('notes', _('Comments')),
            ('locations', _('Locations'))
        ),
        initial=['source', 'target'],
    )


class TermSearchForm(SearchForm):
    """Search form for terminology projects and pootle-terminology files."""
    # Mostly the same as SearchForm, but defining it this way seemed easiest.
    sfields = forms.ChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(
            ('source', _('Source Terms')),
            ('target', _('Target Terms')),
            ('notes', _('Definitions')),
        ),
        initial=['source', 'target'],
    )
