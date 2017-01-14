import json

from flask import request, Response, url_for, jsonify, session, flash, redirect, abort
#from flask.ext.login import login_user, login_required, logout_user
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from barbuddy import app
from .database import session
from getpass import getpass

from werkzeug.security import generate_password_hash

@app.route("/api/signup", methods=["GET"])
@decorators.accept("application/json")
def signup():
    #where should this be going?
    return render_template("signup.html")
    
@app.route("/api/signup", methods = ['POST'])
@decorators.accept("application/json")
@decorators.require("application/json")
def register():
    data = request.json
    user = models.User(username=data["username"], email=data["email"], password=data["password"], userdescription=["userdescription"])
    if models.User.username is None or models.User.password is None:
        abort(400) # missing arguments
    if session.query(models.User).filter_by(username = models.User.username).first() is not None:
        abort(400) # existing user
    user.hash_password(models.User.password)
    session.add(user)
    session.commit()
    #when user registers, I want it to return User with location for all of User's cocktails, but there will be none if new User
    return jsonify({ "username": user.username }), 201, {"Location": url_for("get_cocktails", id = user.id, _external = True)}

@app.route("/api/login", methods=["GET"])
@decorators.accept("application/json")
def login_get():
    #where should this be going?
    return render_template("login.html")
    
@app.route("/api/login", methods=['POST'])
@decorators.accept("application/json")
@decorators.require("application/json")
def login_post():
    data = request.json
    user = models.User(username=data["username"], password=data["password"])
    user = session.query(models.User.username).filter_by(email=models.User.email).first()
    if models.User.username is None or models.User.password is None:
        abort(400) # missing arguments
    if not models.User.username or not check_password_hash(models.User.password, data["password"]):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    else:
        status = False
    #when user is added, I want it to return User with location for all of User's cocktails matching on User id and Cocktail Id
    return jsonify({ "username": user.username }), 201, {"Location": url_for("get_cocktails", id = models.Cocktail.id, _external = True)}
    
@app.route("/api/logout", methods=["GET"])
@decorators.accept("application/json")
def logout_get():
    logout_user()
    return redirect(url_for ("login_get"))
    
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
def cocktails_get():
    """ Get a list of cocktails """
    # Get the querystring arguments for cocktail name and description
    cocktailname_like = request.args.get("cocktailname_like")
    description_like = request.args.get("description_like")
    location_like = request.args.get("location_like")
    rating_like = request.args.get("rating_like")
    
    # Get and filter the cocktails from the database
    cocktails = session.query(models.Cocktail)
    if cocktailname_like:
        cocktails = cocktails.filter(models.Cocktail.cocktailname.contains(cocktailname_like))
    if description_like:
        cocktails = cocktails.filter(models.Cocktail.description.contains(description_like))
    if location_like:
        cocktails = cocktails.filter(models.Cocktail.location.contains(location_like))
    #if rating_like:
        #cocktails = cocktails.filter(models.Cocktail.rating.contains(rating_like))
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
