# 🚦 Real-time Traffic Monitoring and Statistics System

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00ffff)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=flat&logo=opencv&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📌 Introduction
This project implements an end-to-end **Real-time Traffic Monitoring and Statistics System** using Computer Vision and Deep Learning. Powered by **YOLOv8** and object tracking algorithms, the system detects, classifies, and tracks motor vehicles (cars, motorbikes, buses, trucks) in real-time video streams to assess traffic density and counting statistics.

## 🎥 Demo & Visuals


<img width="95" height="103" alt="car_6_231118" src="https://github.com/user-attachments/assets/233435bd-3474-4c81-b04c-6b7e36d54c10" />


## ✨ Key Features
* **Multi-Class Vehicle Detection:** Accurate real-time recognition of cars, motorbikes, buses, and trucks using YOLOv8.
* **Deep Object Tracking:** Maintains continuous trajectory tracking for individual vehicles across consecutive frames.
* **Automated Traffic Counting:** Dynamically counts vehicles crossing predefined virtual check-lines or zones.
* **Flow & Density Assessment:** Provides real-time traffic statistics to aid in smart city routing and congestion analysis.

## 🛠️ Tech Stack & Environment
* **Language:** Python 3.10+
* **Deep Learning Framework:** PyTorch, YOLOv8 (by Ultralytics)
* **Computer Vision & Math:** OpenCV, NumPy
* **Package Management:** `pip` / `uv`

## 📂 Project Structure
```text
A-TRAFFIC-MONITORING-AND-STATISTICS-SYSTEM-/
│
├── snapshots/               # Sample output images and detection frames
├── yolov8n.pt               # YOLOv8 pre-trained model weights
├── main.py                  # Main execution script for traffic tracking
├── requirements.txt         # Project dependencies and libraries
├── .gitignore               # Ignored files (videos, cache, virtual envs)
└── README.md                # Project documentation
