package cm.in.tum.de.signal_diffusion;

import android.app.ProgressDialog;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import cm.in.tum.de.signal_diffusion.utils.AppStorage;
import cm.in.tum.de.signal_diffusion.utils.Config;
import cm.in.tum.de.signal_diffusion.utils.ConfigSection;
import cm.in.tum.de.signal_diffusion.utils.GUIUtils;
import cm.in.tum.de.signal_diffusion.utils.IPermissionListener;
import cm.in.tum.de.signal_diffusion.utils.PermissionHandler;

public class MainActivity extends AppCompatActivity implements IPermissionListener {

  private static final String TAG = MainActivity.class.getSimpleName();
  private static final int ELEMENTS_PER_ROW = 3;
  private BeaconScanner beaconScanner;
  private TextView status;
  private TextView macField;
  private TextView rssiField;
  private ScanCallback scanCallbackFindBeacon;
  private ScanCallback scanCallbackRssi;
  private Map<Integer, List<Double>> bluetoothData;
  private List<Double> rssiList;
  private PermissionHandler permissionHandler;
  private Config config;
  private int measurementPeriod;
  private ProgressDialog progressDialog;
  private Button findBeacon;
  private boolean beaconFound;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    this.permissionHandler = new PermissionHandler(this, this);
    this.status = findViewById(R.id.status);
    getStatus().setText("Bluetooth scan not available");
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
    this.measurementPeriod = getConfig().get("Period", ConfigSection.MEASUREMENTS, int.class);
    init();
  }

  @Override
  public void onPermissionsNotGranted() {
    String title = "Permission Handler";
    String message = "Not all required permissions are granted, please allow necessary permissions";
    GUIUtils.showOKAlertDialog(this, title, message);
  }

  @Override
  protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    if (requestCode == BeaconScanner.PERMISSION_REQUEST_BLUETOOTH) {
      if (resultCode == RESULT_OK) {
        getBeaconScanner().init();
      }
    }
  }

  private void init() {
    this.bluetoothData = new HashMap<>();
    BluetoothManager bluetoothManager = (BluetoothManager) getSystemService(BLUETOOTH_SERVICE);
    this.beaconScanner = new BeaconScanner(this, bluetoothManager, getConfig());
    this.scanCallbackRssi = buildScanCallbackRssi();
    this.scanCallbackFindBeacon = buildScanCallbackFindBeacon();
    this.findBeacon = findViewById(R.id.findBeacon);
    getFindBeaconButton().setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        getProgressDialog().setTitle("Setup");
        getProgressDialog().setMessage("Find Bluetooth beacon ...");
        startProgressDialog();
        getBeaconScanner().startScan(getScanCallbackFindBeacon());
      }
    });
    this.macField = findViewById(R.id.mac);
    this.rssiField = findViewById(R.id.rssi);
    this.progressDialog = new ProgressDialog(this);
    getStatus().setText("Bluetooth scan available");
    getFindBeaconButton().setEnabled(true);
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
          getProgressDialog().setMessage("Bluetooth beacon data ...");
          startProgressDialog();
          final int measurementId = Integer.valueOf(button.getText().toString());
          setRssiList();
          getBeaconScanner().startScan(getScanCallbackRssi());
          new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
              getBeaconScanner().stopScan(getScanCallbackRssi());
              if (getRssiList().size() == 0) {
                getRssiList().add(-100.0);
              }
              getBluetoothData().put(measurementId, getRssiList());
              saveBluetoothData();
              double sumRssi = 0;
              for (double value : getRssiList()) {
                sumRssi += value;
              }
              double averageRssi = Math.round((sumRssi / getRssiList().size()) * 100.0) / 100.0;
              StringBuilder message = new StringBuilder("RSSI: ");
              message.append(averageRssi);
              getStatus().setText("Measurement result, Values: " + getRssiList().size() + ", RSSI: " + averageRssi);
              button.setBackgroundColor(Color.GREEN);
              getProgressDialog().dismiss();
            }
          }, getMeasurementPeriod() * 1000);
        }
      });
      // Calculate new line of table layout (add new table row)
      if ((i + 1) % ELEMENTS_PER_ROW == 0 && (i + 1) != 72 || (i + 1) == positions || (i + 1) == 71) {
        table.addView(row,
                new TableLayout.LayoutParams(TableLayout.LayoutParams.WRAP_CONTENT,
                        TableLayout.LayoutParams.WRAP_CONTENT));
        row = new TableRow(this);
      }
    }
    getProgressDialog().dismiss();
  }

  private ScanCallback buildScanCallbackRssi() {
    return new ScanCallback() {
      @Override
      public void onScanResult(final int callbackType, final ScanResult result) {
        getRssiList().add(Double.valueOf(result.getRssi()));
      }

      @Override
      public void onBatchScanResults(final List<ScanResult> results) {
      }

      @Override
      public void onScanFailed(int errorCode) {
      }
    };
  }

  private ScanCallback buildScanCallbackFindBeacon() {
    return new ScanCallback() {
      @Override
      public void onScanResult(final int callbackType, final ScanResult result) {
        getBeaconScanner().stopScan(getScanCallbackFindBeacon());
        if (!isBeaconFound()) {
          setBeaconFound(true);
          getMacField().setText(result.getDevice().getAddress());
          getRssiField().setText(String.valueOf(result.getRssi()));
          int numMeasurements = getConfig().get("Num", ConfigSection.MEASUREMENTS, int.class);
          buildScanPositions(numMeasurements);
        }
      }

      @Override
      public void onBatchScanResults(final List<ScanResult> results) {
      }

      @Override
      public void onScanFailed(int errorCode) {
      }
    };
  }

  private void saveBluetoothData() {
    try {
      String path = AppStorage.STORAGE_PATH + AppStorage.DATA_FILE;
      BufferedWriter writer = new BufferedWriter(new FileWriter(path));
      Gson gson = new GsonBuilder().setPrettyPrinting().create();
      gson.toJson(getBluetoothData(), writer);
      writer.flush();
      writer.close();
    } catch (IOException e) {
      Log.e(TAG, "error saving bluetooth data");
    }
  }

  private void startProgressDialog() {
    getProgressDialog().setProgressStyle(ProgressDialog.STYLE_SPINNER);
    getProgressDialog().setIndeterminate(true);
    getProgressDialog().show();
  }

  public static int getConfigResource() {
    return R.raw.config;
  }

  private BeaconScanner getBeaconScanner() {
    return this.beaconScanner;
  }

  private TextView getMacField() {
    return this.macField;
  }

  private TextView getRssiField() {
    return this.rssiField;
  }

  private ScanCallback getScanCallbackRssi() {
    return this.scanCallbackRssi;
  }

  private ScanCallback getScanCallbackFindBeacon() {
    return this.scanCallbackFindBeacon;
  }

  private Map<Integer, List<Double>> getBluetoothData() {
    return this.bluetoothData;
  }

  private List<Double> getRssiList() {
    return this.rssiList;
  }

  private void setRssiList() {
    this.rssiList = new ArrayList<>();
  }

  private PermissionHandler getPermissionHandler() {
    return this.permissionHandler;
  }

  private Config getConfig() {
    return this.config;
  }

  private int getMeasurementPeriod() {
    return this.measurementPeriod;
  }

  private ProgressDialog getProgressDialog() {
    return this.progressDialog;
  }

  private TextView getStatus() {
    return this.status;
  }

  private Button getFindBeaconButton() {
    return this.findBeacon;
  }

  private boolean isBeaconFound() {
    return this.beaconFound;
  }

  private void setBeaconFound(boolean beaconFound) {
    this.beaconFound = beaconFound;
  }

}
