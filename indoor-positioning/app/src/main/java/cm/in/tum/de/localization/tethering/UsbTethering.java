package cm.in.tum.de.localization.tethering;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.FileReader;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;

import cm.in.tum.de.localization.MainActivity;

public class UsbTethering {

  private static final String TAG = UsbTethering.class.getSimpleName();

  private static final String IP_USB_RANGE = "192.168.42.";
  private static final String USB_TETHERING_INTERFACE = "rndis";
  private static final String ACTION_TETHER_STATE_CHANGED = "android.net.conn.TETHER_STATE_CHANGED";

  private final Context applicationContext;
  private final ITetheringCallback callback;

  public UsbTethering(Context applicationContext, ITetheringCallback callback) {
    this.applicationContext = applicationContext;
    this.callback = callback;
  }

  public void start() {
    if (!isUsbTetheringActive()) {
      Log.d(TAG, "usb tethering is not active");
      IntentFilter filter = new IntentFilter(ACTION_TETHER_STATE_CHANGED);
      getApplicationContext().registerReceiver(new TetherChange(), filter);
      Intent intent = new Intent();
      intent.setClassName("com.android.settings",
              "com.android.settings.TetherSettings");
      getApplicationContext().startActivity(intent);
      Toast.makeText(getApplicationContext(),
              "Please enable USB tethering",
              Toast.LENGTH_SHORT).show();
    } else {
      Log.d(TAG, "usb tethering is active");
      getCallback().onUsbTethering(getUsbThetheredIP());
    }
  }

  private boolean isUsbTetheringActive() {
    try {
      boolean usbIfaceFound = false;
      Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
      while (!usbIfaceFound && interfaces.hasMoreElements()) {
        NetworkInterface iface = interfaces.nextElement();
        if (iface.getName().contains(USB_TETHERING_INTERFACE)) {
          return true;
        }
      }
    } catch (SocketException e) {
      Log.d(TAG, "USB tethering active", e);
    }
    return false;
  }

  private String getUsbThetheredIP() {
    try {
      String line;
      BufferedReader bufferedReader = new BufferedReader(new FileReader("/proc/net/arp"));
      while ((line = bufferedReader.readLine()) != null) {
        String[] splitted = line.split(" +");
        if (splitted != null && splitted.length >= 4) {
          String ip = splitted[0];
          String mac = splitted[3];
          if (!mac.matches("00:00:00:00:00:00")
                  && ip.startsWith(IP_USB_RANGE)) {
            return ip;
          }
        }
      }
    } catch (Exception e) {
      Log.e(TAG, "IP of USB", e);
    }
    return null;
  }

  public class TetherChange extends BroadcastReceiver {

    private static final int SLEEP_TIME = 250; // ms

    @Override
    public void onReceive(final Context context, Intent intent) {
      if (isUsbTetheringActive()) {
        String serverIp = null;
        while (serverIp == null) {
          serverIp = getUsbThetheredIP();
          try {
            Thread.sleep(SLEEP_TIME);
          } catch (InterruptedException e) {}
        }
        // Show main activity
        Intent mainIntent = new Intent(context, MainActivity.class);
        mainIntent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
        getApplicationContext().startActivity(mainIntent);
        getCallback().onUsbTethering(serverIp);
      }
    }
  }

  private ITetheringCallback getCallback() {
    return this.callback;
  }

  private Context getApplicationContext() {
    return this.applicationContext;
  }

}
