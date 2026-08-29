import { clsx } from "clsx";
import type { ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(inputs));
};

/**
 * Convert a snake_case string to camelCase
 */
const toCamelCase = (str: string): string => {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
};

/**
 * Convert a camelCase string to snake_case
 */
const toSnakeCase = (str: string): string => {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
};

/**
 * Convert object keys from snake_case to camelCase (deep)
 * Used when receiving data from Django backend
 */
export const keysToCamelCase = <T = any>(obj: any): T => {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => keysToCamelCase(item)) as T;
  }

  if (typeof obj === "object" && obj.constructor === Object) {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = toCamelCase(key);
      acc[camelKey] = keysToCamelCase(obj[key]);
      return acc;
    }, {} as any) as T;
  }

  return obj;
};

/**
 * Convert object keys from camelCase to snake_case (deep)
 * Used when sending data to Django backend
 */
export const keysToSnakeCase = <T = any>(obj: any): T => {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => keysToSnakeCase(item)) as T;
  }

  if (typeof obj === "object" && obj.constructor === Object) {
    return Object.keys(obj).reduce((acc, key) => {
      const snakeKey = toSnakeCase(key);
      acc[snakeKey] = keysToSnakeCase(obj[key]);
      return acc;
    }, {} as any) as T;
  }

  return obj;
};
