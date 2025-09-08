import folium
from skyfield.api import EarthSatellite, load
from datetime import datetime
import time
import os
import webbrowser
from typing import Optional, Tuple

class SatelliteTracker:
    def __init__(self, tle_line1: str, tle_line2: str, satellite_name: str = "Satellite"):
        self.TLE_LINE1 = tle_line1
        self.TLE_LINE2 = tle_line2
        self.SATELLITE_NAME = satellite_name
        self.HISTORY_FILE = "satellite_positions_history.csv"
        self.MAP_FILE = "satellite_tracking_map.html"
        self.positions_history = []
        
        self.ts = load.timescale()
        self.eph = load('de421.bsp') 
        
        self.satellite = EarthSatellite(tle_line1, tle_line2, satellite_name, self.ts)
        
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, 'w') as f:
                f.write("timestamp,latitude,longitude,altitude\n")

    def get_satellite_position(self) -> Optional[Tuple[float, float, float]]:
        """Получаем текущие координаты спутника из TLE"""
        try:
            t = self.ts.now()
            geocentric = self.satellite.at(t)
            
            subpoint = geocentric.subpoint()
            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees
            alt = subpoint.elevation.km  
            
            return (lat, lon, alt)
            
        except Exception as e:
            print(f"Ошибка при расчете позиции: {e}")
            return None

    def save_position_to_history(self, lat: float, lon: float, alt: float) -> None:
        """Сохраняем позицию в историю"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.HISTORY_FILE, 'a') as f:
            f.write(f"{timestamp},{lat},{lon},{alt}\n")
        
        self.positions_history.append((timestamp, lat, lon, alt))
        if len(self.positions_history) > 100:
            self.positions_history.pop(0)

    def create_map(self, lat: float, lon: float) -> folium.Map:
        """Создаем интерактивную карту с треком спутника"""
        m = folium.Map(location=[lat, lon], zoom_start=3)
        
        # Добавляем маркер текущей позиции
        folium.Marker(
            [lat, lon],
            popup=f"Спутник {self.SATELLITE_NAME}",
            icon=folium.Icon(color='red', icon='satellite')
        ).add_to(m)
        
        # Добавляем трек из истории (если есть)
        if len(self.positions_history) > 1:
            track = [[p[1], p[2]] for p in self.positions_history]
            folium.PolyLine(
                track,
                color='blue',
                weight=2.5,
                opacity=1,
                popup="Трек спутника"
            ).add_to(m)

        folium.TileLayer(
            tiles='https://map1.vis.earthdata.nasa.gov/wmts-webmerc/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg',
            attr='NASA Blue Marble',
            name='NASA Blue Marble',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.LayerControl().add_to(m)
        
        return m

    def track_satellite(self, update_interval: int = 10) -> None:
        """Основная функция отслеживания"""
        print(f"Начинаем отслеживание спутника {self.SATELLITE_NAME}")
        print(f"Карта будет сохраняться в файл: {self.MAP_FILE}")
        print(f"История позиций записывается в: {self.HISTORY_FILE}")
        print("Нажмите Ctrl+C для остановки...")
        
        try:
            while True:
                position = self.get_satellite_position()
                
                if position:
                    lat, lon, alt = position
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"[{timestamp}] Спутник: широта={lat:.4f}, долгота={lon:.4f}, высота={alt:.1f} км")
                    
                    self.save_position_to_history(lat, lon, alt)

                    map_obj = self.create_map(lat, lon)
                    map_obj.save(self.MAP_FILE)
                    
                    if len(self.positions_history) == 1:
                        webbrowser.open(f'file://{os.path.abspath(self.MAP_FILE)}')
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\nОтслеживание остановлено.")

if __name__ == "__main__":
    # Пример 
    TLE_LINE1 = "1 64750U 25144AC  25192.25002315 -.01375670  00000-0 -59479-2 0  9992"
    TLE_LINE2 = "2 64750  53.1535 228.7163 0000829  90.1939 125.2795 15.86986143  2650"
    
    tracker = SatelliteTracker(TLE_LINE1, TLE_LINE2, "ISS STARLINK-34531")
    tracker.track_satellite(update_interval=300)  # Обновление каждые 300 секунд
