# Firmware

Open `sketch/sketch.ino` with Arduino IDE and select the board used by the prototype
(Arduino Leonardo). Required libraries are `Ethernet`, `Adafruit ADS1X15` and its
dependencies, plus the board's `Wire` library. Exact historical library versions
and a compiled firmware image are not available in this snapshot. Compilation
and operation with the physical prototype have not been repeated for this export.

Configure IP, MAC and TCP port for the instrument network before upload. The
addresses in the source are prototype configuration examples. The Python GUI
must use the same IP and port. Experimental phase sketches are in `archive/firmware`.

| Command | Behavior in this source |
| --- | --- |
| `#ACQUIRE*` | Capture 128 points on channel 0, then 1, then 2; reply `OK*` |
| `#GETADC n*` | Return stored channel values as space-separated decimal text |
| `#GETGAIN n*` | Return the configured ADC gain code |
| `#GETSHIFT code*` | Return phase displacement estimate from digital edge times |
| `#IDN?*` | Recognized, but response is commented out in this sketch |

The ADS1015 nominal rate is configured at 3300 SPS with I2C at 400 kHz and
`GAIN_TWOTHIRDS`. Channels are acquired in consecutive blocks, not simultaneously.
The ADC is command-triggered and not synchronized to zero crossings. Timestamps,
effective cadence and inter-block gaps are not recorded in the waveform dataset.
GUI gain labels are static and do not certify measured analog gains.

Channel 0 applies `(raw * 2) - 512` before conversion with `computeVolts`; the
other channels do not. The Python display uses `Vpp / 100` for a current-related
readout; calibration supporting this conversion is not established. Digital phase
conversion assumes 50 Hz and has not been quantitatively revalidated here.
