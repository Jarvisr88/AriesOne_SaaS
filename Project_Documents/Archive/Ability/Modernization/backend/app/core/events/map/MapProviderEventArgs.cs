using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;

namespace AriesOne.Core.Events.Map
{
    /// <summary>
    /// Represents the type of map provider event
    /// </summary>
    public enum MapEventType
    {
        LocationUpdate,
        RouteCalculation,
        GeofenceUpdate,
        ProviderStatusChange,
        Error
    }

    /// <summary>
    /// Represents the severity level of a map event
    /// </summary>
    public enum MapEventSeverity
    {
        Info,
        Warning,
        Error,
        Critical
    }

    /// <summary>
    /// Base interface for map provider capabilities
    /// </summary>
    public interface IMapProviderCapabilities
    {
        bool SupportsRealTimeTracking { get; }
        bool SupportsGeofencing { get; }
        bool SupportsRouteOptimization { get; }
        bool SupportsOfflineMode { get; }
        int MaxConcurrentRequests { get; }
        TimeSpan RequestTimeout { get; }
    }

    /// <summary>
    /// Modern event arguments for map provider events
    /// </summary>
    public class MapProviderEventArgs : EventArgs
    {
        public string ProviderId { get; }
        public MapEventType EventType { get; }
        public MapEventSeverity Severity { get; }
        public DateTime Timestamp { get; }
        public IDictionary<string, object> Metadata { get; }
        public Exception? Error { get; }

        [JsonIgnore]
        public CancellationToken CancellationToken { get; }

        public MapProviderEventArgs(
            string providerId,
            MapEventType eventType,
            MapEventSeverity severity = MapEventSeverity.Info,
            IDictionary<string, object>? metadata = null,
            Exception? error = null,
            CancellationToken cancellationToken = default)
        {
            ProviderId = providerId;
            EventType = eventType;
            Severity = severity;
            Timestamp = DateTime.UtcNow;
            Metadata = metadata ?? new Dictionary<string, object>();
            Error = error;
            CancellationToken = cancellationToken;
        }
    }

    /// <summary>
    /// Event arguments for location updates
    /// </summary>
    public class LocationUpdateEventArgs : MapProviderEventArgs
    {
        public double Latitude { get; }
        public double Longitude { get; }
        public double? Accuracy { get; }
        public double? Altitude { get; }
        public double? Speed { get; }
        public double? Heading { get; }

        public LocationUpdateEventArgs(
            string providerId,
            double latitude,
            double longitude,
            double? accuracy = null,
            double? altitude = null,
            double? speed = null,
            double? heading = null,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default)
            : base(providerId, MapEventType.LocationUpdate, MapEventSeverity.Info, metadata, null, cancellationToken)
        {
            Latitude = latitude;
            Longitude = longitude;
            Accuracy = accuracy;
            Altitude = altitude;
            Speed = speed;
            Heading = heading;
        }
    }

    /// <summary>
    /// Event arguments for route calculations
    /// </summary>
    public class RouteCalculationEventArgs : MapProviderEventArgs
    {
        public List<(double Latitude, double Longitude)> Waypoints { get; }
        public double Distance { get; }
        public TimeSpan Duration { get; }
        public string? RoutePolyline { get; }
        public IDictionary<string, object> RouteMetadata { get; }

        public RouteCalculationEventArgs(
            string providerId,
            List<(double Latitude, double Longitude)> waypoints,
            double distance,
            TimeSpan duration,
            string? routePolyline = null,
            IDictionary<string, object>? routeMetadata = null,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default)
            : base(providerId, MapEventType.RouteCalculation, MapEventSeverity.Info, metadata, null, cancellationToken)
        {
            Waypoints = waypoints;
            Distance = distance;
            Duration = duration;
            RoutePolyline = routePolyline;
            RouteMetadata = routeMetadata ?? new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Event arguments for geofence updates
    /// </summary>
    public class GeofenceEventArgs : MapProviderEventArgs
    {
        public string GeofenceId { get; }
        public bool IsInside { get; }
        public double Distance { get; }
        public DateTime EnteredAt { get; }
        public DateTime? ExitedAt { get; }

        public GeofenceEventArgs(
            string providerId,
            string geofenceId,
            bool isInside,
            double distance,
            DateTime enteredAt,
            DateTime? exitedAt = null,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default)
            : base(providerId, MapEventType.GeofenceUpdate, MapEventSeverity.Info, metadata, null, cancellationToken)
        {
            GeofenceId = geofenceId;
            IsInside = isInside;
            Distance = distance;
            EnteredAt = enteredAt;
            ExitedAt = exitedAt;
        }
    }

    /// <summary>
    /// Event arguments for provider status changes
    /// </summary>
    public class ProviderStatusEventArgs : MapProviderEventArgs
    {
        public bool IsAvailable { get; }
        public string Status { get; }
        public IMapProviderCapabilities Capabilities { get; }

        public ProviderStatusEventArgs(
            string providerId,
            bool isAvailable,
            string status,
            IMapProviderCapabilities capabilities,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default)
            : base(providerId, MapEventType.ProviderStatusChange, MapEventSeverity.Info, metadata, null, cancellationToken)
        {
            IsAvailable = isAvailable;
            Status = status;
            Capabilities = capabilities;
        }
    }

    /// <summary>
    /// Delegate for asynchronous map provider events
    /// </summary>
    public delegate Task AsyncMapEventHandler<TEventArgs>(object sender, TEventArgs e)
        where TEventArgs : MapProviderEventArgs;

    /// <summary>
    /// Interface for map event logging
    /// </summary>
    public interface IMapEventLogger
    {
        Task LogEventAsync(MapProviderEventArgs eventArgs, ILogger logger);
        Task LogErrorAsync(MapProviderEventArgs eventArgs, Exception error, ILogger logger);
    }

    /// <summary>
    /// Default implementation of map event logger
    /// </summary>
    public class DefaultMapEventLogger : IMapEventLogger
    {
        public async Task LogEventAsync(MapProviderEventArgs eventArgs, ILogger logger)
        {
            await Task.Run(() =>
            {
                var logLevel = eventArgs.Severity switch
                {
                    MapEventSeverity.Info => LogLevel.Information,
                    MapEventSeverity.Warning => LogLevel.Warning,
                    MapEventSeverity.Error => LogLevel.Error,
                    MapEventSeverity.Critical => LogLevel.Critical,
                    _ => LogLevel.Information
                };

                logger.Log(
                    logLevel,
                    "Map provider event: {ProviderId} - {EventType} - {Timestamp}",
                    eventArgs.ProviderId,
                    eventArgs.EventType,
                    eventArgs.Timestamp
                );

                if (eventArgs.Metadata.Count > 0)
                {
                    logger.Log(
                        logLevel,
                        "Event metadata: {@Metadata}",
                        eventArgs.Metadata
                    );
                }
            });
        }

        public async Task LogErrorAsync(MapProviderEventArgs eventArgs, Exception error, ILogger logger)
        {
            await Task.Run(() =>
            {
                logger.LogError(
                    error,
                    "Map provider error: {ProviderId} - {EventType} - {Message}",
                    eventArgs.ProviderId,
                    eventArgs.EventType,
                    error.Message
                );
            });
        }
    }
}
