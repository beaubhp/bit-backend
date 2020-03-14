from flask import (Blueprint, request)
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from backend import api, db
from backend.checkpoints.decorators import checkpoint_exists, checkpoint_exists_in_github, valid_checkpoint_form, \
    valid_checkpoint_type
from backend.checkpoints.schemas import checkpoint_schema
from backend.checkpoints.utils import create_checkpoint, edit_checkpoint
from backend.hooks.utils import call_mc_choice_routes
from backend.models import Checkpoint

# Blueprint for checkpoints
checkpoints_bp = Blueprint("checkpoints", __name__)


# Class to Read, Create, and Update
class CheckpointCRUD(Resource):

    # Function to create a checkpoint
    @valid_checkpoint_form
    @valid_checkpoint_type
    def post(self):
        data = request.get_json()
        checkpoint = create_checkpoint(data)

        db.session.add(checkpoint)
        db.session.commit()
        if checkpoint.checkpoint_type == "Multiple Choice" and "mc_choices" in data and "correct_choice" in data:
            call_mc_choice_routes(data["mc_choices"], data["correct_choice"], checkpoint.id)
        db.session.commit()

        return {"message": "Checkpoint successfully created"}, 201

    # Function to edit a checkpoint
    @checkpoint_exists_in_github
    @valid_checkpoint_form
    @valid_checkpoint_type
    def put(self):
        data = request.get_json()
        checkpoint = Checkpoint.query.filter_by(filename=data["filename"]).first()
        edit_checkpoint(checkpoint, data)

        db.session.commit()

        return {"message": "Checkpoint successfully updated"}, 200

    # Function to delete a checkpoint
    @checkpoint_exists_in_github
    def delete(self):
        data = request.get_json()
        checkpoint = Checkpoint.query.filter_by(filename=data["filename"]).first()

        db.session.delete(checkpoint)
        db.session.commit()

        return {"message": "Checkpoint successfully deleted"}, 200


# This class is used to get a specific checkpoint based on id
class CheckpointGetSpecific(Resource):
    method_decorators = [jwt_required, checkpoint_exists]

    # Function to return data on a single checkpoint
    def get(self, checkpoint_id):
        checkpoint = Checkpoint.query.get(checkpoint_id)

        return checkpoint_schema.dump(checkpoint)


# Creates the routes for the classes
api.add_resource(CheckpointCRUD, "/checkpoints")
api.add_resource(CheckpointGetSpecific, "/checkpoints/<int:checkpoint_id>")
