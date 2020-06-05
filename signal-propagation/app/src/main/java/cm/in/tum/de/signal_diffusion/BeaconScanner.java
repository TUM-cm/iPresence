package cm.in.tum.de.signal_diffusion;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanSettings;
import android.content.Intent;

import java.util.ArrayList;
import java.util.List;

import cm.in.tum.de.signal_diffusion.utils.Config;
import cm.in.tum.de.signal_diffusion.utils.ConfigSection;
import cm.in.tum.de.signal_diffusion.utils.GUIUtils;

public class BeaconScanner {

  public static final int PERMISSION_REQUEST_BLUETOOTH = 1;
  private final BluetoothAdapter bluetoothAdapter;
  private ScanSettings aggressiveScanSettings;
  private BluetoothLeScanner bluetoothLeScanner;
  private List<ScanFilter> scanFilters;
  private Config config;

  public BeaconScanner(Activity activity, BluetoothManager bluetoothManager, Config config) {
    this.config = config;
    this.bluetoothAdapter = bluetoothManager.getAdapter();
    if (getBluetoothAdapter() == null) {
      GUIUtils.showFinishingAlertDialog(activity,
              "Bluetooth Error",
              "Bluetooth not detected on device");
    } else if (!getBluetoothAdapter().isEnabled()) {
      Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
      activity.startActivityForResult(enableBtIntent, PERMISSION_REQUEST_BLUETOOTH);
    } else {
      init();
    }
  }

  public void init() {
    this.bluetoothLeScanner = getBluetoothAdapter().getBluetoothLeScanner();
    this.aggressiveScanSettings = new ScanSettings.Builder()
            .setReportDelay(0)
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build();
    this.scanFilters = new ArrayList<>();
    getScanFilters().add(new ScanFilter.Builder()
            .setDeviceAddress(getConfigValue("Beacon MAC").toUpperCase())
            .build());
  }

  public void startScan(ScanCallback scanCallback) {
    getBluetoothLeScanner().startScan(getScanFilters(),
            getAggressiveScanSettings(), scanCallback);
  }

  public void stopScan(ScanCallback scanCallback) {
    getBluetoothLeScanner().stopScan(scanCallback);
  }

  private ScanSettings getAggressiveScanSettings() {
    return this.aggressiveScanSettings;
  }

  private BluetoothLeScanner getBluetoothLeScanner() {
    return this.bluetoothLeScanner;
  }

  private List<ScanFilter> getScanFilters() {
    return this.scanFilters;
  }

  private String getConfigValue(String key) {
    return getConfig().get(key, ConfigSection.BEACON_MEASUREMENTS, String.class);
  }

  private Config getConfig() {
    return this.config;
  }

  private BluetoothAdapter getBluetoothAdapter() {
    return this.bluetoothAdapter;
  }

}