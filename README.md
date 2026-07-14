# 🚀 Smart Traffic Monitoring and Statistics System

A professional, real-time Computer Vision application designed for intelligent transportation systems (ITS). Utilizing **YOLOv8** for high-accuracy object detection and advanced multi-object tracking algorithms, this system monitors traffic flow, tracks vehicle trajectories, counts lane crossings, and dynamically triggers congestion alerts via a modern graphical user interface (GUI).

---

## 🎥 Demo / Results

Below is the real-time performance of the intelligent traffic monitoring system operating on the test video feed:

<img width="588" height="305" alt="Screenshot (227)" src="https://github.com/user-attachments/assets/411700c0-7c69-4c72-9e0b-90f107dc24fd" />


*Figure 1: The system GUI displaying multi-class vehicle detection, dynamic trajectory tracking IDs, virtual line-crossing count indicators, live statistical charts, and automated traffic jam warnings ("CANH BAO: UN TAC").*

---

## ✨ Key Features

- **Multi-Class Vehicle Detection:** High-fidelity, real-time recognition of various transportation classes including Cars, Motorbikes, Buses, and Trucks powered by a customized **YOLOv8** model.
- **Deep Object Tracking:** Robust multi-object tracking that maintains continuous, unique identity (ID) assignments for individual vehicles across sequential video frames.
- **Automated Traffic Counting:** Dynamically registers and updates vehicle counts as they cross predefined virtual tracking zones or check-lines (Directional Flow Analysis).
- **Intelligent Congestion Alerts:** Real-time density assessment that automatically flags traffic delays or gridlocks based on the active vehicle count within designated regions.
- **Interactive Analytics Dashboard:** A highly intuitive **CustomTkinter** dark-mode user interface integrating live data logs, statistical summaries, and dynamic graphical charts (**Matplotlib**).
- **Data Export Capability:** Seamless one-click extraction of historical traffic logs directly into structured Excel report formats (`.xlsx`) for downstream analysis.

---

## 🛠️ Tech Stack & Environment

- **Core Language:** Python 3.10+
- **Deep Learning Framework:** PyTorch, YOLOv8 (by Ultralytics)
- **Computer Vision Pipeline:** OpenCV (cv2)
- **Data Visualization:** Matplotlib (integrated with Tkinter backend via FigureCanvasTkAgg)
- **User Interface:** CustomTkinter (Modern Dark/Blue Theme)
- **Data Handling & Reports:** Pandas / OpenPyXL (Excel Exporting Engine)

---

## 📂 Project Structure

```text
├── .gitignore               # Automated Git tracking exclusions
├── README.md                # Comprehensive system documentation
├── Bao_cao_Giao_thong.xlsx   # Sample generated traffic data report
├── best.pt                  # Optimized YOLOv8 custom weights
├── config_vach.json          # Configuration file for virtual counting lines
├── main_gui.py               # Main application entry point & GUI layout
