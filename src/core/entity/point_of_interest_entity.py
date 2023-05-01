"""
This point of interest entity
"""

class PointOfInterestEntity:
    """
    This is a class for defined point of interest

    Parameters:
        latitude (float): the latitude
        longitude (float): the longitude
        name (string): the name
    """

    def __init__(self, latitude, longitude, name):
        self.location = {
            "type": "Point",
            "coordinates": [
                latitude,
                longitude
            ]
        }
        self.name = name

    def __str__(self):
        return self.__class__.__name__
    
    def getDict(self):
        return {
            "name": self.name,
            "location": self.location
        }
