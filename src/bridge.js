/* The only bundled file in the project.

   Capacitor 8 populates Capacitor.Plugins[name] inside registerPlugin(), which
   lives in each plugin's own ES module — so official plugins are unreachable
   from plain script-tag JS. This exposes the ones we need on window, which lets
   index.html stay dependency-free and unbundled.

   Bundling @capacitor/core alongside the injected native bridge is safe:
   createCapacitor() does `win.Capacitor || {}`, so it merges onto the bridge
   and keeps its PluginHeaders rather than replacing it.

   Built by `npm run bundle` into www/bridge.js. Only the Android bundle gets
   it — copy-web.mjs injects the script tag, so the GitHub Pages copy of
   index.html is untouched and has nothing to 404 on. */
import { LocalNotifications } from "@capacitor/local-notifications";
import { Filesystem, Directory, Encoding } from "@capacitor/filesystem";
import { Share } from "@capacitor/share";
import { Capacitor } from "@capacitor/core";

window.EveryDayNative = {
  LocalNotifications,
  Filesystem,
  Directory,
  Encoding,
  Share,
  Capacitor,
};
