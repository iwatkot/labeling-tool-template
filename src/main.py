import supervisely as sly
from fastapi import Request
from typing import Any, Dict

from supervisely.app.widgets import Container, Switch, Field

process_labels = Switch(switched=True)
process_labels_field = Field(
    title="Process labels",
    description="If turned on, then label will be processed after creating it with bitmap brush tool",
    content=process_labels,
)

layout = Container(widgets=[process_labels_field])

app = sly.Application(layout=layout)

server = app.get_server()


@process_labels.value_changed
def debug(is_switched):
    sly.logger.info(f"Processing is now {is_switched}")


@server.post("/tools_bitmap_brush_figure_changed")
def brush_figure_changed(request: Request):
    sly.logger.info("Bitmap brush figure changed")
    request_state = request.state
    api: sly.Api = request_state.api
    context: Dict[str, Any] = request_state.context

    tool_state = context.get("toolState", {})
    tool_option = tool_state.get("option")

    sly.logger.info(f"Tool state: {tool_state}, tool option: {tool_option}")

    if tool_option != "fill":
        sly.logger.info("Option is not fill, skipping")
        return

    if not process_labels.is_switched():
        sly.logger.info("Processing is not enabled, skipping")
        return

    class_title = context.get("figureClassTitle")
    project_id = context.get("projectId")

    sly.logger.info(f"Class title: {class_title}, project id: {project_id}")

    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    figure_id = context.get("figureId")
    sly_label = api.annotation.get_image_label_by_id(
        figure_id, class_title, project_meta
    )

    sly.logger.info(f"Retrieved sly.Label by id: {figure_id}")

    sly_label = process_label(sly_label)

    sly.logger.info(f"Processed sly.Label with id: {figure_id}")

    api.annotation.update_label(figure_id, sly_label)

    sly.logger.info(f"Updated figure with id: {figure_id}")


def process_label(label: sly.Label) -> sly.Label:
    # Implement your logic here.
    return label.translate(10, 10)
