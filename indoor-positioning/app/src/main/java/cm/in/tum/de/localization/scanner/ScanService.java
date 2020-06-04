package cm.in.tum.de.localization.scanner;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

import cm.in.tum.de.localization.data.Measurement;
import cm.in.tum.de.localization.utils.AppStorage;

public class ScanService {

  private static final String TAG = ScanService.class.getSimpleName();

  private final BleScanner bleScanner;
  private final WifiScanner wifiScanner;
  private final Map<Integer, Measurement> bleData;
  private final Map<Integer, Measurement> wifiData;
  private int measurementPeriod;
  private final IResultCallback resultCallback;
  private CountDownLatch countDownLatch;
  private Measurement wifiMeasurement;
  private Measurement bleMeasurement;
  private int positionId;
  private boolean wifiScanCompleted;
  private boolean bleScanCompleted;
  private boolean offline;

  public ScanService(Context applicationContext,
                     IResultCallback resultCallback,
                     int measurementPeriod,
                     CountDownLatch semaphoreInterface) {
    this.resultCallback = resultCallback;
    this.measurementPeriod = measurementPeriod;
    this.bleData = new HashMap<>();
    this.bleScanner = new BleScanner(applicationContext, this,
            semaphoreInterface);
    this.wifiData = new HashMap<>();
    this.wifiScanner = new WifiScanner(applicationContext, this,
            semaphoreInterface);
  }

  public void startScan(boolean block, final boolean ble, final boolean wifi) {
    setWifiScanCompleted(true);
    setBleScanCompleted(true);
    if (ble) {
      setBleScanCompleted(false);
      getBleScanner().startScan();
    }
    if(wifi) {
      setWifiScanCompleted(false);
      getWifiScanner().startScan();
    }
    new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
      @Override
      public void run() {
        if (ble) {
          getBleScanner().stopScan();
        }
        if (wifi) {
          getWifiScanner().stopScan();
        }
      }
    }, getMeasurementPeriod() * 1000);
    if(block) {
      try {
        this.countDownLatch = new CountDownLatch(1);
        getCountDownLatch().await();
      } catch (InterruptedException e) {
        Log.e(TAG, "block scan service", e);
      }
    }
  }

  // Offline phase with position id
  public void startScan(int positionId) {
    setPositionId((positionId));
    setOffline(true);
    startScan(false, true, true);
  }

  public void onWifiScanCompleted(Measurement measurement) {
    if (isOffline()) {
      getWifiData().put(getPositionId(), measurement);
      AppStorage.saveWifiData(getWifiData());
    } else {
      setWifiMeasurement(measurement);
    }
    setWifiScanCompleted(true);
    checkScanCompleted();
  }

  public void onBleScanCompleted(Measurement measurement) {
    if (isOffline()) {
      getBleData().put(getPositionId(), measurement);
      AppStorage.saveBleData(getBleData());
    } else {
      setBleMeasurement(measurement);
    }
    setBleScanCompleted(true);
    checkScanCompleted();
  }

  public int getBleSize() {
    return getBleData().size();
  }

  public int getWifiSize() {
    return getWifiData().size();
  }

  private void checkScanCompleted() {
    if (isWifiScanCompleted() && isBleScanCompleted()) {
      if (isOffline()) {
        getResultCallback().onResult();
      } else {
        getCountDownLatch().countDown();
      }
    }
  }

  public void setMeasurementPeriod(int measurementPeriod) {
    this.measurementPeriod = measurementPeriod;
  }

  private void setPositionId(int positionId) {
    this.positionId = positionId;
  }

  private int getPositionId() {
    return this.positionId;
  }

  private Map<Integer, Measurement> getBleData() {
    return this.bleData;
  }

  private Map<Integer, Measurement> getWifiData() {
    return this.wifiData;
  }

  private BleScanner getBleScanner() {
    return this.bleScanner;
  }

  private WifiScanner getWifiScanner() {
    return this.wifiScanner;
  }

  private int getMeasurementPeriod() {
    return this.measurementPeriod;
  }

  private boolean isWifiScanCompleted() {
    return this.wifiScanCompleted;
  }

  private boolean isBleScanCompleted() {
    return this.bleScanCompleted;
  }

  private void setWifiScanCompleted(boolean wifiScanCompleted) {
    this.wifiScanCompleted = wifiScanCompleted;
  }

  private void setBleScanCompleted(boolean bleScanCompleted) {
    this.bleScanCompleted = bleScanCompleted;
  }

  private IResultCallback getResultCallback() {
    return this.resultCallback;
  }

  private void setOffline(boolean offline) {
    this.offline = offline;
  }

  private boolean isOffline() {
    return this.offline;
  }

  private void setWifiMeasurement(Measurement wifiMeasurement) {
    this.wifiMeasurement = wifiMeasurement;
  }

  private void setBleMeasurement(Measurement bleMeasurement) {
    this.bleMeasurement = bleMeasurement;
  }

  public Measurement getWifiMeasurement() {
    return this.wifiMeasurement;
  }

  public Measurement getBleMeasurement() {
    return this.bleMeasurement;
  }

  private CountDownLatch getCountDownLatch() {
    return this.countDownLatch;
  }

}
