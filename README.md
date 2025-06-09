# Flocking Birds Simulation

A Pygame-based simulation demonstrating flocking behavior (boids) with interactive elements like obstacles, food, reproduction, and a real-time statistics graph.

## Description

This project simulates a swarm of "birds" that exhibit emergent flocking behaviors based on a few simple rules:
*   **Cohesion:** Birds steer towards the average position of nearby flockmates.
*   **Alignment:** Birds steer towards the average heading of nearby flockmates.
*   **Separation:** Birds steer to avoid crowding nearby flockmates.

Beyond basic flocking, the simulation includes:
*   **Obstacle Avoidance:** Birds attempt to steer away from moving obstacles.
*   **Food Seeking:** Birds are attracted to food items.
*   **Reproduction:** Birds can reproduce after consuming a certain amount of food, creating new birds with similar (slightly randomized) behavioral traits.
*   **Statistics Graph:** A dynamic Matplotlib graph displays the average behavioral strengths (cohesion, alignment, separation, avoidance, food attraction) of the bird population over time. This graph can be toggled on/off.

## Features

*   Classic boids algorithm implementation.
*   Dynamic spawning of obstacles and food.
*   Bird reproduction based on food consumption.
*   Real-time UI displaying FPS and current bird count.
*   Interactive Matplotlib graph to visualize average flocking parameters.
*   Configurable simulation parameters via `env.py`.

## Requirements

*   Python 3.x
*   Pygame
*   Matplotlib
*   PyQt5 (as a backend for Matplotlib)

## Setup and Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <your-repository-url>
    cd <repository-folder-name>
    ```
    (If you downloaded a ZIP, extract it and navigate into the `swarm_retro` directory.)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate it:
    *   Windows: `venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    Ensure you have a `requirements.txt` file in the project root with the following content:
    ```text
    pygame
    matplotlib
    PyQt5
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

Navigate to the project's root directory (e.g., `..\pygame_swarm_git\swarm_retro\`) in your terminal and run:

```bash
python main.py
