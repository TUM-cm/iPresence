package cm.in.tum.de.signal_diffusion.utils;

import android.os.Environment;

import java.io.File;

public class AppStorage {

  public static final String STORAGE_FOLDER_NAME = "SignalPropagationBluetooth";
  public static final String STORAGE_PATH = Environment.getExternalStorageDirectory().getAbsolutePath() +
          File.separator + STORAGE_FOLDER_NAME + File.separator;
  public static final String DATA_FILE = "bluetooth";

  public static void createDataFolder() {
    File directory = new File(STORAGE_PATH);
    if (!directory.exists()) {
      directory.mkdirs();
    }
  }

}
