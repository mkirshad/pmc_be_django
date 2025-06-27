import json

from django.contrib.gis.db.models.functions import AsGeoJSON
from django.shortcuts import render
from django.http import JsonResponse
from django.core.serializers import serialize
from django.db.models import Count, F
from .idm_models import DistrictsNew, EecClubs
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

ALLOWED_GROUPS = {'Super', 'EEC', 'Admin', 'DEO', 'DG', 'DO', 'LSM', 'LSO', 'TL'}

def user_has_permission(request):
    print('request.user', request.user)
    return request.user.is_authenticated and request.user.groups.filter(name__in=ALLOWED_GROUPS).exists()


def districts_club_counts(request):
    geojson = cache.get('districts_club_geojson')

    if geojson is None:
        districts = DistrictsNew.objects.annotate(
            club_count=Count("eecclubs"),
            geom_json=AsGeoJSON("geom", precision=5)
        ).values("id", "short_name", "club_count", "geom_json")

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(d["geom_json"]),
                "properties": {
                    "id": d["id"],
                    "name": d["short_name"],
                    "club_count": d["club_count"],
                },
            }
            for d in districts
        ]

        geojson = {
            "type": "FeatureCollection",
            "features": features,
        }

        cache.set('districts_club_geojson', geojson, timeout=3600)  # cached for 1 hour

    return JsonResponse(geojson)

def clubs_geojson(request, district_id=None):
    show_sensitive_data = user_has_permission(request)
    clubs = EecClubs.objects.filter(district_id=district_id,
                                    latitude__isnull=False, longitude__isnull=False)

    features = []
    for club in clubs:
        if club.latitude and club.longitude:
            props = {
                "id": club.id,
                "emiscode": club.emiscode,
                "name": club.school_name,
                "address": club.address,
                "head_name": club.head_name,
                "district": club.district_name,
            }
            if show_sensitive_data:
                props["head_mobile"] = club.head_mobile_no_field
                props["notification_path"] = str(club.notification_path.url) if club.notification_path else None

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [club.longitude, club.latitude]
                },
                "properties": props
            })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

# @login_required
def clubs_geojson_all(request):
    show_sensitive_data = user_has_permission(request)
    clubs = EecClubs.objects.filter(latitude__isnull=False, longitude__isnull=False)
    print('show_sensitive_data', show_sensitive_data)
    features = []
    for club in clubs:
        if club.latitude and club.longitude:
            props = {
                "id": club.id,
                "emiscode": club.emiscode,
                "name": club.school_name,
                "address": club.address,
                "head_name": club.head_name,
                "district_id": club.district_id.id if club.district_id else None,
                "district": club.district_name,
            }
            if show_sensitive_data:
                props["head_mobile"] = club.head_mobile_no_field
                props["notification_path"] = str(club.notification_path.url) if club.notification_path else None

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [club.longitude, club.latitude]
                },
                "properties": props
            })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

class ClubGeoJSONViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def all(self, request):
        show_sensitive_data = user_has_permission(request)
        clubs = EecClubs.objects.filter(latitude__isnull=False, longitude__isnull=False)

        features = []
        for club in clubs:
            if club.latitude and club.longitude:
                props = {
                    "id": club.id,
                    "emiscode": club.emiscode,
                    "name": club.school_name,
                    "address": club.address,
                    "head_name": club.head_name,
                    "district_id": club.district_id.id if club.district_id else None,
                    "district": club.district_name,
                }
                if show_sensitive_data:
                    props["head_mobile"] = club.head_mobile_no_field
                    props["notification_path"] = str(club.notification_path.url) if club.notification_path else None

                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [club.longitude, club.latitude]
                    },
                    "properties": props
                })

        return Response({
            "type": "FeatureCollection",
            "features": features
        })