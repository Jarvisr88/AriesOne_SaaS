using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AriesOne.Core.Events.Map
{
    /// <summary>
    /// Configuration options for map providers
    /// </summary>
    public class MapProviderOptions
    {
        public string DefaultProviderId { get; set; } = string.Empty;
        public int MaxRetryAttempts { get; set; } = 3;
        public TimeSpan RetryDelay { get; set; } = TimeSpan.FromSeconds(1);
        public TimeSpan ProviderTimeout { get; set; } = TimeSpan.FromSeconds(30);
        public bool EnableFallback { get; set; } = true;
        public List<string> FallbackProviders { get; set; } = new();
    }

    /// <summary>
    /// Interface for map provider manager
    /// </summary>
    public interface IMapProviderManager : IDisposable
    {
        Task<bool> RegisterProviderAsync(IMapProvider provider);
        Task<bool> UnregisterProviderAsync(string providerId);
        Task<IMapProvider?> GetProviderAsync(string providerId);
        Task<IEnumerable<IMapProvider>> GetAllProvidersAsync();
        Task<bool> IsProviderAvailableAsync(string providerId);
        event AsyncMapEventHandler<MapProviderEventArgs> OnMapEvent;
    }

    /// <summary>
    /// Modern map provider manager implementation
    /// </summary>
    public class MapProviderManager : IMapProviderManager
    {
        private readonly ConcurrentDictionary<string, IMapProvider> _providers;
        private readonly ILogger<MapProviderManager> _logger;
        private readonly IMapEventLogger _eventLogger;
        private readonly MapProviderOptions _options;
        private readonly CancellationTokenSource _cts;

        public event AsyncMapEventHandler<MapProviderEventArgs>? OnMapEvent;

        public MapProviderManager(
            ILogger<MapProviderManager> logger,
            IMapEventLogger eventLogger,
            IOptions<MapProviderOptions> options)
        {
            _providers = new ConcurrentDictionary<string, IMapProvider>();
            _logger = logger;
            _eventLogger = eventLogger;
            _options = options.Value;
            _cts = new CancellationTokenSource();
        }

        public async Task<bool> RegisterProviderAsync(IMapProvider provider)
        {
            try
            {
                if (_providers.TryAdd(provider.ProviderId, provider))
                {
                    // Subscribe to provider events
                    provider.OnLocationUpdate += HandleLocationUpdateAsync;
                    provider.OnRouteCalculation += HandleRouteCalculationAsync;
                    provider.OnGeofenceUpdate += HandleGeofenceUpdateAsync;
                    provider.OnStatusChange += HandleStatusChangeAsync;
                    provider.OnError += HandleErrorAsync;

                    var eventArgs = new ProviderStatusEventArgs(
                        provider.ProviderId,
                        true,
                        "Registered",
                        provider.Capabilities,
                        new Dictionary<string, object>
                        {
                            { "RegisteredAt", DateTime.UtcNow }
                        },
                        _cts.Token
                    );

                    await RaiseEventAsync(this, eventArgs);
                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error registering provider: {ProviderId}", provider.ProviderId);
                return false;
            }
        }

        public async Task<bool> UnregisterProviderAsync(string providerId)
        {
            try
            {
                if (_providers.TryRemove(providerId, out var provider))
                {
                    // Unsubscribe from provider events
                    provider.OnLocationUpdate -= HandleLocationUpdateAsync;
                    provider.OnRouteCalculation -= HandleRouteCalculationAsync;
                    provider.OnGeofenceUpdate -= HandleGeofenceUpdateAsync;
                    provider.OnStatusChange -= HandleStatusChangeAsync;
                    provider.OnError -= HandleErrorAsync;

                    var eventArgs = new ProviderStatusEventArgs(
                        providerId,
                        false,
                        "Unregistered",
                        provider.Capabilities,
                        new Dictionary<string, object>
                        {
                            { "UnregisteredAt", DateTime.UtcNow }
                        },
                        _cts.Token
                    );

                    await RaiseEventAsync(this, eventArgs);
                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error unregistering provider: {ProviderId}", providerId);
                return false;
            }
        }

        public async Task<IMapProvider?> GetProviderAsync(string providerId)
        {
            try
            {
                if (_providers.TryGetValue(providerId, out var provider))
                {
                    return provider;
                }

                if (_options.EnableFallback)
                {
                    foreach (var fallbackId in _options.FallbackProviders)
                    {
                        if (_providers.TryGetValue(fallbackId, out var fallbackProvider))
                        {
                            _logger.LogInformation(
                                "Using fallback provider: {FallbackId} for request to: {ProviderId}",
                                fallbackId,
                                providerId
                            );
                            return fallbackProvider;
                        }
                    }
                }

                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting provider: {ProviderId}", providerId);
                return null;
            }
        }

        public Task<IEnumerable<IMapProvider>> GetAllProvidersAsync()
        {
            return Task.FromResult(_providers.Values.AsEnumerable());
        }

        public async Task<bool> IsProviderAvailableAsync(string providerId)
        {
            try
            {
                var provider = await GetProviderAsync(providerId);
                if (provider == null)
                {
                    return false;
                }

                return await provider.IsAvailableAsync(_cts.Token);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking provider availability: {ProviderId}", providerId);
                return false;
            }
        }

        private async Task HandleLocationUpdateAsync(object sender, LocationUpdateEventArgs e)
        {
            await RaiseEventAsync(sender, e);
        }

        private async Task HandleRouteCalculationAsync(object sender, RouteCalculationEventArgs e)
        {
            await RaiseEventAsync(sender, e);
        }

        private async Task HandleGeofenceUpdateAsync(object sender, GeofenceEventArgs e)
        {
            await RaiseEventAsync(sender, e);
        }

        private async Task HandleStatusChangeAsync(object sender, ProviderStatusEventArgs e)
        {
            await RaiseEventAsync(sender, e);
        }

        private async Task HandleErrorAsync(object sender, MapProviderEventArgs e)
        {
            if (e.Error != null)
            {
                await _eventLogger.LogErrorAsync(e, e.Error, _logger);
            }
            await RaiseEventAsync(sender, e);
        }

        private async Task RaiseEventAsync<T>(object sender, T args) where T : MapProviderEventArgs
        {
            try
            {
                await _eventLogger.LogEventAsync(args, _logger);

                if (OnMapEvent != null)
                {
                    var handlers = OnMapEvent.GetInvocationList();
                    var tasks = new List<Task>();

                    foreach (AsyncMapEventHandler<MapProviderEventArgs> handler in handlers)
                    {
                        tasks.Add(handler.Invoke(sender, args));
                    }

                    await Task.WhenAll(tasks);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error raising map event: {EventType}", args.EventType);
            }
        }

        public void Dispose()
        {
            _cts.Cancel();
            _cts.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}
