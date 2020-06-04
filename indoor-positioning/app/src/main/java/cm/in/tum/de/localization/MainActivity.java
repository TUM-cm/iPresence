package cm.in.tum.de.localization;

import android.app.ProgressDialog;
import android.graphics.Color;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.CountDownLatch;

import cm.in.tum.de.localization.scanner.IResultCallback;
import cm.in.tum.de.localization.scanner.ScanService;
import cm.in.tum.de.localization.tethering.ITetheringCallback;
import cm.in.tum.de.localization.tethering.UsbTethering;
import cm.in.tum.de.localization.utils.AppStorage;
import cm.in.tum.de.localization.utils.Config;
import cm.in.tum.de.localization.utils.ConfigSection;
import cm.in.tum.de.localization.utils.GUIUtils;
import cm.in.tum.de.localization.utils.IPermissionListener;
import cm.in.tum.de.localization.utils.PermissionHandler;

public class MainActivity
        extends AppCompatActivity
        implements IPermissionListener, ITetheringCallback, IResultCallback {

  private static final int NUM_WIRELESS_INTERFACES = 2;
  private static final String TAG = MainActivity.class.getSimpleName();

  private Config config;
  private TextView status;
  private ProgressDialog progressDialog;
  private PermissionHandler permissionHandler;
  private Button positionId;
  private ScanService scanService;
  private boolean offlineMode;
  private int numPerRow;
  private int numMeasurements;
  private int interfacePort;
  private CountDownLatch semaphoreInterface;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    this.permissionHandler = new PermissionHandler(this, this);
    this.status = findViewById(R.id.status);
    getStatus().setText("Bluetooth and Wifi scan not available");
    getPermissionHandler().checkPermissions();
  }

  @Override
  public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
    getPermissionHandler().onRequestPermissionsResult(requestCode, grantResults);
  }

  @Override
  public void onPermissionsGranted() {
    AppStorage.createDataFolder();
    InputStream in = getResources().openRawResource(getConfigResource());
    this.config = new Config(in);
    this.offlineMode = getConfig().get("Offline mode", ConfigSection.GENERAL, boolean.class);
    this.interfacePort = getConfig().get("Interface port", ConfigSection.GENERAL, int.class);
    this.numPerRow = getConfig().get("Row", ConfigSection.MEASUREMENTS, int.class);
    this.progressDialog = new ProgressDialog(this);
    int measurementPeriod = getConfig().get("Period", ConfigSection.MEASUREMENTS, int.class);
    this.semaphoreInterface = new CountDownLatch(NUM_WIRELESS_INTERFACES);
    this.scanService = new ScanService(this, this,
            measurementPeriod, semaphoreInterface);
    getStatus().setText("Bluetooth and Wifi scan available");
    if (isOfflineMode()) {
      this.numMeasurements = getConfig().get("Num", ConfigSection.MEASUREMENTS, int.class);
      buildScanPositions(getNumMeasurements());
    } else {
      try {
        this.semaphoreInterface.await();
        UsbTethering usbTethering = new UsbTethering(this, this);
        usbTethering.start();
      } catch (InterruptedException e) {
        e.printStackTrace();
        Log.d(TAG, "wait failed for USB tethering", e);
      }
    }
  }

  @Override
  public void onPermissionsNotGranted() {
    String title = "Permission Handler";
    String message = "Not all required permissions are granted, please allow necessary permissions";
    GUIUtils.showOKAlertDialog(this, title, message);
  }

  @Override
  public void onUsbTethering(String ip) {
    getStatus().setText("USB tethering active, IP: " + ip);
    try {
      RestInterface server = new RestInterface(getInterfacePort(), getScanService());
      server.start();
      getStatus().setText("USB tethering and HTTP server active");
    } catch (IOException e) {
      Log.e(TAG, "cannot start REST server", e);
    }
  }

  @Override
  public void onResult() {
    int bleSize = getScanService().getBleSize();
    int wifiSize = getScanService().getWifiSize();
    boolean status = (bleSize == wifiSize);
    getStatus().setText("Recording: " + status + ", Num: " + wifiSize + "/" + getNumMeasurements());
    getPositionId().setBackgroundColor(Color.GREEN);
    getProgressDialog().dismiss();
  }

  private void buildScanPositions(int positions) {
    TableLayout table = findViewById(R.id.measurements);
    TableRow row = new TableRow(this);
    for (int i = 0; i < positions; i++) {
      final Button button = new Button(this);
      button.setText(String.valueOf(i + 1));
      row.addView(button);
      button.setOnClickListener(new View.OnClickListener() {
        @Override
        public void onClick(View v) {
          getProgressDialog().setTitle("Collect data");
          getProgressDialog().setMessage("BLE and WiFi data ...");
          startProgressDialog();
          setPositionId(button);
          int posId = Integer.valueOf(getPositionId().getText().toString());
          getScanService().startScan(posId);
        }
      });
      // Calculate new line of table layout (add new table row)
      boolean newline = (i + 1) % getNumPerRow() == 0;
      boolean end = (i == positions-1);
      if (newline || end) {
        table.addView(row, new TableLayout.LayoutParams(TableLayout.LayoutParams.WRAP_CONTENT,
                TableLayout.LayoutParams.WRAP_CONTENT));
        row = new TableRow(this);
      }
    }
    getProgressDialog().dismiss();
  }

  private void startProgressDialog() {
    getProgressDialog().setProgressStyle(ProgressDialog.STYLE_SPINNER);
    getProgressDialog().setIndeterminate(true);
    getProgressDialog().show();
  }

  public static int getConfigResource() {
    return R.raw.config;
  }

  private PermissionHandler getPermissionHandler() {
    return this.permissionHandler;
  }

  private Config getConfig() {
    return this.config;
  }

  private int getNumPerRow() {
    return this.numPerRow;
  }

  private ProgressDialog getProgressDialog() {
    return this.progressDialog;
  }

  private TextView getStatus() {
    return this.status;
  }

  private boolean isOfflineMode() {
    return this.offlineMode;
  }

  private Button getPositionId() {
    return this.positionId;
  }

  private void setPositionId(Button positionId) {
    this.positionId = positionId;
  }

  private int getNumMeasurements() {
    return this.numMeasurements;
  }

  private int getInterfacePort() {
    return this.interfacePort;
  }

  private ScanService getScanService() {
    return this.scanService;
  }

}
