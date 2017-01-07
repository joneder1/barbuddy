import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from barbuddy import app
from .database import session

# JSON Schema describing the structure of a cocktail
cocktail_schema = {
    "properties": {
        "cocktailname" : {"type" : "string"},
        "description" : {"type" : "string"},
        "location" : {"type" : "string"},
        "rating" : {"type" : "integer"}
    },
    "required": ["cocktailname", "description", "location", "rating"]
}

@app.route("/api/cocktails", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def cocktails_post():
    """ Add a new cocktail """
    data = request.json

    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, cocktail_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Add the cocktail to the database
    cocktail = models.Cocktail(cocktailname=data["cocktailname"], description=data["description"], location=data["location"], rating=data["rating"])
    session.add(cocktail)
    session.commit()

    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(cocktail.as_dictionary())
    headers = {"Location": url_for("cocktail_get", id=cocktail.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")

@app.route("/api/cocktails/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def cocktail_get(id):
    """ Single cocktail endpoint """
    # Get the post from the database
    cocktail = session.query(models.Cocktail).get(id)

    # Check whether the cocktail exists
    # If not return a 404 with a helpful message
    if not cocktail:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Return the post as JSON
    data = json.dumps(cocktail.as_dictionary())
    return Response(data, 200, mimetype="application/json")    

@app.route("/api/cocktails", methods=["GET"])
@decorators.accept("application/json")
def posts_get():
    """ Get a list of cocktails """
    # Get the querystring arguments for title and body
    cocktailname_like = request.args.get("cocktailname_like")
    description_like = request.args.get("description_like")
    
    # Get and filter the cocktails from the database
    cocktails = session.query(models.Cocktail)
    if cocktailname_like:
        cocktails = cocktails.filter(models.Cocktail.cocktailname.contains(cocktailname_like))
    if description_like:
        cocktails = cocktails.filter(models.Cocktail.description.contains(description_like))
    cocktails = cocktails.order_by(models.Cocktail.id)

    # Convert the cocktails to JSON and return a response
    data = json.dumps([cocktail.as_dictionary() for cocktail in cocktails])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/cocktails/<id>", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def cocktail_edit(id):
    """ Edit cocktail """
    data = request.json
    
    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, cocktail_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
        
    # edit post for specified id # by retrieving id
    cocktail = session.query(models.Cocktail).get(id)
    cocktail.cocktailname = data["cocktailname"]
    cocktail.description = data["description"]
    cocktail.location = data["location"]
    cocktail.rating = data["rating"]
    session.commit()

    data = json.dumps(cocktail.as_dictionary())
    headers = {"Location": url_for("cocktail_get", id=cocktail.id)}
    return Response(data, 200, headers=headers,
                    mimetype="application/json")           

    
@app.route("/api/cocktails/<int:id>", methods=["DELETE"])
@decorators.accept("application/json")
def cocktail_delete(id):
    """ Delete a single cocktail """
    cocktail = session.query(models.Cocktail).get(id)
    if not cocktail:
        message = "Could not find cocktail with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    session.delete(cocktail)
    session.commit()
    
    message = "Cocktail {} has been deleted".format(id)
    data = json.dumps({"message": message})
    return Response(data, 200, mimetype="application/json")

