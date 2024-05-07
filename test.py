import carla

client = carla.Client("localhost", 2000)
client.set_timeout(3.0)

def list_available_maps(client):
    print(client.get_available_maps())

