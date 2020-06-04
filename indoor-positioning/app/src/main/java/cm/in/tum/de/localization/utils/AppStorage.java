package cm.in.tum.de.localization.utils;

import android.os.Environment;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

import cm.in.tum.de.localization.data.Measurement;

public class AppStorage {

  public static final String TAG = AppStorage.class.getSimpleName();
  public static final String STORAGE_FOLDER_NAME = "IndoorLocalization";
  public static final String STORAGE_PATH = Environment.getExternalStorageDirectory()
          .getAbsolutePath() + File.separator + STORAGE_FOLDER_NAME + File.separator;

  private static final String BLE_FINGERPRINTS = STORAGE_PATH + "bluetooth-fingerprints";
  private static final String WIFI_FINGERPRINTS = STORAGE_PATH + "wifi-fingerprints";

  public static void createDataFolder() {
    File directory = new File(STORAGE_PATH);
    if (!directory.exists()) {
      directory.mkdirs();
    }
  }

  public static void saveBleData(Map<Integer, Measurement> data) {
    saveData(data, AppStorage.BLE_FINGERPRINTS);
  }

  public static void saveWifiData(Map<Integer, Measurement> data) {
    saveData(data, AppStorage.WIFI_FINGERPRINTS);
  }

  private static void saveData(Map<Integer, Measurement> data, String filepath) {
    try {
      BufferedWriter writer = new BufferedWriter(new FileWriter(filepath));
      Gson gson = new GsonBuilder().setPrettyPrinting().create();
      gson.toJson(data, writer);
      writer.flush();
      writer.close();
    } catch (IOException e) {
      Log.e(TAG, "error saving data");
    }
  }

}
