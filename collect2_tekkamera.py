import carla
import random
from time import sleep

def connect_to_carla(host='localhost', port=2000, timeout=10.0, retries=5):
    client = carla.Client(host, port)
    client.set_timeout(timeout)
    for i in range(retries):
        try:
            world = client.load_world('Town02')
            return client, world
        except RuntimeError as e:
            if i == retries - 1:
                raise ConnectionError(f"CARLA server could not be reached after {retries} attempts: {str(e)}")
            print(f"Connection attempt {i+1}/{retries} failed. Retrying...")
            sleep(2)
    return None, None

client, world = connect_to_carla()

bp_lib = world.get_blueprint_library()

def set_all_traffic_lights(world, light):
    traffic_lights = world.get_actors().filter('traffic.traffic_light')
    for tl in traffic_lights:
        tl.set_state(getattr(carla.TrafficLightState, light))
        tl.freeze(True)
set_all_traffic_lights(world, "Yellow")

class VehicleManager:
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.world = world
        self.camera = self.attach_autopilot_and_camera()

    def attach_autopilot_and_camera(self):
        self.vehicle.set_autopilot(True)
        camera_bp = bp_lib.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '800')
        camera_bp.set_attribute('image_size_y', '600')
        camera_bp.set_attribute('fov', '110')
        camera_transform = carla.Transform(carla.Location(x=2.5, z=1.7))
        return world.spawn_actor(camera_bp, camera_transform, attach_to=self.vehicle)

    def record_on_traffic_lights(self):
        def process_image(image):
            nearest_light = self.update_traffic_light()
            if nearest_light and nearest_light.get_location().distance(self.vehicle.get_location()) < 30:
                traffic_light_color = self.vehicle.get_traffic_light_state().name
                color_folder = traffic_light_color
                image.save_to_disk(f'./{color_folder}/{traffic_light_color}_{image.frame}_{self.vehicle.id}.png')
        self.camera.listen(process_image)

    def update_traffic_light(self):
        lights = self.world.get_actors().filter('traffic.traffic_light')
        vehicle_location = self.vehicle.get_location()
        return min(lights, key=lambda light: light.get_location().distance(vehicle_location), default=None)

def spawn_single_vehicle(world, bp_lib, spawn_points):
    vehicle_bp = random.choice(bp_lib.filter('vehicle.*'))
    spawn_point = random.choice(spawn_points)
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
    if vehicle:
        world.tick()
        return vehicle
    return None

spawn_points = world.get_map().get_spawn_points()
vehicle = spawn_single_vehicle(world, bp_lib, spawn_points)

if vehicle:
    manager = VehicleManager(vehicle, world)
    manager.record_on_traffic_lights()
def add_traffic(world, bp_lib, spawn_points, num_vehicles=20):
    vehicle_blueprints = bp_lib.filter('vehicle.*')
    vehicles = []
    for _ in range(num_vehicles):
        blueprint = random.choice(vehicle_blueprints)
        # Aracı rastgele bir spawn noktasında yarat
        spawn_point = random.choice(spawn_points)
        vehicle = world.try_spawn_actor(blueprint, spawn_point)
        if vehicle:
            vehicles.append(vehicle)
            vehicle.set_autopilot(True)  # Otomatik pilotu aktifleştir
            world.tick()
    return vehicles

spawn_points = world.get_map().get_spawn_points()
vehicles = add_traffic(world, bp_lib, spawn_points, 20)  # Örnek olarak 30 araç ekleyelim


def setup_traffic_manager(world, ignore_lights=True, max_speed_kmh=20):
    traffic_manager = client.get_trafficmanager()
    if ignore_lights:
        # Hız limitlerini azaltarak daha güvenli bir sürüş sağlar
        for vehicle in world.get_actors().filter('vehicle.*'):
            traffic_manager.ignore_lights_percentage(vehicle, 100.0)  # Tüm araçlar için trafik ışıklarını yüzde 100 oranında görmezden gel
            speed_difference = ((max_speed_kmh / vehicle.get_speed_limit()) - 1.0) * 100
            traffic_manager.vehicle_percentage_speed_difference(vehicle, speed_difference)

setup_traffic_manager(world, ignore_lights=True)
# Ana döngü
weather_list = [
carla.WeatherParameters.ClearNoon,
    carla.WeatherParameters.CloudyNoon,
    carla.WeatherParameters.WetNoon,
    carla.WeatherParameters.WetCloudyNoon,
    carla.WeatherParameters.MidRainyNoon,
    carla.WeatherParameters.HardRainNoon,
    carla.WeatherParameters.SoftRainNoon,
    carla.WeatherParameters.ClearSunset,
    carla.WeatherParameters.CloudySunset,
    carla.WeatherParameters.WetSunset,
    carla.WeatherParameters.WetCloudySunset,
    carla.WeatherParameters.MidRainSunset,
    carla.WeatherParameters.HardRainSunset,
    carla.WeatherParameters.SoftRainSunset
]

try:
    while True:
        selected_weather = random.choice(weather_list)
        world.set_weather(selected_weather)
        print("Weather changed to:", selected_weather)
        sleep(10)  # Adjust this for your required interval, 120 seconds for 2 minutes
except KeyboardInterrupt:
    print("Weather changing stopped by user.")
