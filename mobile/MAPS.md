# Meeting map

After a successful meeting search, choose Map to see both starting landmarks,
the geographic midpoint, and all returned places. Tap a green place pin to
show its card and directions below. List restores all cards in server order.
Fit all places restores the viewport. The map also shows starting locations
and the midpoint when no places match. Sorting and wider searches use the same
API flow as List; no additional location permission is requested.

Install dependencies with `npm ci` and restart Metro with `npm start -- --clear`.
`react-native-maps` is included in Expo Go for SDK 57. iOS uses Apple Maps by
default, so no Google Maps key is required for the iOS simulator. Android uses
Google Maps; a standalone Android binary needs a restricted Google Maps SDK
key in the react-native-maps config plugin and a rebuilt binary. See:
https://docs.expo.dev/versions/v57.0.0/sdk/map-view/

Web retains the list and displays an explanatory message in Map mode. Native
map tiles require connectivity. The app doesn't draw or calculate routes;
directions still open externally. Map tiles and gestures need a device or
simulator check; an Expo bundle export alone doesn't verify native rendering.

## Choose starting points

The home screen's Pick on map opens a native map for each person. Tap or drag
the pin, then confirm; Cancel leaves the existing point unchanged. Points must
be inside the backend's broad NYC service box (40.47–40.93 latitude,
-74.27–-73.69 longitude). This box is not an exact borough boundary. Coordinates
are sent directly to /meet; no geocoding or location permission is required.
Landmark selection remains available. Older landmark-based result links still
resolve. Web uses landmark selection because native map picking is unavailable.

## Remember the last search

Both starting points (including exact map coordinates), category, and sort
preference are saved automatically on this device using AsyncStorage. The app
restores them before showing the form, and serializes saves to keep rapid
changes in order. Reset saved search replaces the saved settings with default
landmarks, Cafés, and Fairest. Corrupt or unsupported records fall back to defaults;
storage errors leave the current session usable. No results or tokens are stored.
The stored search is local and unencrypted; it is not synced to other devices.

Manual checks: choose two map points, cancel an edit to verify the old point
stays selected, then search and change sort. Close and reopen the app to verify
both points, category, and sort restore. Try Reset saved search and reopen again.
The map's native gestures and persistence across app restarts need device or
simulator validation in addition to automated checks.
