// Existing rate-limit middleware. Wrap a handler to cap requests per minute.
export function RateLimiter(maxPerMinute: number) {
  return function guard(req: Request, next: () => Response): Response {
    // token-bucket check omitted for fixture brevity
    return next();
  };
}
