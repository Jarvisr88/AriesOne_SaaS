import React, { useEffect, useRef, useState } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { cn } from "@/lib/utils";
import { MapViewProps } from "@/types/address";
import { mapStyles } from "@/config/map-styles";

export function MapView({
  center,
  zoom,
  markers = [],
  onMapClick,
  className,
}: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [googleMarkers, setGoogleMarkers] = useState<google.maps.Marker[]>([]);

  useEffect(() => {
    if (!mapRef.current) return;

    const loader = new Loader({
      apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
      version: "weekly",
    });

    loader.load().then(() => {
      const mapInstance = new google.maps.Map(mapRef.current!, {
        center,
        zoom,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.RIGHT_TOP,
        },
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        styles: mapStyles,
        gestureHandling: "cooperative",
        disableDefaultUI: true,
        backgroundColor: "#f8fafc",
      });

      // Add custom controls container
      const customControlsDiv = document.createElement("div");
      customControlsDiv.className = "custom-map-controls";
      customControlsDiv.style.margin = "10px";
      mapInstance.controls[google.maps.ControlPosition.TOP_LEFT].push(customControlsDiv);

      if (onMapClick) {
        mapInstance.addListener("click", (e: google.maps.MapMouseEvent) => {
          if (e.latLng) {
            onMapClick({
              lat: e.latLng.lat(),
              lng: e.latLng.lng(),
            });
          }
        });
      }

      setMap(mapInstance);
    });

    return () => {
      googleMarkers.forEach((marker) => marker.setMap(null));
    };
  }, []);

  useEffect(() => {
    if (map) {
      map.setCenter(center);
    }
  }, [map, center.lat, center.lng]);

  useEffect(() => {
    if (map) {
      map.setZoom(zoom);
    }
  }, [map, zoom]);

  useEffect(() => {
    if (!map) return;

    googleMarkers.forEach((marker) => marker.setMap(null));

    const newMarkers = markers.map((markerData) => {
      const marker = new google.maps.Marker({
        position: markerData.position,
        map,
        title: markerData.title,
        animation: google.maps.Animation.DROP,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: "#3b82f6",
          fillOpacity: 1,
          strokeColor: "#ffffff",
          strokeWeight: 2,
        },
      });

      // Add hover effect
      marker.addListener("mouseover", () => {
        marker.setIcon({
          path: google.maps.SymbolPath.CIRCLE,
          scale: 12,
          fillColor: "#2563eb",
          fillOpacity: 1,
          strokeColor: "#ffffff",
          strokeWeight: 2,
        });
      });

      marker.addListener("mouseout", () => {
        marker.setIcon({
          path: google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: "#3b82f6",
          fillOpacity: 1,
          strokeColor: "#ffffff",
          strokeWeight: 2,
        });
      });

      if (markerData.onClick) {
        marker.addListener("click", markerData.onClick);
      }

      // Add InfoWindow
      if (markerData.title) {
        const infoWindow = new google.maps.InfoWindow({
          content: `<div class="p-2 text-sm font-medium">${markerData.title}</div>`,
        });

        marker.addListener("click", () => {
          infoWindow.open(map, marker);
        });
      }

      return marker;
    });

    setGoogleMarkers(newMarkers);

    return () => {
      newMarkers.forEach((marker) => marker.setMap(null));
    };
  }, [map, markers]);

  return (
    <div
      ref={mapRef}
      className={cn(
        "w-full h-full rounded-md border border-border bg-muted overflow-hidden shadow-sm",
        className
      )}
    />
  );
}
