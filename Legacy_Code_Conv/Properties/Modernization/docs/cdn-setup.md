# CDN Setup Guide

This guide explains how to set up and configure CDN delivery for the Icon System.

## Overview

The Icon System uses a CDN to deliver optimized SVG icons with:
- Automatic theme switching
- Efficient caching
- Performance optimization
- Error handling

## CDN Configuration

### 1. Environment Setup

Create or update your `.env` file:

```env
NEXT_PUBLIC_CDN_URL=https://your-cdn.com/assets
NEXT_PUBLIC_CDN_REGION=us-east-1
NEXT_PUBLIC_CDN_CACHE_DURATION=86400
```

### 2. Directory Structure

Organize your CDN assets:

```
assets/
├── light/
│   ├── checked.svg
│   ├── unchecked.svg
│   ├── reload.svg
│   └── ...
└── dark/
    ├── checked.svg
    ├── unchecked.svg
    ├── reload.svg
    └── ...
```

### 3. Cache Configuration

Set up caching headers:

```nginx
# Nginx configuration
location /assets/ {
    expires 24h;
    add_header Cache-Control "public, no-transform";
    add_header Access-Control-Allow-Origin "*";
}
```

## Asset Deployment

### 1. Asset Optimization

Run optimization before deployment:

```bash
#!/bin/bash
# optimize-icons.sh

for file in assets/**/*.svg; do
  svgo -i "$file" -o "$file"
done
```

### 2. Upload Script

Deploy assets to CDN:

```bash
#!/bin/bash
# deploy-icons.sh

AWS_PROFILE=your-profile
BUCKET=your-bucket
DISTRIBUTION_ID=your-distribution-id

# Upload assets
aws s3 sync ./assets s3://$BUCKET/assets \
  --profile $AWS_PROFILE \
  --cache-control "public,max-age=86400"

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/assets/*" \
  --profile $AWS_PROFILE
```

## Performance Optimization

### 1. Browser Caching

Configure service worker:

```ts
// sw.js
workbox.routing.registerRoute(
  /\/assets\/.*/,
  new workbox.strategies.CacheFirst({
    cacheName: 'icon-cache',
    plugins: [
      new workbox.expiration.ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 24 * 60 * 60
      })
    ]
  })
);
```

### 2. Preloading

Configure icon preloading:

```ts
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/assets/:path*',
        headers: [
          {
            key: 'Link',
            value: '</assets/light/checked.svg>; rel=preload; as=image'
          }
        ]
      }
    ];
  }
};
```

## Monitoring

### 1. Performance Metrics

Monitor CDN performance:

```ts
export function trackIconLoad(name: string, loadTime: number) {
  console.log(`Icon ${name} loaded in ${loadTime}ms`);
  // Send to analytics
}
```

### 2. Error Tracking

Monitor CDN errors:

```ts
export function trackCDNError(error: Error) {
  console.error('CDN Error:', error);
  // Send to error tracking
}
```

## Troubleshooting

### Common Issues

1. CORS Errors
   ```nginx
   # Add to CDN configuration
   add_header Access-Control-Allow-Origin "*";
   add_header Access-Control-Allow-Methods "GET, OPTIONS";
   ```

2. Caching Issues
   ```bash
   # Force cache invalidation
   aws cloudfront create-invalidation \
     --distribution-id $DISTRIBUTION_ID \
     --paths "/assets/*"
   ```

3. Performance Issues
   - Enable Brotli compression
   - Use HTTP/2 or HTTP/3
   - Enable edge caching

## Security

### 1. Access Control

Restrict CDN access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket/assets/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::account-id:distribution/dist-id"
        }
      }
    }
  ]
}
```

### 2. Content Security Policy

Add CSP headers:

```nginx
add_header Content-Security-Policy "default-src 'self'; img-src 'self' https://your-cdn.com";
```
