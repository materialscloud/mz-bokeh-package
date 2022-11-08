import os
import logging
from typing import List
from bokeh.io import curdoc
from bokeh.models import Widget, Toggle, Button, CustomJS, Column

from .app_state import AppState

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
CONFIRMATION_MODAL_MACROS_PATH = os.path.join(BASE_DIR, "../templates/confirmation_modal")


class ConfirmationModal:
    def __init__(self, title: str, content_widgets: List[Widget], state: AppState):
        """This class creates a confirmation modal.

        In addition to instantiating this class, it's also required to include the
        confirmation modal Jinja macros in the Jinja template that's used to generate the app:
            - Import the macros: Add the line '{% import "confirmation_modal_macros.html" as confirmation_modal with context %}'
                as the first line of the template file.
            - Include modal's css: Add the line '{{ confirmation_modal.include_css() }}'
                to the "preamble" block.
            - Include modal's html: Add the line '{{ confirmation_modal.include_html(confirmation_modal_title, confirmation_modal_widgets) }}'
                to the "contents" block.

        Args:
            title: Modal's title.
            content_widgets: The Bokeh widgets that should be displayed in the
                main area of the modal.
            state: App state object.
        """  # noqa: E501
        self._title = title
        self._state = state
        self._content_widgets = content_widgets
        self._invoker_css_class = "confirmation-modal-invoker"

        # Name content widgets. This is necessary for embedding the widgets
        # in the app's Jinja template.
        for i, widget in enumerate(self._content_widgets):
            widget.name = f"content_widget_{i}"

        # Create a dummy widget to allow invoking the modal from the backend.
        self._modal_invoker = Toggle(visible=False, name="modal_invoker")
        self._modal_invoker.js_on_change("active", self._get_modal_invoker_js_callback())

        # "Apply" button.
        self.apply_modal_btn = Button(
            label="Apply",
            width=75,
            css_classes=["apply-btn"],
            name="apply_btn",
        )
        self.apply_modal_btn.on_click(self._on_apply_modal)

        # "Cancel" button.
        self.cancel_modal_btn = Button(
            label="Cancel",
            width=75,
            css_classes=["cancel-btn"],
            name="cancel_btn",
        )
        self.cancel_modal_btn.on_click(self._on_cancel_modal)

        # Layout the widgets.
        self.layout = Column(
            *(widget for widget in self._content_widgets),
            self._modal_invoker,
            self.apply_modal_btn,
            self.cancel_modal_btn,
        )

        self._configure_jinja_environment()

    def show(self):
        """Displays the modal.

        Toggling the "active" property of the "_modal_invoker" widget triggers a
        JS callback that displays the modal.
        """
        self._modal_invoker.active = not self._modal_invoker.active
        logger.debug("The modal was displayed.")

    def _get_modal_invoker_js_callback(self) -> CustomJS:
        """Returns a javascript callback to run when the modal invoker is triggered.

        Returns:
            CustomJS: "on_click" Javascript callback.
        """
        code = """
        // Add "data" attribute to both the "Apply" and "Cancel" buttons (in the modal) to allow closing the modal.
        $(".apply-btn > .bk-btn-group > .bk-btn").attr("data-dismiss", "modal")
        $(".cancel-btn > .bk-btn-group > .bk-btn").attr("data-dismiss", "modal")

        // Show the modal.
        $('#confirmation-modal').modal('show')
        """
        return CustomJS(code=code)

    def _configure_jinja_environment(self):
        """Configures the Bokeh template's environment.

        These configurations:
            1. Allow the Bokeh template that is used to render the app to import/include the confirmation modal macros
                by adding their path to Jinja's search path.
            2. Add template variables that are necessary for running the confirmation modal macros.
        """
        doc = curdoc()

        # Add the confirmation modal macros directory to the Jinja environment search path.
        # This allows importing/including the confirmation modal macros in the Bokeh app template.
        doc.template.environment.loader.searchpath.append(CONFIRMATION_MODAL_MACROS_PATH)

        # Add template variables. These variables are necessary for generating the confirmation modal HTML.
        doc.template_variables["is_confirmation_modal"] = True
        doc.template_variables["confirmation_modal_title"] = self._title
        doc.template_variables["confirmation_modal_widgets"] = [widget.name for widget in self._content_widgets]

    def _on_apply_modal(self, event):
        """This function runs when the "Apply" button is clicked.
        """
        logger.debug('The "Apply" button was clicked.')
        self._state["confirmation_modal_applied"] += 1

    def _on_cancel_modal(self, event):
        logger.debug('The "Cancel" button was clicked.')
        self._state["confirmation_modal_canceled"] += 1
