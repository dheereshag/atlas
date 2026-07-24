# Hardware Module Specifications & System Interconnection Guide

Quick reference guide for mechanical dimensions, system power architecture, pin mappings, screw hole specifications, and enclosure mounting requirements for the 3-module system.

---

## 1. LM2596 DC-DC Buck Converter Step Down Module

| Dimension / Property | Value | Notes |
| :--- | :--- | :--- |
| **Length** | `43.2 mm` | PCB length |
| **Width** | `21.6 mm` | PCB width |
| **Height** | `14.0 mm` | Top of potentiometer / electrolytic capacitors |
| **Weight** | `~11 g` | Approximate module weight |
| **Mounting Holes** | `2x M3` | 3.0 mm diameter clearance mounting holes |
| **Mounting Hole Layout** | Diagonal | Pitch: `36.0 mm (X) x 20.0 mm (Y)` center-to-center |
| **Fastener Spec** | `M3 x 6mm` | M3 machine screws / standoffs |
| **Input Voltage Range** | `7.0V – 35V DC` | Accepts raw DC input from RS232 module power rail |
| **Output Voltage** | `5.0V DC` | Calibrated to 5.0V output to feed ESP32 VIN pin |

---

## 2. MAX3232 DB9 RS232 to TTL Converter Module

| Dimension / Property | Value | Notes |
| :--- | :--- | :--- |
| **PCB Length** | `33.0 mm` | Board length only |
| **Overall Length** | `44.0 mm` | Includes female DB9 metal connector overhang |
| **Width** | `32.0 mm` | Board width |
| **Height** | `15.0 mm` | Top of DB9 connector |
| **Weight** | `~12 g` | Standard board weight |
| **Mounting Holes** | `4x M3` | 3.0 mm diameter corner mounting holes |
| **Mounting Hole Layout** | 4 Corners | Pitch: `27.0 mm (X) x 26.0 mm (Y)` center-to-center |
| **Fastener Spec** | `M3 x 6mm` | M3 machine screws / standoffs |
| **Power Input** | External DC Line | Main system DC power is fed via MAX3232 board rail |
| **Logic Power (VCC)**| `3.3V DC` | Supplied from ESP32 3V3 pin for 3.3V TTL signal levels |

---

## 3. ESP32 DevKit V1 Board

| Dimension / Property | Value | Notes |
| :--- | :--- | :--- |
| **Length** | `51.5 mm` | 30-pin variant (~55.0 mm for 38-pin version) |
| **Width** | `28.5 mm` | Standard module width |
| **Height** | `7.0 mm` | Includes PCB and pre-soldered male header pins |
| **Pin Pitch** | `2.54 mm` | Standard 0.1 inch header spacing |
| **Row Spacing** | `25.4 mm` | 1.0 inch / 1000 mil row-to-row spacing |
| **Mounting Holes** | `4x M3` | 3.0 mm diameter corner mounting holes |
| **Mounting Hole Layout** | 4 Corners | Pitch: `23.5 mm (X) x 46.5 mm (Y)` center-to-center |
| **Fastener Spec** | `M3 x 6mm` | M3 machine screws / standoffs |
| **Power Input (VIN)** | `5.0V DC` | Fed from LM2596 `OUT+` (5.0V) |
| **Logic Voltage** | `3.3V DC` | GPIO operating voltage |

---

## 4. System Wiring Architecture & Interconnections

### Power Distribution Path
1. **Primary DC Power Input**: Fed into the **MAX3232 RS232 Module** power rail / DB9 connector.
2. **Buck Converter Input**: MAX3232 power rail passes raw DC voltage to **LM2596 `IN+` / `IN-`**.
3. **Step-Down Power to ESP32**: LM2596 steps raw DC down to **5.0V DC**:
   - `OUT+` (5.0V) $\rightarrow$ ESP32 **`VIN`**
   - `OUT-` (GND) $\rightarrow$ ESP32 **`GND`**
4. **Logic Power & Common Ground**:
   - ESP32 **`3V3`** $\rightarrow$ MAX3232 **`VCC`** (Powers MAX3232 at 3.3V logic level)
   - ESP32 **`GND`** $\rightarrow$ MAX3232 **`GND`** (Common ground reference)

### Data Path (UART Serial Communication)
- ESP32 **`GPIO17 (TX2)`** $\rightarrow$ MAX3232 **`RXD`**
- ESP32 **`GPIO16 (RX2)`** $\leftarrow$ MAX3232 **`TXD`**

---

## 5. Complete Pin Mapping Matrix

| Source Module | Source Pin | Destination Module | Destination Pin | Wire Color Code | Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **External Source** | `Raw DC (+)` | **MAX3232** | `V+ Input` | Red | Main DC Power Input |
| **External Source** | `Raw DC (-)` | **MAX3232** | `GND Input` | Black | Main DC Ground Input |
| **MAX3232** | `V+ Rail` | **LM2596** | `IN+` | Red | Raw DC to Buck Converter |
| **MAX3232** | `GND Rail` | **LM2596** | `IN-` | Black | Raw Ground to Buck Converter |
| **LM2596** | `OUT+` | **ESP32** | `VIN` | Red | Regulated 5.0V DC System Power |
| **LM2596** | `OUT-` | **ESP32** | `GND` | Black | Common Ground |
| **ESP32** | `3V3` | **MAX3232** | `VCC` | Yellow | 3.3V Logic Power to MAX3232 |
| **ESP32** | `GND` | **MAX3232** | `GND` | Black | Common Ground Reference |
| **ESP32** | `GPIO17 (TX2)`| **MAX3232** | `RXD` | Green | Serial Transmit (ESP32 $\rightarrow$ MAX3232) |
| **ESP32** | `GPIO16 (RX2)`| **MAX3232** | `TXD` | Blue | Serial Receive (MAX3232 $\rightarrow$ ESP32) |

---

## 6. Enclosure Design Parameters & Clearance Specs

* **Enclosure Inner Volume Target**: $\ge 85\text{ mm (L)} \times 65\text{ mm (W)} \times 30\text{ mm (H)}$
* **Wall Thickness**: $2.0\text{ mm}$ minimum (standard FDM print strength)
* **Tolerances / Play**: $+0.5\text{ mm}$ clearance on module mounting slots and cutouts.
* **Non-Overlapping Internal Layout Zones**:
  1. **MAX3232 Module (Front Left)**: Centered at `X = -20.0 mm, Y = -16.0 mm`. Bounding box: `[-36.0 to -4.0 mm, -32.5 to 0.5 mm]`.
  2. **LM2596 Converter (Back Left)**: Centered at `X = -18.0 mm, Y = +18.0 mm`. Bounding box: `[-39.6 to +3.6 mm, +7.2 to +28.8 mm]`.
  3. **ESP32 DevKit Board (Right Side)**: Centered at `X = +24.0 mm, Y = 0.0 mm`. Bounding box: `[+9.75 to +38.25 mm, -25.75 to +25.75 mm]`.
* **External Cutouts Required**:
  1. **DB9 Female Connector Cutout**: $31.0\text{ mm} \times 15.5\text{ mm}$ on the front wall (`X = -20.0 mm, Y = -35.0 mm`) for MAX3232 DB9 connector.
  2. **ESP32 Micro-USB Port Cutout**: $10.0\text{ mm} \times 7.0\text{ mm}$ on the right side wall (`X = +45.0 mm, Y = 0.0 mm`) for USB flashing/debugging access.
  3. **Ventilation / Tuning Access**: Top lid potentiometer access hole centered over LM2596 (`X = -18.0 mm, Y = +18.0 mm`).
* **Internal Standoff Posts & Screw Holes**:
  - **Lid Mounting**: 4x M3 corner posts ($4.0\text{ mm}$ radius, $2.8\text{ mm}$ pilot hole diameter) for top lid M3 screws.
  - **LM2596 Buck Converter**: 2x M3 PCB standoff posts ($3.0\text{ mm}$ radius, $4.0\text{ mm}$ height, $2.8\text{ mm}$ pilot hole) at diagonal positions (`(-36.0, +8.0)` & `(0.0, +28.0)`).
  - **MAX3232 Module**: 4x M3 PCB standoff posts ($3.0\text{ mm}$ radius, $4.0\text{ mm}$ height, $2.8\text{ mm}$ pilot hole) at 4 corner positions (`(-33.5, -29.0)`, `(-6.5, -29.0)`, `(-33.5, -3.0)`, `(-6.5, -3.0)`).
  - **ESP32 Board**: 4x M3 PCB standoff posts ($3.0\text{ mm}$ radius, $4.0\text{ mm}$ height, $2.8\text{ mm}$ pilot hole) at 4 corner positions (`(+12.25, -23.25)`, `(+35.75, -23.25)`, `(+12.25, +23.25)`, `(+35.75, +23.25)`).
* **Screw Fastener Summary (Total 14x M3 Screws)**:
  - 4x M3 x 8mm screws for Enclosure Top Lid
  - 2x M3 x 6mm screws for LM2596 module
  - 4x M3 x 6mm screws for MAX3232 module
  - 4x M3 x 6mm screws for ESP32 module