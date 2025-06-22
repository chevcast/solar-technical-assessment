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
        data = json.loads(request.body)
        lat = float(data.get("lat"))
        lng = float(data.get("lng"))
        offset_angle = float(data.get("offsetAngle", 0.0))

        year = datetime.now().year
        times = pd.date_range(
            f"{year}-01-01 00:00:00",
            f"{year}-12-31 23:00:00",
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
        global_horizontal_irradiance = clearsky["ghi"]

        # Optimize tilt by maximizing plane-of-array irradiance
        tilt_span = np.arange(lat - 15.0, lat + 15.0, 1.0)
        best_tilt, best_energy = tilt_span[0], -np.inf

        for tilt in tilt_span:
            poa_sum = irradiance.get_total_irradiance(
                surface_tilt=tilt,
                surface_azimuth=180.0
                if lat >= 0
                else 0.0,  # south-facing north of equator
                solar_zenith=solpos["zenith"],
                solar_azimuth=solpos["azimuth"],
                dni=direct_normal_irradiance,
                ghi=global_horizontal_irradiance,
                dhi=diffuse_horizontal_irradiance,
                dni_extra=dni_extra,
                model="haydavies",
            )["poa_global"].sum()

            if poa_sum > best_energy:
                best_energy, best_tilt = poa_sum, tilt

        pitch_raw = float(best_tilt - offset_angle)
        pitch = max(0.0, min(90.0, pitch_raw))

        # local-solar-noon azimuth on the spring equinox
        site_tz = location.tz
        equinox_day = pd.Timestamp(f"{year}-03-21", tz=site_tz)
        day_minutes = pd.date_range(
            equinox_day,
            equinox_day + pd.Timedelta(days=1) - pd.Timedelta(minutes=1),
            freq="1min",
            tz=site_tz,
        )
        solpos_day = pd.DataFrame(location.get_solarposition(day_minutes))
        noon_idx = solpos_day["zenith"].idxmin()
        azimuth = round(float(solpos_day.loc[noon_idx, "azimuth"]), 2)

        # TODO: Allow specifying tilt calculation mode (seasonal or monthly averages)
        # and accept a date parameter for specific calculations

        # TODO: PV system simulation for energy output estimation

        # TODO: Add terrain modeling using elevation DSM

        # TODO: Also use DSM to calculate accurate obstacle shading throughout the year

        # TODO: Cache data in Redis based on input parameters to avoid redundant future calculations

        return JsonResponse({"pitch": round(pitch, 2), "azimuth": azimuth})

    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)
