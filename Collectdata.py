import carla
import numpy as np
import random
from datetime import time
import random


def connect_to_carla(host='localhost', port=2000, timeout=10.0, retries=5):
    client = carla.Client(host, port)
    client.set_timeout(timeout)
    for i in range(retries):
        try:
            world = client.get_world()
            return client, world
        except RuntimeError as e:
            if i == retries - 1:
                raise ConnectionError(f"CARLA server could not be reached after {retries} attempts: {str(e)}")
            print(f"Connection attempt {i+1}/{retries} failed. Retrying...")
            time.sleep(2)  # 2 saniye bekleyerek tekrar deneyin
    return None, None

# CARLA'ya bağlan
client, world = connect_to_carla()

bp_lib=world.get_blueprint_library()

actor_list=[]

world = client.load_world('Town02')
list_actor = world.get_actors()
for actor in list_actor:
    if isinstance(actor, carla.TrafficLight):
        actor.set_red_time(0.2)



def spawn_vehicles(num_vehicles, world, bp_lib, spawn_points):
    vehicles = []
    for _ in range(num_vehicles):
        vehicle_bp = bp_lib.filter('model3')[0]
        spawn_point = random.choice(spawn_points)
        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        if vehicle is not None:
            vehicles.append(vehicle)
            world.tick()  # Araç başarılı bir şekilde dünya içine spawn edildikten sonra dünyayı güncelleyin
    return vehicles


def attach_autopilot_and_camera(vehicle, world):
    # Autopilot
    vehicle.set_autopilot(True)
    
    # Camera
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '110')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))  # Kamera için transform ayarları
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
    return camera

def update_traffic_light(self):
    # Aracın bulunduğu yere en yakın trafik ışığını bul
    lights = self.world.get_actors().filter('traffic.traffic_light')
    vehicle_location = self.vehicle.get_location()
    nearest_light = min(
        lights, 
        key=lambda light: light.get_location().distance(vehicle_location),
        default=None
    )
    return nearest_light

def record_on_traffic_lights(self, camera):
    def process_image(image):
        # Her 40 frame'de bir en yakın trafik ışığını güncelle
        if image.frame % 40 == 0:
            nearest_light = self.update_traffic_light()
            if nearest_light and self.vehicle.is_at_traffic_light() and nearest_light.get_location().distance(self.vehicle.get_location()) < 40:
                traffic_light_color = self.vehicle.get_traffic_light_state()
                image.save_to_disk(f'{traffic_light_color}_{image.frame}.png')
    
    camera.listen(process_image)

# CARLA dünyası ve diğer gerekli ayarlar yüklendi varsayılır
spawn_points = world.get_map().get_spawn_points()
vehicles = spawn_vehicles(5, world, bp_lib, spawn_points)
for vehicle in vehicles:
    camera = attach_autopilot_and_camera(vehicle, world)
    record_on_traffic_lights(camera)

def setup_traffic_manager(client, ignore_lights=True):
    traffic_manager = client.get_trafficmanager()
    if ignore_lights:
        traffic_manager.set_global_distance_to_leading_vehicle(2.0)
        traffic_manager.global_percentage_speed_difference(-30.0)  # Hız limitlerini azaltarak daha güvenli bir sürüş sağlar
        for vehicle in client.get_world().get_actors().filter('vehicle.*'):
            traffic_manager.ignore_lights_percentage(vehicle.id, 100)  # Tüm araçlar için trafik ışıklarını görmezden gelme

from time import sleep
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
        # Rastgele bir hava koşulu seç
        selected_weather = random.choice(weather_list)
        
        # Hava koşullarını değiştir
        world.set_weather(selected_weather)
        print("Weather changed to:", selected_weather)

        # 2 dakika bekleme
        sleep(2)

except KeyboardInterrupt:
    print("Weather changing stopped by user.")