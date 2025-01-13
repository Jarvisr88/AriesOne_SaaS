using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace AriesOne.Core.Events.Map
{
    /// <summary>
    /// Interface for map providers
    /// </summary>
    public interface IMapProvider : IDisposable
    {
        string ProviderId { get; }
        IMapProviderCapabilities Capabilities { get; }
        
        Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default);
        Task<bool> InitializeAsync(IDictionary<string, object> config, CancellationToken cancellationToken = default);
        Task<bool> ShutdownAsync(CancellationToken cancellationToken = default);

        // Async events
        event AsyncMapEventHandler<LocationUpdateEventArgs> OnLocationUpdate;
        event AsyncMapEventHandler<RouteCalculationEventArgs> OnRouteCalculation;
        event AsyncMapEventHandler<GeofenceEventArgs> OnGeofenceUpdate;
        event AsyncMapEventHandler<ProviderStatusEventArgs> OnStatusChange;
        event AsyncMapEventHandler<MapProviderEventArgs> OnError;

        // Core functionality
        Task<LocationUpdateEventArgs> UpdateLocationAsync(
            double latitude,
            double longitude,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default);

        Task<RouteCalculationEventArgs> CalculateRouteAsync(
            List<(double Latitude, double Longitude)> waypoints,
            IDictionary<string, object>? options = null,
            CancellationToken cancellationToken = default);

        Task<GeofenceEventArgs> UpdateGeofenceAsync(
            string geofenceId,
            double latitude,
            double longitude,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Base implementation of map provider capabilities
    /// </summary>
    public class MapProviderCapabilities : IMapProviderCapabilities
    {
        public bool SupportsRealTimeTracking { get; set; }
        public bool SupportsGeofencing { get; set; }
        public bool SupportsRouteOptimization { get; set; }
        public bool SupportsOfflineMode { get; set; }
        public int MaxConcurrentRequests { get; set; }
        public TimeSpan RequestTimeout { get; set; }

        public MapProviderCapabilities(
            bool supportsRealTimeTracking = true,
            bool supportsGeofencing = true,
            bool supportsRouteOptimization = true,
            bool supportsOfflineMode = false,
            int maxConcurrentRequests = 10,
            TimeSpan? requestTimeout = null)
        {
            SupportsRealTimeTracking = supportsRealTimeTracking;
            SupportsGeofencing = supportsGeofencing;
            SupportsRouteOptimization = supportsRouteOptimization;
            SupportsOfflineMode = supportsOfflineMode;
            MaxConcurrentRequests = maxConcurrentRequests;
            RequestTimeout = requestTimeout ?? TimeSpan.FromSeconds(30);
        }
    }

    /// <summary>
    /// Base implementation of map provider
    /// </summary>
    public abstract class BaseMapProvider : IMapProvider
    {
        protected readonly string _providerId;
        protected readonly IMapProviderCapabilities _capabilities;
        protected readonly SemaphoreSlim _semaphore;
        protected bool _isInitialized;
        protected IDictionary<string, object> _config;
        protected readonly CancellationTokenSource _cts;

        public string ProviderId => _providerId;
        public IMapProviderCapabilities Capabilities => _capabilities;

        public event AsyncMapEventHandler<LocationUpdateEventArgs>? OnLocationUpdate;
        public event AsyncMapEventHandler<RouteCalculationEventArgs>? OnRouteCalculation;
        public event AsyncMapEventHandler<GeofenceEventArgs>? OnGeofenceUpdate;
        public event AsyncMapEventHandler<ProviderStatusEventArgs>? OnStatusChange;
        public event AsyncMapEventHandler<MapProviderEventArgs>? OnError;

        protected BaseMapProvider(
            string providerId,
            IMapProviderCapabilities capabilities)
        {
            _providerId = providerId;
            _capabilities = capabilities;
            _semaphore = new SemaphoreSlim(capabilities.MaxConcurrentRequests);
            _isInitialized = false;
            _config = new Dictionary<string, object>();
            _cts = new CancellationTokenSource();
        }

        public virtual async Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default)
        {
            return _isInitialized && !_cts.Token.IsCancellationRequested;
        }

        public virtual async Task<bool> InitializeAsync(
            IDictionary<string, object> config,
            CancellationToken cancellationToken = default)
        {
            try
            {
                _config = config;
                _isInitialized = true;

                await RaiseStatusChangeAsync(
                    true,
                    "Initialized",
                    new Dictionary<string, object>
                    {
                        { "InitializedAt", DateTime.UtcNow }
                    },
                    cancellationToken
                );

                return true;
            }
            catch (Exception ex)
            {
                await RaiseErrorAsync(
                    "Initialization failed",
                    ex,
                    MapEventSeverity.Error,
                    cancellationToken
                );
                return false;
            }
        }

        public virtual async Task<bool> ShutdownAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                _isInitialized = false;
                _cts.Cancel();

                await RaiseStatusChangeAsync(
                    false,
                    "Shutdown",
                    new Dictionary<string, object>
                    {
                        { "ShutdownAt", DateTime.UtcNow }
                    },
                    cancellationToken
                );

                return true;
            }
            catch (Exception ex)
            {
                await RaiseErrorAsync(
                    "Shutdown failed",
                    ex,
                    MapEventSeverity.Error,
                    cancellationToken
                );
                return false;
            }
        }

        public abstract Task<LocationUpdateEventArgs> UpdateLocationAsync(
            double latitude,
            double longitude,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default);

        public abstract Task<RouteCalculationEventArgs> CalculateRouteAsync(
            List<(double Latitude, double Longitude)> waypoints,
            IDictionary<string, object>? options = null,
            CancellationToken cancellationToken = default);

        public abstract Task<GeofenceEventArgs> UpdateGeofenceAsync(
            string geofenceId,
            double latitude,
            double longitude,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default);

        protected virtual async Task RaiseLocationUpdateAsync(
            LocationUpdateEventArgs args,
            CancellationToken cancellationToken = default)
        {
            if (OnLocationUpdate != null)
            {
                await OnLocationUpdate.Invoke(this, args);
            }
        }

        protected virtual async Task RaiseRouteCalculationAsync(
            RouteCalculationEventArgs args,
            CancellationToken cancellationToken = default)
        {
            if (OnRouteCalculation != null)
            {
                await OnRouteCalculation.Invoke(this, args);
            }
        }

        protected virtual async Task RaiseGeofenceUpdateAsync(
            GeofenceEventArgs args,
            CancellationToken cancellationToken = default)
        {
            if (OnGeofenceUpdate != null)
            {
                await OnGeofenceUpdate.Invoke(this, args);
            }
        }

        protected virtual async Task RaiseStatusChangeAsync(
            bool isAvailable,
            string status,
            IDictionary<string, object>? metadata = null,
            CancellationToken cancellationToken = default)
        {
            if (OnStatusChange != null)
            {
                var args = new ProviderStatusEventArgs(
                    _providerId,
                    isAvailable,
                    status,
                    _capabilities,
                    metadata,
                    cancellationToken
                );
                await OnStatusChange.Invoke(this, args);
            }
        }

        protected virtual async Task RaiseErrorAsync(
            string message,
            Exception error,
            MapEventSeverity severity = MapEventSeverity.Error,
            CancellationToken cancellationToken = default)
        {
            if (OnError != null)
            {
                var args = new MapProviderEventArgs(
                    _providerId,
                    MapEventType.Error,
                    severity,
                    new Dictionary<string, object>
                    {
                        { "Message", message },
                        { "ErrorType", error.GetType().Name }
                    },
                    error,
                    cancellationToken
                );
                await OnError.Invoke(this, args);
            }
        }

        protected virtual async Task<T> ExecuteWithRetryAsync<T>(
            Func<CancellationToken, Task<T>> action,
            int maxRetries = 3,
            TimeSpan? delay = null,
            CancellationToken cancellationToken = default)
        {
            var retryDelay = delay ?? TimeSpan.FromSeconds(1);
            var attempt = 0;

            while (true)
            {
                try
                {
                    await _semaphore.WaitAsync(cancellationToken);
                    return await action(cancellationToken);
                }
                catch (Exception ex) when (attempt < maxRetries)
                {
                    attempt++;
                    await RaiseErrorAsync(
                        $"Operation failed (Attempt {attempt}/{maxRetries})",
                        ex,
                        MapEventSeverity.Warning,
                        cancellationToken
                    );
                    await Task.Delay(retryDelay * attempt, cancellationToken);
                }
                finally
                {
                    _semaphore.Release();
                }
            }
        }

        public virtual void Dispose()
        {
            _semaphore.Dispose();
            _cts.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}
