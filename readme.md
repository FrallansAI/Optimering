# Tournament Scheduler

A web application for optimizing tournament scheduling and judge assignments, especially designed for football (soccer) clubs managing multiple teams.

## Features

- Create and manage tournaments with multiple teams
- Connect trainers with their children on specific teams
- Assign judges to matches based on preferences (e.g., judges with children on teams)
- Optimize judge workload to ensure balanced assignments
- Minimize the time each judge needs to be present at the tournament
- Upload match schedules via CSV or Excel files
- Generate optimized schedules with judge assignments

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git (for cloning the repository)

### Installation

1. Clone this repository to your local machine:

```bash
git clone <your-repository-url>
cd tournament-scheduler
```

2. Build and start the Docker container:

```bash
docker-compose up -d
```

3. Access the application in your web browser at:

```
http://localhost:8000
```

## Usage

### Creating a Tournament

1. On the home page, enter a name for your tournament and click "Create Tournament"
2. You'll be redirected to the tournament management page

### Adding Teams

1. Go to the "Teams" tab
2. Click "Add Team"
3. Enter the team name and trainer name
4. Click "Save"

### Adding Judges

1. Go to the "Judges" tab
2. Click "Add Judge"
3. Enter the judge's name
4. If the judge has a child on one of the teams, select the team from the dropdown
5. Click "Save"

### Adding Players

1. Go to the "Teams" tab
2. Find the team you want to add a player to
3. Click "Add Player" on that team's card
4. Enter the player's name
5. If the player has a parent who is a trainer or judge, enter their name
6. Click "Save"

### Uploading Matches

1. Go to the "Matches" tab
2. Click "Upload Matches"
3. Select your CSV or Excel file containing match information
4. Click "Upload"

#### Match File Format

Your CSV or Excel file should contain columns for:
- Time (in format HH:MM or YYYY-MM-DD HH:MM)
- Home Team
- Away Team
- Location
- Plan Number

### Generating a Schedule

1. Go to the "Schedule" tab
2. Click "Generate Schedule"
3. The system will automatically assign judges to matches according to these priorities:
   - Judges prefer to judge games with their children
   - Even workload distribution among judges
   - Minimizing time at venue for each judge

## System Design

The application consists of:

1. **Core Scheduling Algorithm** (scheduler.py)
   - Classes for Teams, Players, Matches, and Tournament
   - Optimization logic for judge assignments

2. **Web Interface** (FastAPI)
   - Upload match data
   - Manage teams, judges, and players
   - Generate and view schedules

3. **Frontend**
   - Responsive web interface built with Bootstrap
   - JavaScript for dynamic interactions

## Customization

You can modify the scheduling algorithm by editing the `scheduler.py` file. The main optimization logic is in the `assign_judges_optimally` method of the `Tournament` class.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Built with FastAPI, Bootstrap, and Python
- Optimized for football tournaments with multiple teams from the same club
