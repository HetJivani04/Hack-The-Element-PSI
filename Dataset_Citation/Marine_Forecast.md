# Open-Meteo Marine API Data Retrieval

## Prerequisites
```bash
pip install openmeteo-requests requests-cache retry-requests numpy pandas
```

## Python Implementation

```python
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://marine-api.open-meteo.com/v1/marine"
params = {
	"latitude": 54.544587,
	"longitude": 10.227487,
	"hourly": ["wave_height", "wave_direction", "wave_period", "wave_peak_period", "wind_wave_height", "wind_wave_direction", "wind_wave_period", "wind_wave_peak_period", "swell_wave_direction", "swell_wave_height", "swell_wave_period", "swell_wave_peak_period", "secondary_swell_wave_height", "secondary_swell_wave_period", "secondary_swell_wave_direction", "tertiary_swell_wave_height", "tertiary_swell_wave_period", "tertiary_swell_wave_direction", "sea_level_height_msl", "sea_surface_temperature", "ocean_current_velocity", "ocean_current_direction"],
	"bounding_box": "43.675818,-64.328234,44.831526,-61.943675",
	"start_date": "2000-01-16",
	"end_date": "2026-05-30",
}
responses = openmeteo.weather_api(url, params = params)

# Process bounding box locations
for response in responses:
	print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
	
	hourly = response.Hourly()
	hourly_wave_height = hourly.Variables(0).ValuesAsNumpy()
	hourly_wave_direction = hourly.Variables(1).ValuesAsNumpy()
	hourly_wave_period = hourly.Variables(2).ValuesAsNumpy()
	hourly_wave_peak_period = hourly.Variables(3).ValuesAsNumpy()
	hourly_wind_wave_height = hourly.Variables(4).ValuesAsNumpy()
	hourly_wind_wave_direction = hourly.Variables(5).ValuesAsNumpy()
	hourly_wind_wave_period = hourly.Variables(6).ValuesAsNumpy()
	hourly_wind_wave_peak_period = hourly.Variables(7).ValuesAsNumpy()
	hourly_swell_wave_direction = hourly.Variables(8).ValuesAsNumpy()
	hourly_swell_wave_height = hourly.Variables(9).ValuesAsNumpy()
	hourly_swell_wave_period = hourly.Variables(10).ValuesAsNumpy()
	hourly_swell_wave_peak_period = hourly.Variables(11).ValuesAsNumpy()
	hourly_secondary_swell_wave_height = hourly.Variables(12).ValuesAsNumpy()
	hourly_secondary_swell_wave_period = hourly.Variables(13).ValuesAsNumpy()
	hourly_secondary_swell_wave_direction = hourly.Variables(14).ValuesAsNumpy()
	hourly_tertiary_swell_wave_height = hourly.Variables(15).ValuesAsNumpy()
	hourly_tertiary_swell_wave_period = hourly.Variables(16).ValuesAsNumpy()
	hourly_tertiary_swell_wave_direction = hourly.Variables(17).ValuesAsNumpy()
	hourly_sea_level_height_msl = hourly.Variables(18).ValuesAsNumpy()
	hourly_sea_surface_temperature = hourly.Variables(19).ValuesAsNumpy()
	hourly_ocean_current_velocity = hourly.Variables(20).ValuesAsNumpy()
	hourly_ocean_current_direction = hourly.Variables(21).ValuesAsNumpy()
	
	hourly_data = {
		"date": pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		)
	}
	
	hourly_data["wave_height"] = hourly_wave_height
	hourly_data["wave_direction"] = hourly_wave_direction
	hourly_data["wave_period"] = hourly_wave_period
	hourly_data["wave_peak_period"] = hourly_wave_peak_period
	hourly_data["wind_wave_height"] = hourly_wind_wave_height
	hourly_data["wind_wave_direction"] = hourly_wind_wave_direction
	hourly_data["wind_wave_period"] = hourly_wind_wave_period
	hourly_data["wind_wave_peak_period"] = hourly_wind_wave_peak_period
	hourly_data["swell_wave_direction"] = hourly_swell_wave_direction
	hourly_data["swell_wave_height"] = hourly_swell_wave_height
	hourly_data["swell_wave_period"] = hourly_swell_wave_period
	hourly_data["swell_wave_peak_period"] = hourly_swell_wave_peak_period
	hourly_data["secondary_swell_wave_height"] = hourly_secondary_swell_wave_height
	hourly_data["secondary_swell_wave_period"] = hourly_secondary_swell_wave_period
	hourly_data["secondary_swell_wave_direction"] = hourly_secondary_swell_wave_direction
	hourly_data["tertiary_swell_wave_height"] = hourly_tertiary_swell_wave_height
	hourly_data["tertiary_swell_wave_period"] = hourly_tertiary_swell_wave_period
	hourly_data["tertiary_swell_wave_direction"] = hourly_tertiary_swell_wave_direction
	hourly_data["sea_level_height_msl"] = hourly_sea_level_height_msl
	hourly_data["sea_surface_temperature"] = hourly_sea_surface_temperature
	hourly_data["ocean_current_velocity"] = hourly_ocean_current_velocity
	hourly_data["ocean_current_direction"] = hourly_ocean_current_direction
	
	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print("\nHourly data\n", hourly_dataframe)
```

## Marine Variables

| Variable | Valid time | Unit | Description |
| :--- | :--- | :--- | :--- |
| `wave_height`, `wind_wave_height`, `swell_wave_height`, `secondary_swell_wave_height`, `tertiary_swell_wave_height` | Instant | Meter | Wave height of significant mean, wind and swell waves. Wave directions are always reported as the direction the waves come from (0° = north to south; 90° = from east). |
| `wave_direction`, `wind_wave_direction`, `swell_wave_direction`, `secondary_swell_wave_direction`, `tertiary_swell_wave_direction` | Instant | ° | Mean direction of mean, wind and swell waves. |
| `wave_period`, `wind_wave_period`, `swell_wave_period`, `secondary_swell_wave_period`, `tertiary_swell_wave_period` | Instant | Seconds | Period between mean, wind and swell waves. |
| `wind_wave_peak_period`, `swell_wave_peak_period` | Instant | Seconds | Peak period between wind and swell waves. |
| `ocean_current_velocity` | Instant | km/h (mph, m/s, knots) | Velocity of ocean current considering Eulerian, Waves and Tides. |
| `ocean_current_direction` | Instant | ° | Direction following the flow of the current (0° = Going north; 90° = Towards east). |
| `sea_surface_temperature` | Instant | Celsius | The sea surface temperature close to the water surface. |
| `sea_level_height_msl` | Instant | metre | The sea level height accounts for ocean tides, the inverted barometer effect, sea surface height, global mean steric variation, and global mean mass volume variation. |
| `invert_barometer_height` | Instant | metre | Invert barometer effect is the height low and high pressure systems effect the sea level height. |


## Citation
Citation & Acknowledgement
Generated using ICON Wave forecast from the German Weather Service DWD.

All users of Open-Meteo data must provide a clear attribution to DWD as well as a reference to Open-Meteo.