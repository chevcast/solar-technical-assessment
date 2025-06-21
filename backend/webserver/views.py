from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pvlib.location import Location
from pvlib import irradiance
from pvlib.irradiance import get_extra_radiation
from datetime import datetime
import pandas as pd
import numpy as np
import json


@csrf_exempt
@require_http_methods(["POST"])
def calculate_optimal_angles(request):
    try:
        # Parse and validate input
        data = json.loads(request.body)
        lat = float(data.get("lat"))
        lng = float(data.get("lng"))
        offset_angle = float(data.get("offsetAngle", 0))

        # NREL (Liu & Jordan classic) rule
        # optimal_tilt = 0.9 * lat

        # Masters/Duffie-Beckman rule
        # optimal_tilt = 0.76 * lat + 3.1

        # Reverse-engineered formula from shopsolarkits and sunsolartilt calculators
        # optimal_tilt = 0.7 * lat + 3.5

        year = datetime.now().year
        times = pd.date_range(
            start=f"{year}-01-01 00:00:00",
            end=f"{year}-12-31 23:00:00",
            freq="1h",
            tz="UTC",
        )
        dni_extra = get_extra_radiation(times)

        location = Location(lat, lng, tz="UTC")
        solpos = location.get_solarposition(times)
        clearsky = location.get_clearsky(times)

        # Total direct sunlight hitting the panel
        direct_normal_irradiance = clearsky["dni"]
        # Diffuse atmosphere-scattered sunlight reflected onto panel
        diffuse_horizontal_irradiance = clearsky["dhi"]
        # Total sunlight hitting the panel, including direct and diffuse
        # ghi = dni * cos(zenith) + dhi
        global_horizontal_irradiance = clearsky["ghi"]

        # Optimize tilt by maximizing POA irradiance
        tilts = np.arange(lat - 15, lat + 15, 1)
        best_tilt = 0
        best_energy = -np.inf

        for tilt in tilts:
            irrads = irradiance.get_total_irradiance(
                surface_tilt=tilt,
                surface_azimuth=180
                if lat >= 0
                else 0,  # Assume south-facing in northern hemisphere
                solar_zenith=solpos["zenith"],
                solar_azimuth=solpos["azimuth"],
                dni=direct_normal_irradiance,
                ghi=global_horizontal_irradiance,
                dhi=diffuse_horizontal_irradiance,
                dni_extra=dni_extra,
                model="haydavies",
            )
            total_poa = irrads["poa_global"].sum()
            if total_poa > best_energy:
                best_energy = total_poa
                best_tilt = tilt

        # Full plane-of-array optimization
        optimal_tilt = best_tilt

        # Adjust for angled ground terrain using specified offset
        pitch = optimal_tilt - offset_angle
        pitch = max(0, min(90.0, float(pitch)))  # clamp to 0-90 degress
        time = pd.Timestamp(datetime(datetime.now().year, 3, 21, 12), tz="UTC")
        solpos_noon = pd.DataFrame(location.get_solarposition(time))
        azimuth = round(float(solpos_noon["azimuth"].iloc[0]), 2)

        # TODO: Allow specifying tilt calculation mode (seasonal or monthly averages)
        # and accept a date parameter for specific calculations

        # TODO: PV system simulation for energy output estimation

        # TODO: Add terrain modeling using elevation DSM

        # TODO: Also use DSM to calculate accurate obstacle shading throughout the year

        # TODO: Cache data in Redis based on input parameters to avoid redundant future calculations

        return JsonResponse({"pitch": round(pitch, 2), "azimuth": azimuth})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
