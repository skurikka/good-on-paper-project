"""
Translation tests
=================
"""

from typing import List

import pytest
from flask import Flask
from flask_babel import (
    Babel,
    Locale,
    force_locale,
    gettext,
)

from tjts5901.i18n import SupportedLocales


@pytest.fixture
def babel(app: Flask) -> Babel:
    """
    Babel translation fixture.

    Returns babel tranlaslation fixture registered in flask app
    """
    yield app.extensions['babel'].instance


def test_for_supported_locales(app: Flask, babel: Babel):
    """
    Compare supported locales with locales with translations available.
    """
    with app.app_context():
        languages: List[Locale] = babel.list_translations()

        # Using list comprehension to convert Enum to list of Locales
        # required_languages = [Locale.parse(locale.value) for locale in SupportedLocales]
        required_languages: List[Locale] = list()
        for locale in SupportedLocales:
            required_languages.append(Locale.parse(locale.value))

        for required in required_languages:

            # Skip English, as it is the default language of the application.
            if required.language == 'en':
                continue

            assert required in languages, f"Missing translation for language {required.language}"

def test_babel_translations(app: Flask, babel: Babel):
    """
    Test that translations exists for test string "Hello, world!". This test
    will fail if the translation is missing for any language.

    This test is not intended to test the translation itself, but rather to
    ensure that the translation exists.

    And if the actual translation for "Hello, world!" is "Hello, world!", then
    the test needs to be updated to use a different test string.
    """

    # For flask_babel to work, we need to run in app context
    with app.app_context():

        # Iterate through all of the languages available.
        languages: List[Locale] = babel.list_translations()
        for locale in languages:
            if locale.language == "en":
                # By default everything should be in english
                continue

            with force_locale(locale):
                assert gettext("New item") != "New item", f"Message is not translated for language {locale.language}"


def test_app_language_detection(client, babel):
    """
    Similar to :func:`test_babel_translations`, but uses e2e test client
    to test translations.

    Uses the Accept-Language header to set the language for the request.

    TODO: Write variation that includes the territory code in the Accept-Language header.
    """

    # Iterate through all of the languages available.
    with client.application.app_context():
        languages: List[Locale] = babel.list_translations()

    for locale in languages:
        if locale.language == "en":
            # By default everything should be in english
            continue

        response = client.get('/', headers={'Accept-Language': locale.language})
        resp_as_string = response.data.decode('utf-8')
        assert gettext("Myy") != resp_as_string, f"Message is not translated for language {locale.language}"

