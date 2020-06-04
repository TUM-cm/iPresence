package cm.in.tum.de.localization.data;

import java.util.List;

public class Measurement {

  private final long startTimestamp;
  private final long stopTimestamp;
  private final List<MeasurementEntry> entries;

  public Measurement(long startTimestamp, long stopTimestamp, List<MeasurementEntry> entries) {
    this.startTimestamp = startTimestamp;
    this.stopTimestamp = stopTimestamp;
    this.entries = entries;
  }

}
