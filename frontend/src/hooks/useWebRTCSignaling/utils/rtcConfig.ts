/**
 * WebRTC Configuration utilities
 */

import { WebRTCConfig } from '../types';

/**
 * Default STUN servers (Google's public STUN servers)
 */
const DEFAULT_STUN_SERVERS: RTCIceServer[] = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
];

/**
 * Create WebRTC configuration with optional TURN servers
 * 
 * @param turnServers - Array of TURN server configurations
 * @param options - Additional RTC configuration options
 * @returns Complete RTCConfiguration object
 */
export function createRTCConfig(
  turnServers: RTCIceServer[] = [],
  options: Partial<WebRTCConfig> = {}
): RTCConfiguration {
  const iceServers = [
    ...DEFAULT_STUN_SERVERS,
    ...turnServers,
    ...(options.iceServers || []),
  ];

  return {
    iceServers,
    iceTransportPolicy: options.iceTransportPolicy || 'all',
    bundlePolicy: options.bundlePolicy || 'max-bundle',
    rtcpMuxPolicy: options.rtcpMuxPolicy || 'require',
  };
}

/**
 * Validate RTCConfiguration
 */
export function validateRTCConfig(config: RTCConfiguration): boolean {
  if (!config.iceServers || config.iceServers.length === 0) {
    return false;
  }

  return config.iceServers.every((server) => {
    if (!server.urls) return false;
    const urls = Array.isArray(server.urls) ? server.urls : [server.urls];
    return urls.every((url) => typeof url === 'string' && url.length > 0);
  });
}
