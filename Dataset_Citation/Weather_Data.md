# Open-Meteo API Data Retrieval

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
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"start_date": "2000-01-01",
	"end_date": "2026-05-21",
	"hourly": ["temperature_2m", "dew_point_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "snowfall", "snow_depth", "weather_code", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "et0_fao_evapotranspiration", "vapour_pressure_deficit", "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m", "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_100_to_255cm", "soil_moisture_28_to_100cm"],
	"bounding_box": "43.675818,-64.328234,44.831526,-61.943675",
}
responses = openmeteo.weather_api(url, params = params)

# Process bounding box locations
for response in responses:
	print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
	
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_dew_point_2m = hourly.Variables(1).ValuesAsNumpy()
	hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()
	hourly_apparent_temperature = hourly.Variables(3).ValuesAsNumpy()
	hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
	hourly_rain = hourly.Variables(5).ValuesAsNumpy()
	hourly_snowfall = hourly.Variables(6).ValuesAsNumpy()
	hourly_snow_depth = hourly.Variables(7).ValuesAsNumpy()
	hourly_weather_code = hourly.Variables(8).ValuesAsNumpy()
	hourly_pressure_msl = hourly.Variables(9).ValuesAsNumpy()
	hourly_surface_pressure = hourly.Variables(10).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(11).ValuesAsNumpy()
	hourly_cloud_cover_low = hourly.Variables(12).ValuesAsNumpy()
	hourly_cloud_cover_mid = hourly.Variables(13).ValuesAsNumpy()
	hourly_cloud_cover_high = hourly.Variables(14).ValuesAsNumpy()
	hourly_et0_fao_evapotranspiration = hourly.Variables(15).ValuesAsNumpy()
	hourly_vapour_pressure_deficit = hourly.Variables(16).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(17).ValuesAsNumpy()
	hourly_wind_speed_100m = hourly.Variables(18).ValuesAsNumpy()
	hourly_wind_direction_10m = hourly.Variables(19).ValuesAsNumpy()
	hourly_wind_direction_100m = hourly.Variables(20).ValuesAsNumpy()
	hourly_wind_gusts_10m = hourly.Variables(21).ValuesAsNumpy()
	hourly_soil_temperature_0_to_7cm = hourly.Variables(22).ValuesAsNumpy()
	hourly_soil_temperature_7_to_28cm = hourly.Variables(23).ValuesAsNumpy()
	hourly_soil_temperature_28_to_100cm = hourly.Variables(24).ValuesAsNumpy()
	hourly_soil_temperature_100_to_255cm = hourly.Variables(25).ValuesAsNumpy()
	hourly_soil_moisture_0_to_7cm = hourly.Variables(26).ValuesAsNumpy()
	hourly_soil_moisture_7_to_28cm = hourly.Variables(27).ValuesAsNumpy()
	hourly_soil_moisture_100_to_255cm = hourly.Variables(28).ValuesAsNumpy()
	hourly_soil_moisture_28_to_100cm = hourly.Variables(29).ValuesAsNumpy()
	
	hourly_data = {
		"date": pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		)
	}
	
	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["dew_point_2m"] = hourly_dew_point_2m
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["apparent_temperature"] = hourly_apparent_temperature
	hourly_data["precipitation"] = hourly_precipitation
	hourly_data["rain"] = hourly_rain
	hourly_data["snowfall"] = hourly_snowfall
	hourly_data["snow_depth"] = hourly_snow_depth
	hourly_data["weather_code"] = hourly_weather_code
	hourly_data["pressure_msl"] = hourly_pressure_msl
	hourly_data["surface_pressure"] = hourly_surface_pressure
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
	hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
	hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
	hourly_data["et0_fao_evapotranspiration"] = hourly_et0_fao_evapotranspiration
	hourly_data["vapour_pressure_deficit"] = hourly_vapour_pressure_deficit
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
	hourly_data["wind_speed_100m"] = hourly_wind_speed_100m
	hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
	hourly_data["wind_direction_100m"] = hourly_wind_direction_100m
	hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
	hourly_data["soil_temperature_0_to_7cm"] = hourly_soil_temperature_0_to_7cm
	hourly_data["soil_temperature_7_to_28cm"] = hourly_soil_temperature_7_to_28cm
	hourly_data["soil_temperature_28_to_100cm"] = hourly_soil_temperature_28_to_100cm
	hourly_data["soil_temperature_100_to_255cm"] = hourly_soil_temperature_100_to_255cm
	hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
	hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm
	hourly_data["soil_moisture_100_to_255cm"] = hourly_soil_moisture_100_to_255cm
	hourly_data["soil_moisture_28_to_100cm"] = hourly_soil_moisture_28_to_100cm
	
	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print("\nHourly data\n", hourly_dataframe)
```

## Hourly Variables

| Variable | Valid time | Unit | Description |
| :--- | :--- | :--- | :--- |
| `temperature_2m` | Instant | °C (°F) | Air temperature at 2m above ground |
| `relative_humidity_2m` | Instant | % | Relative humidity at 2m above ground |
| `dew_point_2m` | Instant | °C (°F) | Dew point temperature at 2m above ground |
| `apparent_temperature` | Instant | °C (°F) | Perceived feels-like temperature |
| `pressure_msl`, `surface_pressure` | Instant | hPa | Atmospheric pressure at mean sea level (msl) or surface |
| `precipitation` | Preceding hour sum | mm (inch) | Total precipitation (rain, showers, snow) |
| `rain` | Preceding hour sum | mm (inch) | Liquid precipitation |
| `snowfall` | Preceding hour sum | cm (inch) | Snowfall amount |
| `cloud_cover` | Instant | % | Total cloud cover area fraction |
| `cloud_cover_low` | Instant | % | Low level clouds and fog (up to 2km) |
| `cloud_cover_mid` | Instant | % | Mid level clouds (2 to 6km) |
| `cloud_cover_high` | Instant | % | High level clouds (from 6km) |
| `shortwave_radiation` | Preceding hour mean | W/m² | Shortwave solar radiation |
| `direct_radiation`, `direct_normal_irradiance` | Preceding hour mean | W/m² | Direct solar radiation |
| `diffuse_radiation` | Preceding hour mean | W/m² | Diffuse solar radiation |
| `global_tilted_irradiance` | Preceding hour mean | W/m² | Total radiation on tilted pane |
| `sunshine_duration` | Preceding hour sum | Seconds | Seconds of sunshine |
| `wind_speed_10m`, `wind_speed_100m` | Instant | km/h (mph, m/s, knots) | Wind speed at 10m or 100m |
| `wind_direction_10m`, `wind_direction_100m` | Instant | ° | Wind direction at 10m or 100m |
| `wind_gusts_10m` | Instant | km/h (mph, m/s, knots) | Maximum wind gusts at 10m |
| `et0_fao_evapotranspiration` | Preceding hour sum | mm (inch) | ET₀ Reference Evapotranspiration |
| `weather_code` | Instant | WMO code | Weather condition numeric code |
| `snow_depth` | Instant | meters | Snow depth on ground |
| `vapour_pressure_deficit` | Instant | kPa | Vapor Pressure Deficit (VPD) |
| `soil_temperature_0_to_7cm`, `..._7_to_28cm`, `..._28_to_100cm`, `..._100_to_255cm` | Instant | °C (°F) | Average soil temperature at depths |
| `soil_moisture_0_to_7cm`, `..._7_to_28cm`, `..._28_to_100cm`, `..._100_to_255cm` | Instant | m³/m³ | Average soil water content at depths |

## Daily Variables

| Variable | Unit | Description |
| :--- | :--- | :--- |
| `weather_code` | WMO code | Most severe weather condition on a day |
| `temperature_2m_max`, `temperature_2m_min` | °C (°F) | Maximum and minimum daily air temperature |
| `apparent_temperature_max`, `apparent_temperature_min` | °C (°F) | Maximum and minimum daily apparent temperature |
| `precipitation_sum` | mm | Sum of daily precipitation |
| `rain_sum` | mm | Sum of daily rain |
| `snowfall_sum` | cm | Sum of daily snowfall |
| `precipitation_hours` | hours | Number of hours with rain |
| `sunrise`, `sunset` | iso8601 | Sun rise and set times |
| `sunshine_duration` | seconds | Seconds of sunshine per day |
| `daylight_duration` | seconds | Seconds of daylight per day |
| `wind_speed_10m_max`, `wind_gusts_10m_max` | km/h (mph, m/s, knots) | Maximum wind speed and gusts |
| `wind_direction_10m_dominant` | ° | Dominant wind direction |
| `shortwave_radiation_sum` | MJ/m² | Sum of solar radiation |
| `et0_fao_evapotranspiration` | mm | Daily sum of ET₀ Reference Evapotranspiration |
