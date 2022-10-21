import os
import logging
from typing import List

from bokeh.io import curdoc
from bokeh.models import Widget, Toggle, Button, CustomJS, Column

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
CONFIRMATION_MODAL_MACROS_PATH = os.path.join(BASE_DIR, "../templates/confirmation_modal")


class ConfirmationModal:
    def __init__(self, title: str, invoking_widget: Widget, content_widgets: List[Widget]):
        """This class creates a confirmation modal.

        In addition to instantiating this class, it's also required to include the
        confirmation modal Jinja macros in the Jinja template that's used to generate the app.
        Currently, the modal can only be invoked by a Button Bokeh widget.

        Args:
            title (str): Modal's title.
            invoking_widget (Widget): The Bokeh widget that invokes this modal.
            content_widgets (List[Widget]): The Bokeh widgets that should be displayed in the
                main area of the modal.
        """
        self._title = title
        self._invoking_widget = invoking_widget
        self._content_widgets = content_widgets
        self._invoker_css_class = "confirmation-modal-invoker"

        # Add a class name to the modal invoker.
        self._invoking_widget.css_classes += [self._invoker_css_class]

        # Set a Javascript callback to allow:
        #   - Invoking the modal
        #   - Dismissing the modal when clicking apply/cancel
        #   - Run a backend callback on modal invocation
        self._invoking_widget.js_on_click(self._get_js_callback)

        # Create a dummy widget to allow invoking a backend callback (python)
        # from the frontend (javascript).
        self._backend_callback_invoker = Toggle()
        self._backend_callback_invoker.on_change("active", self._on_modal_invocation)

        # "Apply" button.
        self._apply_modal_btn = Button(
            label="Apply",
            width=75,
            css_classes=["apply-btn"],
            name="apply_btn",
        )
        self._apply_modal_btn.on_click(self._on_apply_modal)

        # "Cancel" button.
        self._cancel_modal_btn = Button(
            label="Cancel",
            width=75,
            css_classes=["cancel-btn"],
            name="cancel_btn",
        )
        self._cancel_modal_btn.on_click(self._on_cancel_modal)

        # Layout the widgets.
        self.layout = Column(
            *(widget for widget in self._content_widgets),
            self._apply_modal_btn,
            self._cancel_modal_btn,
        )

        self._configure_jinja_environment()

    def _get_js_callback(self) -> CustomJS:
        """Returns a javascript callback to run when a button is clicked.

        Returns:
            CustomJS: "on_click" Javascript callback.
        """

        args = {"backend_callback_invoker": self._backend_callback_invoker}
        code = f"""
        // Add "data" attributes to the modal invoker to allow toggling the modal.
        $(".{self._invoker_css_class}")
            .attr("data-toggle", "modal")
            .attr("data-target", "#confirmation-modal")

        // Add "data" attribute to both the "Apply" and "Cancel" buttons (in the modal) to allow closing the modal.
        $(".apply-btn > .bk-btn-group > .bk-btn").attr("data-dismiss", "modal")
        $(".cancel-btn > .bk-btn-group > .bk-btn").attr("data-dismiss", "modal")

        // Invoke backend callback
        backend_callback_invoker.active = !backend_callback_invoker.active
        """
        return CustomJS(args=args, code=code)

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
        doc.template_variables["confirmation_modal_title"] = self._title
        doc.template_variables["confirmation_modal_widgets"] = [widget.name for widget in self._content_widgets]

    def _on_apply_modal(self):
        """This function runs when the "Apply" button is clicked.
        """
        logger.info('The "Apply" button was clicked.')

    def _on_cancel_modal(self):
        logger.info('The "Cancel" button was clicked.')

    def _on_modal_invocation(self):
        logger.info('The modal was invoked.')
