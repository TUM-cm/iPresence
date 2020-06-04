package cm.in.tum.de.localization.data;

public class MeasurementEntry {

  private final String mac;
  private final int rssi;

  public MeasurementEntry(String mac, int rssi) {
    this.mac = mac;
    this.rssi = rssi;
  }

}
