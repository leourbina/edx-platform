"""
Login page for the LMS.
"""

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
from . import BASE_URL


class LoginPage(PageObject):
    """
    Login page for the LMS.
    """

    url = BASE_URL + "/login"

    def is_browser_on_page(self):
        return any([
            'log in' in title.lower()
            for title in self.q(css='span.title-super').text
        ])


    def wait_for_ajax(self):
        """ Make sure that all ajax requests are finished.
        """
        def _is_ajax_finished():
            """
            Check if all the ajax call on current page completed.
            :return:
            """
            return self.browser.execute_script("return jQuery.active") == 0

        EmptyPromise(_is_ajax_finished, "Finished waiting for ajax requests.").fulfill()


    def login(self, email, password):
        """
        Attempt to log in using `email` and `password`.
        """

        EmptyPromise(self.q(css='input#email').is_present, "Click ready").fulfill()
        EmptyPromise(self.q(css='input#password').is_present, "Click ready").fulfill()

        self.q(css='input#email').fill(email)
        self.q(css='input#password').fill(password)
        self.wait_for_ajax()
        self.q(css='button#submit').click()

        EmptyPromise(
            lambda: "login" not in self.browser.current_url,
            "redirected from the login page"
        )
