package cm.in.tum.de.localization.scanner;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.os.SystemClock;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;

import cm.in.tum.de.localization.data.Measurement;
import cm.in.tum.de.localization.data.MeasurementEntry;
import cm.in.tum.de.localization.utils.GUIUtils;

public class BleScanner {

  private static final String TAG = BleScanner.class.getSimpleName();

  private final Context applicationContext;
  private final BluetoothManager bluetoothManager;
  private final BluetoothAdapter bluetoothAdapter;
  private final ScanService scanService;
  private final CountDownLatch semaphoreInterface;
  private ScanSettings aggressiveScanSettings;
  private BluetoothLeScanner bluetoothLeScanner;
  private ScanCallback scanCallback;
  private long startTimestamp;
  private long stopTimestamp;
  private List<MeasurementEntry> entries;

  public BleScanner(Context applicationContext, ScanService scanService,
                    CountDownLatch semaphoreInterface) {
    this.applicationContext = applicationContext;
    this.scanService = scanService;
    this.semaphoreInterface = semaphoreInterface;
    this.bluetoothManager = (BluetoothManager) getApplicationContext()
            .getSystemService(Context.BLUETOOTH_SERVICE);
    this.bluetoothAdapter = getBluetoothManager().getAdapter();
    if (getBluetoothAdapter() == null) {
      GUIUtils.showFinishingAlertDialog(((Activity) getApplicationContext()),
              "Bluetooth Error",
              "Bluetooth not detected on device");
    } else if (!getBluetoothAdapter().isEnabled()) {
      GUIUtils.showFinishingAlertDialog(((Activity) getApplicationContext()),
              "Bluetooth",
              "Enable Bluetooth");
    } else {
      this.scanCallback = buildScanCallback();
      this.bluetoothLeScanner = getBluetoothAdapter().getBluetoothLeScanner();
      this.aggressiveScanSettings = new ScanSettings.Builder()
              .setReportDelay(0)
              .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
              .build();
      getSemaphoreInterface().countDown();
    }
  }

  private ScanCallback buildScanCallback() {

    return new ScanCallback() {
      @Override
      public void onScanResult(final int callbackType, final ScanResult result) {
        Log.d(TAG, "ble scan");
        entries.add(new MeasurementEntry(result.getDevice().getAddress(), result.getRssi()));
      }

      @Override
      public void onBatchScanResults(final List<ScanResult> results) {
      }

      @Override
      public void onScanFailed(int errorCode) {
      }
    };
  }

  public void startScan() {
    this.entries = new ArrayList<>();
    this.startTimestamp = SystemClock.elapsedRealtime();
    getBluetoothLeScanner().startScan(null,
            getAggressiveScanSettings(),
            getScanCallback());
  }

  public void stopScan() {
    this.stopTimestamp = SystemClock.elapsedRealtime();
    getBluetoothLeScanner().stopScan(getScanCallback());
    getScanService().onBleScanCompleted(new Measurement(startTimestamp, stopTimestamp, entries));
  }

  private ScanSettings getAggressiveScanSettings() {
    return this.aggressiveScanSettings;
  }

  private BluetoothLeScanner getBluetoothLeScanner() {
    return this.bluetoothLeScanner;
  }

  private BluetoothAdapter getBluetoothAdapter() {
    return this.bluetoothAdapter;
  }

  private ScanCallback getScanCallback() {
    return this.scanCallback;
  }

  private Context getApplicationContext() {
    return this.applicationContext;
  }

  private BluetoothManager getBluetoothManager() {
    return this.bluetoothManager;
  }

  private ScanService getScanService() {
    return this.scanService;
  }

  private CountDownLatch getSemaphoreInterface() {
    return this.semaphoreInterface;
  }

}
