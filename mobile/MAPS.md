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
