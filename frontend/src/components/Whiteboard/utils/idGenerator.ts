/**
 * ID generation utilities
 */

/**
 * Generate a unique path ID
 */
export function generatePathId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
