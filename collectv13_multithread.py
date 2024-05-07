import threading
import carla
import  random
from time import sleep

def connect_to_carla(host='localhost', port=2000, timeout=10.0, retries=5):
    client = carla.Client(host, port)
    client.set_timeout(timeout)
    for i in range(retries):
        try:
            world = client.load_world('Town02')  # Loading the world directly here
            return client, world
        except RuntimeError as e:
            if i == retries - 1:
                raise ConnectionError(f"CARLA server could not be reached after {retries} attempts: {str(e)}")
            print(f"Connection attempt {i+1}/{retries} failed. Retrying...")
            sleep(2)  # Retry after 2 seconds
    return None, None

client, world = connect_to_carla()

bp_lib = world.get_blueprint_library()
list_actor = world.get_actors()

def set_all_traffic_lights(world, light):
    # Trafik ışıklarının tümünü al
    traffic_lights = world.get_actors().filter('traffic.traffic_light')
    # Her bir trafik ışığını kırmızı yap
    for tl in traffic_lights:
        # Trafik ışığını kırmızıya ayarla
        if light == "Red":
            tl.set_state(carla.TrafficLightState.Red)
        elif light == "Yellow":
            tl.set_state(carla.TrafficLightState.Yellow)
        elif light == "Green":
            tl.set_state(carla.TrafficLightState.Green)
        # Trafik ışığının durumunun değişmemesi için dondur
        tl.freeze(True)
set_all_traffic_lights(world, "Yellow")


class VehicleManager:
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.world = world
        self.camera = None

    def start(self):
        self.camera = attach_autopilot_and_camera(self.vehicle, self.world)
        self.record_on_traffic_lights(self.camera)

    def record_on_traffic_lights(self, camera):
        def process_image(image):
            if image.frame % 60 == 0:
                nearest_light = self.update_traffic_light()
                if nearest_light and nearest_light.get_location().distance(self.vehicle.get_location()) < 30:
                    traffic_light_color = self.vehicle.get_traffic_light_state()
                    color_folder = 'Yellow'  # Assuming all lights are yellow
                    image.save_to_disk(f'./{color_folder}/{traffic_light_color}_{image.frame}_{self.vehicle.id}.png')
        camera.listen(process_image)

    def update_traffic_light(self):
        lights = self.world.get_actors().filter('traffic.traffic_light')
        vehicle_location = self.vehicle.get_location()
        nearest_light = min(lights, key=lambda light: light.get_location().distance(vehicle_location), default=None)
        return nearest_light
    
def attach_autopilot_and_camera(vehicle, world):
    vehicle.set_autopilot(True)
    camera_bp = bp_lib.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '110')
    camera_transform = carla.Transform(carla.Location(x=2.5, z=1.7))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
    return camera

def spawn_vehicles(num_vehicles, world, bp_lib, spawn_points):
    vehicles = []
    sensors = []
    vehicle_blueprints = bp_lib.filter('vehicle.*')
    for _ in range(num_vehicles):
        vehicle_bp = random.choice(vehicle_blueprints)
        spawn_point = random.choice(spawn_points)
        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        if vehicle:
            vehicles.append(vehicle)
            camera = attach_autopilot_and_camera(vehicle, world)
            sensors.append(camera)
            world.tick()
    return vehicles, sensors

spawn_points = world.get_map().get_spawn_points()
vehicles, sensors = spawn_vehicles(10, world, bp_lib, spawn_points)
managers = [VehicleManager(vehicle, world) for vehicle in vehicles]
def start_vehicle_manager(manager):
    manager.start()

# Araç yöneticileri için iş parçacıkları oluşturma
threads = []
for manager in managers:
    t = threading.Thread(target=start_vehicle_manager, args=(manager,))
    threads.append(t)
    t.start()

# Tüm iş parçacıklarının tamamlanmasını bekle
for t in threads:
    t.join()

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
