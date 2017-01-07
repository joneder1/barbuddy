import unittest
import os
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Python 2 compatibility

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "barbuddy.config.TestingConfig"

from barbuddy import app
from barbuddy import models
from barbuddy.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the posts API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
    def test_get_empty_cocktails(self):
        """ Getting cocktails from an empty database """
        response = self.client.get("/api/cocktails",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data, [])    
        
    def test_get_cocktails(self):
        """ Getting cocktails from a populated database """
        cocktailA = models.Cocktail(cocktailname="Example Cocktail A", description="vodka", location="bar", rating="5")
        cocktailB = models.Cocktail(cocktailname="Example Cocktail B", description="bourbon", location="restaurant", rating="4")

        session.add_all([cocktailA, cocktailB])
        session.commit()
        
        response = self.client.get("/api/cocktails",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 2)

        cocktailA = data[0]
        self.assertEqual(cocktailA["cocktailname"], "Example Cocktail A")
        self.assertEqual(cocktailA["description"], "vodka")
        self.assertEqual(cocktailA["location"], "bar")
        self.assertEqual(cocktailA["rating"], 5)

        cocktailB = data[1]
        self.assertEqual(cocktailB["cocktailname"], "Example Cocktail B")
        self.assertEqual(cocktailB["description"], "bourbon")
        self.assertEqual(cocktailB["location"], "restaurant")
        self.assertEqual
        
    def test_get_cocktails_with_search(self):
        """ Filtering cocktails """
        cocktailA = models.Cocktail(cocktailname="Old Fashioned", description="vodka", location="bar", rating="5")
        cocktailB = models.Cocktail(cocktailname="Sazerac", description="bourbon", location="restaurant", rating="4")

        session.add_all([cocktailA, cocktailB])
        session.commit()

        response = self.client.get("/api/cocktails?cocktailname_like=Old&description_like=vodka",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        cocktails = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(cocktails), 1)
        #should only return 1 cocktail
        cocktail = cocktails[0]
        self.assertEqual(cocktail["cocktailname"], "Old Fashioned")
        self.assertEqual(cocktail["description"], "vodka")
        self.assertEqual(cocktail["location"], "bar")
        self.assertEqual(cocktail["rating"], 5)
        
    def test_cocktail_post(self):
        """ Posting a new cocktail """
        data = {
            "cocktailname": "Old Fashioned",
            "description": "Bourbon and bitters",
            "location": "Blue Hound Lounge",
            "rating": 5
        }

        response = self.client.post("/api/cocktails",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/cocktails/1")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["cocktailname"], "Old Fashioned")
        self.assertEqual(data["description"], "Bourbon and bitters")
        self.assertEqual(data["location"], "Blue Hound Lounge")
        self.assertEqual(data["rating"], 5)

        cocktails = session.query(models.Cocktail).all()
        self.assertEqual(len(cocktails), 1)

        cocktail = cocktails[0]
        self.assertEqual(cocktail.cocktailname, "Old Fashioned")
        self.assertEqual(cocktail.description, "Bourbon and bitters")
        self.assertEqual(cocktail.location, "Blue Hound Lounge")
        self.assertEqual(cocktail.rating, 5)    
        
    def test_cocktail_edit(self):
        """ Editing a cocktail """
        #run test cocktail function to add data
        self.test_cocktail_post()
        #data for the edited post
        data = {
            "cocktailname": "Edit Old Fashioned",
            "description": "Edit Bourbon and bitters",
            "location": "Edit Blue Hound Lounge",
            "rating": 4
        }
        
        response = self.client.put("/api/cocktails/1",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )    
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/cocktails/1")
        
        #Cocktail with id 1 should have matching data    
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["cocktailname"], "Edit Old Fashioned")
        self.assertEqual(data["description"], "Edit Bourbon and bitters")
        self.assertEqual(data["location"], "Edit Blue Hound Lounge")
        self.assertEqual(data["rating"], 4)
        
        #should only return 1 cocktail
        cocktails = session.query(models.Cocktail).all()
        self.assertEqual(len(cocktails), 1)
        
        #cocktail should match info
        cocktail = cocktails[0]
        self.assertEqual(cocktail.cocktailname, "Edit Old Fashioned")
        self.assertEqual(cocktail.description, "Edit Bourbon and bitters")
        self.assertEqual(cocktail.location, "Edit Blue Hound Lounge")
        self.assertEqual(cocktail.rating, 4)    
        
    def test_delete_cocktail(self):
        """ deleting a cocktail """
        cocktailA = models.Cocktail(cocktailname="Example Cocktail A", description="vodka", location="bar", rating="5")
        
        session.add_all([cocktailA])
        session.commit()

        response = self.client.get("/api/cocktails/{}".format(cocktailA.id),
            headers=[("Accept", "application/json")])

        session.delete(cocktailA)
        session.commit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        cocktails = session.query(models.Cocktail).all()
        self.assertEqual(len(cocktails), 0)
        
    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()
