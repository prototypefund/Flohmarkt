import haversine

from flohmarkt.models.instance_settings import InstanceSettingsSchema

async def is_inside_perimeter(c):
    """
        Returns true if the given lanlng coords are located
        inside this instance's range. False otherwise.
    """
    settings = await InstanceSettingsSchema.retrieve()
    home_coords = (settings["coordinates"]["lat"], settings["coordinates"]["lng"])
    perimeter = settings["perimeter"]
    remote_coords = (c["lat"],c["lng"])
    return haversine.haversine(home_coords, remote_coords) <= perimeter

    
