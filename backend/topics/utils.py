from backend.models import Topic
from backend.PrereqAssociationObjects.utils import create_topic_badge_loop, edit_topic_badge_prereqs


# Function to create a topic
def create_topic(form_data):
    topic = Topic(name=form_data["name"],
                  description=form_data["description"]
                  )
    create_topic_badge_loop(topic, form_data["badge_prereqs"])

    return topic


# Function to edit a topic
def edit_topic(topic, form_data):
    topic.name = form_data["name"]
    topic.description = form_data["description"]
    edit_topic_badge_prereqs(topic, form_data["badge_prereqs"])

    return