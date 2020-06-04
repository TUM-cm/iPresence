package cm.in.tum.de.localization.scanner;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.SystemClock;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;

import cm.in.tum.de.localization.data.Measurement;
import cm.in.tum.de.localization.data.MeasurementEntry;

public class WifiScanner extends BroadcastReceiver {

  private static final String TAG = WifiScanner.class.getSimpleName();

  private final WifiManager wifiManager;
  private final Context applicationContext;
  private final ScanService scanService;
  private final CountDownLatch semaphoreInterface;
  private long startTimestamp;
  private long stopTimestamp;
  List<MeasurementEntry> entries;
  private boolean stopScan;

  public WifiScanner(Context applicationContext, ScanService scanService,
                     CountDownLatch semaphoreInterface) {
    this.applicationContext = applicationContext;
    this.scanService = scanService;
    this.semaphoreInterface = semaphoreInterface;
    this.wifiManager = (WifiManager) getApplicationContext()
            .getSystemService(Context.WIFI_SERVICE);
    if (!getWifiManager().isWifiEnabled()) {
      getWifiManager().setWifiEnabled(true);
    }
    getSemaphoreInterface().countDown();
  }

  public void startScan() {
    this.entries = new ArrayList<>();
    getApplicationContext().registerReceiver(this,
            new IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION));
    setStopScan(false);
    this.startTimestamp = SystemClock.elapsedRealtime();
    getWifiManager().startScan();
  }

  public void stopScan() {
    setStopScan(true);
  }

  @Override
  public void onReceive(Context context, Intent intent) {
    Log.d(TAG, "wifi scan");
    List<ScanResult> scanResultList = getWifiManager().getScanResults();
    for(ScanResult scanResult : scanResultList) {
      entries.add(new MeasurementEntry(scanResult.BSSID, scanResult.level));
    }
    if (isStopScan()) {
      this.stopTimestamp = SystemClock.elapsedRealtime();
      getApplicationContext().unregisterReceiver(this);
      getScanService().onWifiScanCompleted(new Measurement(startTimestamp, stopTimestamp, entries));
    } else {
      getWifiManager().startScan();
    }
  }

  private WifiManager getWifiManager() {
    return this.wifiManager;
  }

  private Context getApplicationContext() {
    return this.applicationContext;
  }

  private boolean isStopScan() {
    return this.stopScan;
  }

  private void setStopScan(boolean stopScan) {
    this.stopScan = stopScan;
  }

  private ScanService getScanService() {
    return this.scanService;
  }

  private CountDownLatch getSemaphoreInterface() {
    return this.semaphoreInterface;
  }

}
