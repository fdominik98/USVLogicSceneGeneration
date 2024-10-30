
# USVLogicSceneGeneration

A Python 3.10-based project for generating and evaluating Unmanned Surface Vehicle (USV) interaction scenes. This repository includes utilities for risk vector analysis, evolutionary computation, and trajectory planning, with detailed visualization and evaluation tools.

This project serves as supplementary material for our research paper **Automated Scene Generation for Testing COLREGS-Compliance of Autonomous Surface Vehicles**

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Requirements](#requirements)
- [Usage](#usage)

## Getting Started

These instructions will help you set up and run the project on your local machine for development and testing purposes.

## Project Structure

The following tree provides an overview of the project structure:

```
USVLogicSceneGeneration
├── .vscode                # Editor configuration for VSCode
├── assets                 # Stores image assets used in visualizations, generated scene and trajectory descriptions are saved here.
├── refinery_functional_models  # Functional model definitions in Refinery's domain specific language: https://refinery.services/
├── requirements.txt       # Python dependencies required for the project
└── src                    # Source code directory
```

### Detailed Description

#### `.vscode`
- `launch.json`: Configures debug settings and launch shortcuts for VSCode.
- `settings.json`: Includes project-specific settings for VSCode.

#### `assets`
- Contains images and plot exports used in the project. Also generated scene and trajectory descriptions are saved here.
  - `images/distr.png`: Distribution plot image from https://doi.org/10.1016/j.oceaneng.2023.116436.
  - `images/gradient.png`: Gradient scale from https://doi.org/10.1016/j.oceaneng.2023.116436. Used to map values to colors and extract distribution from plot.
  - `gen_data/`: **All the evaluation data generated to showcase the results of scene generation.**
  - `figures/`: **All the figures used to showcase the results of scene generation.**

#### `refinery_functional_models`
- Contains `COLREGS.problem` files with functional COLREGS scenario specifications in Refinery DSL:  https://refinery.services/.

#### `requirements.txt`
- Lists the Python packages required for this project. 

#### `src`
- Primary source code for USV scene generation, evaluation, and visualization.
  - `evaluation/`: Modules related to risk and performance evaluation.
    - `eqv_class_calculator.py`: Calculates equivalence classes for risk.
    - `risk_evaluation.py`: Evaluates risk vectors for OS based on a concrete scene.
    - `mann_whitney_u_cliff_delta.py`: Evaluates p-values and effect size for floating point samples.
    - `fishers_exact_odds_ratio`: Evaluates p-values and effect size for dichotomous samples.

  - `evolutionary_computation/`: Algorithms for optimization and evolutionary computation.
    - `evolutionary_algorithms/`: Implements different optimization algorithms such as NSGAII, NSGAIII, Genetic Algorithm, Swarm Optimization, Differential Evolution.
  - `aggregates.py`: Implements aggregate strategies for calculating fitness functions (Category, Vessel, Global aggregates).
  - `evaluation_data.py`: A data model class for storing and loading evaluation results. These files are used to visualize concretization performance and COLREGS scenarios.
  - `model/`: Defines USV models, relations, and interaction environment.
    - `data_parser.py`: Parses evaluation data models.
    - `environment/`: Environmental and interaction modeling.
    - `environment/functional_models`: Functional model generation for MSR and SBO.
    - `relation_types.py`: Defines relationship types between vessels.
    - `vessel.py`: Data model for representing a vessel.
    - `instance_initializer.py`: Initializes a population of random or deterministic individuals for evolutionary algorithms.
    - `relation_types.py`: Defines relationship types between vessels.

  - `proof_of_concept/`: Code that is not directly used for project purposes.

  - `trajectory_planning/`: Implements trajectory generation and interpolation for USV scenarios.
    - `bidirectional_rrt_star_fnd.py`: Path finding algorithm for trajectory planning.

  - `visualization/`: Utilities for generating visualizations and animations.
    - `algo_evaluation/`: Evaluation plots for algorithm performance visualization.
    - `colreg_scenarios/`: Visualizations of concrete scenes/scenarios.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/USVLogicSceneGeneration.git
cd USVLogicSceneGeneration
```

### 2. Set Up a Virtual Environment

For isolated project dependencies, it's recommended to use a virtual environment.

```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Requirements

Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Instructions on how to run the main scripts, such as evaluation and visualization tools. You can run these scripts directly in your terminal or use the provided configurations in Visual Studio Code for debugging.

### Running from the Terminal

You can execute any of the following Python scripts from the terminal:

```bash
# Generates trajectories by loading an evaluation data file
python src/trajectory_generator.py

# Loads trajectories that are generated with trajectory_generator.py
python src/trajectory_viewer.py

# Runs single adhoc tests of scene generation 
python src/test_algorithm.py

# Runs hyper-parameter tuning for evolutionary algorithms
python src/hyperparam_test.py

# This is the file with which the evaluation is run for each batch. 
python src/evaluation_main.py

# Loads folders containing evaluation data and visualizes them in a Dash table on local server. Good for debuging and browsing the data.
python src/table_browser.py

# Runs the evaluation visualization script where all the plots are generated for the evaluation data used in the research.
python src/eval_vis.py

# Script for postprocessing evaluation result files for example annotating them with risk vectors.
python src/annotate_risk_vectors.py

# Executes the RRT* path finding algorithm (not used, only proof of concept)
python src/trajectory_planning/RRTStarFN.py

# Executes the bidirectional RRT* algorithm (not used, only proof of concept)
python src/trajectory_planning/bidirectionalRRTStarFND.py

# Extracts the evaluation results from the images images/distr.png and images/gradient.png scraped from https://doi.org/10.1016/j.oceaneng.2023.116436. Used to map values to colors and extract distribution from plot.
python src/wang24_eval.py
