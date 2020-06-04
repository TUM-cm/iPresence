package cm.in.tum.de.localization;

import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import cm.in.tum.de.localization.scanner.ScanService;
import fi.iki.elonen.NanoHTTPD;

public class RestInterface extends NanoHTTPD {

  private static final String TAG = RestInterface.class.getSimpleName();
  private final ScanService scanService;
  private final Gson gson;

  public RestInterface(int port, ScanService scanService) {
    super(port);
    this.scanService = scanService;
    this.gson = new GsonBuilder().setPrettyPrinting().create();
  }

  // Call server running on Android to perform Wi-Fi and Bluetooth scanning from external program
  @Override
  public Response serve(IHTTPSession session) {
    Method method = session.getMethod();
    Map<String, String> map = new HashMap<>();
    if (Method.PUT.equals(method) || Method.POST.equals(method)) {
      try {
        session.parseBody(map);
      } catch (IOException ioe) {
        return newFixedLengthResponse(Response.Status.INTERNAL_ERROR, MIME_PLAINTEXT,
                "SERVER INTERNAL ERROR: IOException: " + ioe.getMessage());
      } catch (ResponseException re) {
        return newFixedLengthResponse(re.getStatus(), MIME_PLAINTEXT, re.getMessage());
      }
    }
    String uri = session.getUri();
    if(uri.equals("/measurement")) {
      String values = map.get("postData");
      Log.d(TAG, "parms: " + map.toString());
      values = values.substring(1, values.length()-1);
      String[] elements = values.split(",");
      Map<String, String> parms = new HashMap<>();
      for(String element : elements) {
        String[] parts = element.split(":");
        String key = parts[0].trim();
        key = key.substring(1, key.length()-1);
        String value = parts[1].trim();
        parms.put(key, value);
      }
      Log.d(TAG, "parms: " + parms.toString());
      boolean bleStatus = Boolean.valueOf(parms.get("BLE"));
      boolean wifiStatus = Boolean.valueOf(parms.get("WIFI"));
      int duration = Integer.valueOf(parms.get("duration"));
      Log.d(TAG, "ble: " + bleStatus + ", wifi: " + wifiStatus + ", duration: " + duration);
      getScanService().setMeasurementPeriod(duration);
      getScanService().startScan(true, bleStatus, wifiStatus);
      String ble = getGson().toJson(getScanService().getBleMeasurement());
      String wifi = getGson().toJson(getScanService().getWifiMeasurement());
      String mimeType = "application/json";
      String data = "{\"ble\":" + ble + ", \"wifi\":" + wifi + "}";
      return newFixedLengthResponse(Response.Status.OK, mimeType, data);
    }
    return null;
  }

  private Gson getGson() {
    return this.gson;
  }

  private ScanService getScanService() {
    return this.scanService;
  }

}
