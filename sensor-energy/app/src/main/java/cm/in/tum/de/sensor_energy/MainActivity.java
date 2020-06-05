package cm.in.tum.de.sensor_energy;

import android.net.wifi.WifiManager;

import android.util.Log;

import java.text.SimpleDateFormat;

import java.util.List;
import java.util.Date;

import android.Manifest;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.PermissionChecker;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import android.content.IntentFilter;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

import android.location.Location;
import android.location.LocationManager;
import android.location.LocationListener;

import android.os.Handler;
import android.telephony.CellInfo;
import android.telephony.CellInfoCdma;
import android.telephony.CellInfoGsm;
import android.telephony.CellInfoLte;
import android.telephony.CellInfoWcdma;
import android.telephony.TelephonyManager;
import android.telephony.CellLocation;
import android.telephony.PhoneStateListener;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = MainActivity.class.getSimpleName();

    private enum Measurement {
        Idle,
        Sensor_Accelerometer,
        Sensor_Barometer,
        Sensor_Magnetometer,
        Sensor_Light,
        Sensor_Temperature, // not available
        Sensor_Humidity, // not available
        Bluetooth,
        BLE,
        Wifi,
        GSM,
        Location_GPS,
        Location_Network
    }

    private int numReading = 0;
    private static final int S_to_MS = 1000;
    private static final int S_to_US = 1000000;
    private static final int SAMPLING_RATE_S = 10;
    private static final Measurement MEASUREMENT = Measurement.Sensor_Light;

    private WifiManager wifiManager;
    private BluetoothAdapter bluetoothAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Log.d(TAG, "Measurement: " + MEASUREMENT);
        if (MEASUREMENT == Measurement.Sensor_Accelerometer ||
                MEASUREMENT == Measurement.Sensor_Barometer ||
                MEASUREMENT == Measurement.Sensor_Magnetometer ||
                MEASUREMENT == Measurement.Sensor_Temperature ||
                MEASUREMENT == Measurement.Sensor_Humidity ||
                MEASUREMENT == Measurement.Sensor_Light) {
            int sensorType = Sensor.TYPE_ACCELEROMETER;
            switch (MEASUREMENT) {
                case Sensor_Accelerometer:
                    sensorType = Sensor.TYPE_ACCELEROMETER;
                    break;
                case Sensor_Barometer:
                    sensorType = Sensor.TYPE_PRESSURE;
                    break;
                case Sensor_Magnetometer:
                    sensorType = Sensor.TYPE_MAGNETIC_FIELD;
                    break;
                case Sensor_Temperature:
                    sensorType = Sensor.TYPE_AMBIENT_TEMPERATURE;
                    break;
                case Sensor_Light:
                    sensorType = Sensor.TYPE_LIGHT;
                    break;
                case Sensor_Humidity:
                    sensorType = Sensor.TYPE_RELATIVE_HUMIDITY;
                    break;
            }
            SensorManager sensorManager = (SensorManager) getApplicationContext().getSystemService(Context.SENSOR_SERVICE);
            Sensor sensor = sensorManager.getDefaultSensor(sensorType);
            sensorManager.registerListener(buildSensorListener(), sensor, SAMPLING_RATE_S * S_to_US);
        }
        if (MEASUREMENT == Measurement.BLE) {
            BluetoothManager bluetoothManager = (BluetoothManager) getApplicationContext().getSystemService(Context.BLUETOOTH_SERVICE);
            BluetoothAdapter bluetoothAdapter = bluetoothManager.getAdapter();
            BluetoothLeScanner bluetoothLeScanner = bluetoothAdapter.getBluetoothLeScanner();
            /*ScanSettings aggressiveScanSettings = new ScanSettings.Builder()
                    .setReportDelay(0)
                    .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                    .build();
            bluetoothLeScanner.startScan(null, aggressiveScanSettings, bluetoothLeCallback);*/
            bluetoothLeScanner.startScan(buildBluetoothLeCallback());
        }
        if (MEASUREMENT == Measurement.Bluetooth) {
            BluetoothManager bluetoothManager = (BluetoothManager) getApplicationContext().getSystemService(Context.BLUETOOTH_SERVICE);
            bluetoothAdapter = bluetoothManager.getAdapter();
            IntentFilter filter = new IntentFilter();
            filter.addAction(BluetoothDevice.ACTION_FOUND);
            filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED);
            filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_STARTED);
            getApplicationContext().registerReceiver(buildBluetoothCallback(), filter);
            bluetoothAdapter.startDiscovery();
        }
        if (MEASUREMENT == Measurement.Wifi) {
            wifiManager = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
            getApplicationContext().registerReceiver(buildWifiCallback(), new IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION));
            wifiManager.startScan();
        }
        if (MEASUREMENT == Measurement.Location_GPS ||
                MEASUREMENT == Measurement.Location_Network) {
            int permission = PermissionChecker.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION);
            if (permission == PermissionChecker.PERMISSION_GRANTED) {
                float minDistance = 0;
                long minTime = SAMPLING_RATE_S * S_to_MS;
                String locationProvider = LocationManager.NETWORK_PROVIDER;
                if (MEASUREMENT == Measurement.Location_GPS) {
                    locationProvider = LocationManager.GPS_PROVIDER;
                }
                LocationManager locationManager = (LocationManager) getApplicationContext().getSystemService(LOCATION_SERVICE);
                locationManager.requestLocationUpdates(locationProvider, minTime, minDistance, buildLocationListener());
            }
        }
        if (MEASUREMENT == Measurement.GSM) {
            final TelephonyManager telephonyManager = (TelephonyManager) getApplicationContext().getSystemService(Context.TELEPHONY_SERVICE);
            getCellInfo(telephonyManager);
            final Handler handler = new Handler();
            handler.postDelayed(new Runnable(){
                public void run(){
                    getCellInfo(telephonyManager);
                    handler.postDelayed(this, SAMPLING_RATE_S * S_to_MS);
                }
            }, SAMPLING_RATE_S * S_to_MS);
            //PhoneStateListener phoneStateListener = buildPhoneStateListener();
            //telephonyManager.listen(phoneStateListener, PhoneStateListener.LISTEN_CELL_LOCATION);
            //telephonyManager.listen(phoneStateListener, PhoneStateListener.LISTEN_CELL_INFO);
        }
    }

    // https://github.com/awareframework/com.awareframework.android.sensor.telephony/blob/master/library/src/main/java/com/awareframework/android/sensor/telephony/TelephonySensor.kt
    private void getCellInfo(TelephonyManager telephonyManager) {
        int phoneTypeInt = telephonyManager.getPhoneType();
        String phoneType = null;
        if (phoneTypeInt == TelephonyManager.PHONE_TYPE_GSM) {
            phoneType = "gsm";
        } else if (phoneTypeInt == TelephonyManager.PHONE_TYPE_CDMA) {
            phoneType = "cdma";
        }
        int permission = PermissionChecker.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION);
        if (permission == PermissionChecker.PERMISSION_GRANTED) {
            /* outdated
            List<NeighboringCellInfo> neighCells = telephonyManager.getNeighboringCellInfo();
            for (int i = 0; i < neighCells.size(); i++) {
                NeighboringCellInfo thisCell = neighCells.get(i);
                thisCell.getCid();
                thisCell.getLac();
                thisCell.getRssi();
            } */
            List<CellInfo> infos = telephonyManager.getAllCellInfo();
            for (int i = 0; i < infos.size(); ++i) {
                CellInfo info = infos.get(i);
                if (info instanceof CellInfoGsm) {
                    CellInfoGsm cellinfo = (CellInfoGsm) info;
                } else if (info instanceof CellInfoCdma) {
                    CellInfoCdma cellInfo = (CellInfoCdma) info;
                } else if (info instanceof CellInfoWcdma) {
                    CellInfoWcdma cellInfo = (CellInfoWcdma) info;
                } else if (info instanceof CellInfoLte) {
                    CellInfoLte cellInfo = (CellInfoLte) info;
                }
            }
        }
        printOutput();
    }

    private PhoneStateListener buildPhoneStateListener() {
        return new PhoneStateListener() {
            @Override
            public void onCellInfoChanged(List<CellInfo> cellInfo) {
                printOutput();
            }

            @Override
            public void onCellLocationChanged(CellLocation location) {
                printOutput();
            }
        };
    }

    private ScanCallback buildBluetoothLeCallback() {
        return new ScanCallback() {
            @Override
            public void onScanResult(final int callbackType, final ScanResult result) {
                printOutput();
            }

            @Override
            public void onBatchScanResults(final List<ScanResult> results) {
            }

            @Override
            public void onScanFailed(int errorCode) {
            }
        };
    }

    private BroadcastReceiver buildBluetoothCallback() {
        return new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String action = intent.getAction();
                if (action.equals(BluetoothAdapter.ACTION_DISCOVERY_STARTED)) {
                    printOutput();
                }
                /*if (action.equals(BluetoothDevice.ACTION_FOUND)) {
                    Log.d(TAG, "bluetooth found");
                }*/
                // Bluetooth discovery needs restart
                if (action.equals(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)) {
                    bluetoothAdapter.startDiscovery();
                }
            }
        };
    }

    private BroadcastReceiver buildWifiCallback() {
        return new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                printOutput();
                // Wifi scan needs restart
                wifiManager.startScan();
            }
        };
    }

    private LocationListener buildLocationListener() {
        return new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                printOutput();
            }

            @Override
            public void onStatusChanged(String s, int i, Bundle bundle) {
            }

            @Override
            public void onProviderEnabled(String s) {
            }

            @Override
            public void onProviderDisabled(String s) {
            }
        };
    }

    private SensorEventListener buildSensorListener() {
        return new SensorEventListener() {
            @Override
            public void onSensorChanged(SensorEvent sensorEvent) {
                printOutput();
            }

            @Override
            public void onAccuracyChanged(Sensor sensor, int i) {
            }
        };
    }

    private void printOutput() {
        numReading++;
        Log.d(TAG, "Time: " + getCurrentTime() + " Reading: " + numReading);
    }

    private String getCurrentTime() {
        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss.SSS");
        return sdf.format(new Date());
    }

}
