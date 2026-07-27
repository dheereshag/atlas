# Hardware Module Specifications & System Interconnection Guide

Quick reference guide for mechanical dimensions, system power architecture, pin mappings, screw hole specifications, status indicators, and enclosure mounting requirements for the 3-module system.

---

## 1. LM2596 DC-DC Buck Converter Step Down Module

| Dimension / Property | Value | Notes |
| :--- | :--- | :--- |
| **Length** | `45.0 mm` | PCB length |
| **Width** | `20.0 mm` | PCB width |
| **Height** | `14.0 mm` | Top of potentiometer / electrolytic capacitors |
| **Weight** | `~11 g` | Approximate module weight |
| **Mounting Holes** | `2x M3` | 3.0 mm diameter clearance mounting holes |
| **Mounting Hole Layout** | Diagonal (Flipped) | Pitch: `36.0 mm (X) x 20.0 mm (Y)` center-to-center |
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
| **Height** | `16.0 mm` | Top of DB9 connector |
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
| **Length** | `50.0 mm` | Updated board length |
| **Width** | `28.0 mm` | Updated module width |
| **Height** | `14.0 mm` | Includes PCB, socket, and component height |
| **Pin Pitch** | `2.54 mm` | Standard 0.1 inch header spacing |
| **Row Spacing** | `25.4 mm` | 1.0 inch / 1000 mil row-to-row spacing |
| **Mounting Holes** | `4x M3` | 3.0 mm diameter corner mounting holes |
| **Mounting Hole Layout** | 4 Corners | Pitch: `23.0 mm (X) x 45.0 mm (Y)` center-to-center |
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

## 6. Enclosure Design Parameters, Status LEDs & Clearance Specs

* **Enclosure Inner Volume Target**: $\ge 116\text{ mm (L)} \times 86\text{ mm (W)} \times 26\text{ mm (H)}$ (Outer dimensions: $120.0\text{ mm} \times 90.0\text{ mm} \times 28.0\text{ mm}$)
* **Wall Thickness**: $2.0\text{ mm}$ minimum (standard FDM print strength)
* **Tolerances / Play**: $+0.5\text{ mm}$ clearance on module mounting slots and cutouts.
* **Modern Case Aesthetics & Materials (Black & White Two-Tone)**:
  - **Main Base (`Mat_Filament_Black`)**: Sleek Matte Black 3D printing filament finish (`(0.03, 0.03, 0.03)`) with $2.5\text{ mm}$ chamfered outer edges, tactical $8.0\text{ mm}$ corner chamfer facets, and side accent channels.
  - **Top Lid Body (`Mat_Filament_Black`)**: Sleek Matte Black 3D printing filament finish (`(0.03, 0.03, 0.03)`) for the main top lid recessed panel, debossed sci-fi lines, and hexagonal thermal ventilation grid.
  - **Top Lid Outer Boundary Frame (`Mat_Filament_White`)**: Pure Clean White 3D printing filament finish (`(0.90, 0.90, 0.90)`) forming a 4.0 mm accent border rim around the top lid outer perimeter.
  - **GLUVOK Corporate Branding (`Mat_Filament_White`)**: Pure Clean White 3D debossed `"G L U V O K"` lettering inlaid flush into the Matte Black top lid surface at `X = 0.0 mm, Y = +26.0 mm`.
  - **Clearance Mockup PCBs (`Mat_Filament_Black`)**: High-contrast Matte Black PCB mockups for LM2596, MAX3232, and ESP32 DevKit boards.
  - **Default Colored Viewport in Blender**: Viewport shading configured to `MATERIAL` preview and material `diffuse_color` mapped so the high-contrast Black and White model displays by default when opened in Blender.
  - **GLUVOK Corporate Branding**:
    1. **Primary Top Logo Engraving**: $0.8\text{ mm}$ deep 3D-printed debossed/engraved `"G L U V O K"` lettering carved directly into the top lid surface centered at `X = 0.0 mm, Y = +26.0 mm`.
  - **Base Feet**: 4x non-slip rubber base pads ($4.5\text{ mm}$ radius) under bottom corners.
* **Dual Display & Status Indicators (Top Lid Front Panel)**:
  1. **7-Segment Display (`Numeric / Status Display`)**: Standard 0.56" 1-Digit 7-segment LED module ($13.0\text{ mm} \times 19.5\text{ mm}$ rectangular cutout), mounted at `X = -10.0 mm, Y = -22.0 mm`.
  2. **RGB LED (`System Status / Power / Link`)**: $5.0\text{ mm}$ dome ($5.2\text{ mm}$ cutout), mounted at `X = +12.0 mm, Y = -22.0 mm` with metallic bezel ring.
  - **Indicator Panel**: Recessed black bezel strip ($42.0\text{ mm} \times 24.5\text{ mm}$) framing the 7-segment display and RGB LED cutouts.
* **Non-Overlapping Internal Layout Zones**:
  1. **MAX3232 Module (Front Left)**: Centered at `X = -26.0 mm, Y = -22.0 mm`. Bounding box: `[-42.0 to -10.0 mm, -38.5 to -5.5 mm]`.
  2. **LM2596 Converter (Back Left)**: Centered at `X = -25.0 mm, Y = +22.0 mm`. Bounding box: `[-47.5 to -2.5 mm, +12.0 to +32.0 mm]`.
  3. **ESP32 DevKit Board (Front Right)**: Centered at `X = +28.0 mm, Y = -18.0 mm`. Front edge flush with front inner wall (`Y = -43.0 mm`). Bounding box: `[+14.0 to +42.0 mm, -43.0 to +7.0 mm]`.
* **External Cutouts Required**:
  1. **DB9 Female Connector Cutout**: $31.5\text{ mm} \times 14.0\text{ mm}$ on the front wall (`X = -26.0 mm, Y = -45.0 mm`) for MAX3232 DB9 connector.
  2. **ESP32 Micro-USB Port Cutout**: $10.5\text{ mm} \times 7.5\text{ mm}$ on the **front wall** (`X = +28.0 mm, Y = -45.0 mm`) — USB port is at the short end of the ESP32 board, centered between the two front screw holes.
* **Internal Standoff Posts & Screw Holes**:
  - **Lid Mounting**: 4x M3 corner posts ($4.0\text{ mm}$ radius, $2.8\text{ mm}$ pilot hole diameter) for top lid M3 screws.
  - **LM2596 Buck Converter**: 2x M3 PCB standoff posts ($3.0\text{ mm}$ radius, $4.0\text{ mm}$ height, brass insert collar) at diagonal positions (`(-43.0, +32.0)` & `(-7.0, +12.0)`).
  - **MAX3232 Module**: 4x M3 PCB standoff posts ($3.0\text{ mm}$ radius, $4.0\text{ mm}$ height, brass insert collar) at 4 corner positions.
  - **ESP32 Board**: 4x M3 PCB standoff posts ($3.0\text{ mm}$ radius, $4.0\text{ mm}$ height, brass insert collar) at 4 corner positions.
* **Screw Fastener Summary (Total 14x M3 Screws)**:
  - 4x M3 x 8mm screws for Enclosure Top Lid
  - 2x M3 x 6mm screws for LM2596 module
  - 4x M3 x 6mm screws for MAX3232 module
  - 4x M3 x 6mm screws for ESP32 module

---

## 7. Generated Output Files

1. **`main.blend`**: Complete combined 3D assembly scene (Enclosure Base + Top Lid + PCB Clearance Mockups).
2. **`enclosure_base.blend`**: Isolated 3D model containing only the Enclosure Base component.
3. **`enclosure_top_lid.blend`**: Isolated 3D model containing only the Enclosure Top Lid component.